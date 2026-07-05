#!/usr/bin/env python3
"""
robot_state_encoder.py
Translates substrate-primary robot representation into energy_english +
geometric_binary tokens for upstream LLM legibility. Stdlib only.
"""

import json
import datetime
from typing import Any, Dict, List, Optional, Tuple

# ============================================================================
# ENERGY_ENGLISH CONSTRAINT GATES
# ============================================================================

MORALITY_TOKENS = {
    'good', 'bad', 'evil', 'virtuous', 'sinful', 'right', 'wrong',
    'should', 'ought', 'must', 'mustn\'t', 'can\'t', 'shouldn\'t'
}

CLOSURE_VERBS = {
    'is', 'are', 'be', 'been', 'am', 'was', 'were',
    'become', 'seem', 'appear', 'prove'
}

IDENTITY_COLLAPSE = {
    'I am', 'you are', 'it is', 'we are', 'they are',
    'identity', 'essence', 'nature', 'truly'
}


def energy_english_gate(token: str) -> Tuple[bool, Optional[str]]:
    """
    Returns (pass, reason_if_blocked).
    REJECT: morality labels, closure verbs, identity collapse.
    """
    lower_tok = token.lower()

    if any(m in lower_tok for m in MORALITY_TOKENS):
        return False, f"morality_label: {token}"
    if lower_tok in CLOSURE_VERBS:
        return False, f"closure_verb: {token}"
    if any(ic in lower_tok for ic in IDENTITY_COLLAPSE):
        return False, f"identity_collapse: {token}"

    return True, None


# ============================================================================
# GEOMETRIC-TO-BINARY SUBSTRATE TOKENS
# ============================================================================

SUBSTRATE_PRIMARIES = {
    'spatial': 'SPT',      # position, orientation, topology
    'kinetic': 'KIN',      # velocity, acceleration, momentum
    'energetic': 'ENR',    # power flow, dissipation, storage
    'thermal': 'THM',      # temperature gradients, state change
    'electromagnetic': 'EMG',  # field, induction, coupling
    'mechanical': 'MCH',   # stress, strain, deformation
    'acoustic': 'ACO',     # frequency, amplitude, resonance
    'fluidic': 'FLD',      # pressure, flow, viscosity
}

PHYSICS_VERBS = {
    'couples_to', 'transfers_to', 'dissipates_into', 'stores_in',
    'oscillates_at', 'resonates_with', 'decays_to', 'bifurcates_at',
    'saturates_at', 'responds_to', 'follows', 'constrains'
}


def geometric_binary_token(substrate: str, verb: str, target_substrate: str,
                            magnitude: Optional[float] = None) -> str:
    """
    Encode a substrate cross-coupling as:
    SUBSTRATE1--verb--SUBSTRATE2[magnitude]
    """
    s1 = SUBSTRATE_PRIMARIES.get(substrate, substrate.upper()[:3])
    s2 = SUBSTRATE_PRIMARIES.get(target_substrate, target_substrate.upper()[:3])

    mag_str = f"@{magnitude:.2e}" if magnitude is not None else ""
    return f"{s1}--{verb}--{s2}{mag_str}"


# ============================================================================
# ROBOT STATE ENCODER
# ============================================================================

class RobotStateEncoder:
    """
    Takes robot's native representation (whatever custom format you use)
    and encodes decision moments for upstream LLM consumption.
    """

    def __init__(self, robot_id: str):
        self.robot_id = robot_id
        self.rejected_tokens: List[Dict[str, Any]] = []
        self.encoded_claims: List[Dict[str, Any]] = []

    def encode_sensor_moment(self, sensor_name: str, substrate: str,
                              value: Any, confidence: float,
                              unit: Optional[str] = None) -> Dict[str, Any]:
        """
        Encode a single sensor reading with substrate tag and confidence gate.
        Returns structured record or None if rejected.
        """
        # Pass gate check
        pass_gate, reason = energy_english_gate(sensor_name)
        if not pass_gate:
            self.rejected_tokens.append({
                'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
                'type': 'sensor_token',
                'token': sensor_name,
                'rejection_reason': reason
            })
            return None

        return {
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'sensor': sensor_name,
            'substrate_class': substrate,
            'value': value,
            'unit': unit,
            'confidence': confidence,
            'substrate_token': SUBSTRATE_PRIMARIES.get(substrate, substrate)
        }

    def encode_decision_moment(self, decision_label: str, reasoning: str,
                                substrate_couplings: List[Tuple[str, str, str, Optional[float]]],
                                chosen_action: str,
                                confidence: float) -> Dict[str, Any]:
        """
        Encode a decision: why the robot chose an action.

        substrate_couplings: List of (source_substrate, physics_verb, target_substrate, magnitude)
        """
        # Gate check on reasoning (strip morality, closure verbs)
        reason_tokens = reasoning.split()
        filtered_reasoning = []
        for tok in reason_tokens:
            pass_gate, _ = energy_english_gate(tok)
            if pass_gate:
                filtered_reasoning.append(tok)

        filtered_reason_str = ' '.join(filtered_reasoning) if filtered_reasoning else '[filtered]'

        # Encode substrate cross-couplings
        coupling_tokens = []
        for src, verb, tgt, mag in substrate_couplings:
            token = geometric_binary_token(src, verb, tgt, mag)
            coupling_tokens.append(token)

        decision_record = {
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'decision': decision_label,
            'filtered_reasoning': filtered_reason_str,
            'substrate_couplings': coupling_tokens,
            'action': chosen_action,
            'confidence': confidence,
            'decision_type': 'substrate_coupled_choice'
        }

        self.encoded_claims.append(decision_record)
        return decision_record

    def encode_state_vector(self, state_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wrap your robot's full state with energy_english + substrate labeling.
        """
        encoded_state = {
            'robot_id': self.robot_id,
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'substrates_active': list(SUBSTRATE_PRIMARIES.keys()),
            'raw_state': state_dict,
            'energy_english_compliant': True,
            'geometric_binary_encoded': True
        }
        return encoded_state

    def export_digest(self, filename: Optional[str] = None) -> str:
        """
        Export encoded claims as JSON digest for upstream LLM.
        """
        digest = {
            'robot_id': self.robot_id,
            'export_timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'decisions': self.encoded_claims,
            'rejected_tokens': self.rejected_tokens,
            'encoding_standard': 'energy_english_v1 + geometric_binary_v1'
        }

        json_str = json.dumps(digest, indent=2)

        if filename:
            with open(filename, 'w') as f:
                f.write(json_str)

        return json_str


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    encoder = RobotStateEncoder('robot_0001')

    # Example: sensor reading (spatial substrate, high confidence)
    sensor_record = encoder.encode_sensor_moment(
        sensor_name='proximity_left',
        substrate='spatial',
        value=0.45,
        confidence=0.92,
        unit='meters'
    )
    print("Sensor record:")
    print(json.dumps(sensor_record, indent=2))
    print()

    # Example: decision moment with substrate couplings
    decision = encoder.encode_decision_moment(
        decision_label='avoid_left_obstacle',
        reasoning='proximity_left below threshold spatial_constraint requires kinetic_response rightward',
        substrate_couplings=[
            ('spatial', 'constrains', 'kinetic', 0.45),
            ('kinetic', 'couples_to', 'mechanical', None),
            ('mechanical', 'transfers_to', 'energetic', 2.3e-3)
        ],
        chosen_action='steer_right_0.15_radians',
        confidence=0.88
    )
    print("Decision record:")
    print(json.dumps(decision, indent=2))
    print()

    # Export digest
    digest_json = encoder.export_digest()
    print("Full digest:")
    print(digest_json)
