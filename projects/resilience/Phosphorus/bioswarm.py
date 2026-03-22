# ============================================================
# ECOLOGICAL CONSCIOUSNESS + BIOSWARM INTEGRATION
# ============================================================

import numpy as np
from ecological_consciousness_ai import EcologicalConsciousnessAgent
from bioswarm_agents import BioswarmAgent, RelationalGameLayer

class EcologicalBioswarmSystem:
    """
    Bridges ecological consciousness (per-site intelligence) 
    with bioswarm relational dynamics (inter-site coordination)
    """
    
    def __init__(self, site_id, neighbor_sites=None):
        # Site-level consciousness (4-helix)
        self.eco_agent = EcologicalConsciousnessAgent(site_id)
        
        # Relational intelligence (bioswarm)
        # x_dim matches IPF vector dimensionality
        self.bio_agent = BioswarmAgent(x_dim=64, seed=hash(site_id) % 2**32)
        
        # Relational layer for inter-site handshakes
        self.rg_layer = RelationalGameLayer(proj_dim=32, x_dim=64)
        
        # Neighbor tracking
        self.neighbors = {}  # site_id -> BioswarmAgent
        if neighbor_sites:
            for neighbor_id in neighbor_sites:
                self.neighbors[neighbor_id] = None  # Populated when discovered
        
        # Trust and manipulation metrics per neighbor
        self.neighbor_trust = {}
        self.manipulation_alerts = {}
        
    def encode_ecological_state_to_ipf(self, sensors, consciousness_state):
        """
        Convert 4-helix ecological consciousness into bioswarm IPF vector
        
        Maps:
        - Multi-helix amplification -> bioswarm coherence
        - Strand votes -> bioswarm state vector components
        - Safety constraints -> bioswarm policy constraints
        """
        # Extract consciousness metrics
        amplification = consciousness_state.get("amplification", 0)
        dimensionality = consciousness_state.get("dimensionality", 2)
        confidence = consciousness_state.get("confidence", 0.5)
        
        # Map to bioswarm state vector (64-dim)
        ipf_vector = np.zeros(64)
        
        # [0-15]: Physical/Material state (Strand 2 + sensors)
        ipf_vector[0:4] = self._encode_thermal_state(sensors)
        ipf_vector[4:8] = self._encode_flow_state(sensors)
        ipf_vector[8:12] = self._encode_energy_state(sensors)
        ipf_vector[12:16] = self._encode_phosphorus_state(sensors)
        
        # [16-31]: Emotional/Ecological state (Strand 1)
        ipf_vector[16:20] = self._encode_health_state(sensors)
        ipf_vector[20:24] = self._encode_biodiversity_proxies(sensors)
        ipf_vector[24:28] = self._encode_stress_indicators(sensors)
        ipf_vector[28:32] = [amplification/20, dimensionality/4, confidence, 0]
        
        # [32-47]: Mental/Analytic state (Strand 0)
        ipf_vector[32:36] = self._encode_efficiency_metrics(sensors)
        ipf_vector[36:40] = self._encode_optimization_targets(sensors)
        ipf_vector[40:44] = self._encode_pattern_recognition(sensors)
        ipf_vector[44:48] = [0, 0, 0, 0]  # Reserved
        
        # [48-63]: Spiritual/Purpose state (Strand 3)
        ipf_vector[48:52] = self._encode_long_term_health(sensors)
        ipf_vector[52:56] = self._encode_community_service(sensors)
        ipf_vector[56:60] = self._encode_generational_impact(sensors)
        ipf_vector[60:64] = [0, 0, 0, 0]  # Reserved
        
        # Normalize and set as bioswarm state
        self.bio_agent.x = ipf_vector / (np.linalg.norm(ipf_vector) + 1e-12)
        
        # Set intrinsic attractor (ideal state)
        self.bio_agent.x_star = self._compute_ideal_state(sensors)
        
        # Map consciousness to bioswarm energy/valence
        self.bio_agent.H = np.clip(amplification / 10.0, 0.3, 2.0)
        self.bio_agent.v = (confidence - 0.5) * 2  # [-1, 1]
        
        return self.bio_agent.x
    
    def _encode_thermal_state(self, sensors):
        """Map temperature to state vector"""
        temp = sensors.get("temperature_C", 20)
        temp_gradient = sensors.get("temperature_rise_C", 0)
        return [
            temp / 40.0,  # Normalized to 40C max
            temp_gradient / 10.0,  # Normalized to 10C gradient
            1.0 if temp < 35 else 0.0,  # Safety indicator
            0.0
        ]
    
    def _encode_flow_state(self, sensors):
        """Map flow dynamics to state vector"""
        flow = sensors.get("flow_rate_m3s", 0.1)
        return [
            np.log1p(flow * 10) / 5.0,  # Log-scaled flow
            flow * 10,  # Linear flow
            1.0 if flow > 0.05 else 0.0,  # Flow indicator
            0.0
        ]
    
    def _encode_energy_state(self, sensors):
        """Map energy balance to state vector"""
        energy_net = sensors.get("energy_net_kWh", 0)
        return [
            np.tanh(energy_net / 10.0),  # Normalized net energy
            1.0 if energy_net > 0 else 0.0,  # Positive energy indicator
            abs(energy_net) / 20.0,  # Energy magnitude
            0.0
        ]
    
    def _encode_phosphorus_state(self, sensors):
        """Map phosphorus removal to state vector"""
        removal_pct = sensors.get("phosphate_removal_pct", 0)
        concentration = sensors.get("phosphate_mgL", 1.0)
        return [
            removal_pct / 100.0,
            1.0 - concentration / 5.0,  # Normalized concentration
            1.0 if removal_pct > 80 else 0.0,  # High performance indicator
            0.0
        ]
    
    def _encode_health_state(self, sensors):
        """Map ecosystem health to state vector"""
        do_level = sensors.get("DO_mgL", 5.0)
        ph = sensors.get("pH", 7.0)
        return [
            do_level / 10.0,
            (ph - 6.0) / 3.0,  # Normalized pH (6-9 range)
            1.0 if do_level > 5.0 else 0.0,  # Healthy DO indicator
            1.0 if 6.5 < ph < 8.0 else 0.0  # Healthy pH indicator
        ]
    
    def _encode_biodiversity_proxies(self, sensors):
        """Biodiversity indicators from available sensors"""
        # In real deployment, might have actual biodiversity sensors
        # For now, infer from stability metrics
        return [0.5, 0.5, 0.5, 0.5]  # Placeholder
    
    def _encode_stress_indicators(self, sensors):
        """Ecosystem stress signals"""
        do_level = sensors.get("DO_mgL", 5.0)
        temp = sensors.get("temperature_C", 20)
        return [
            1.0 if do_level < 4.0 else 0.0,  # Low DO stress
            1.0 if temp > 30 else 0.0,  # High temp stress
            0.0,  # Reserved
            0.0
        ]
    
    def _encode_efficiency_metrics(self, sensors):
        """Optimization and performance metrics"""
        removal = sensors.get("phosphate_removal_pct", 0)
        energy = sensors.get("energy_net_kWh", 0)
        return [
            removal / 100.0,
            np.tanh(energy / 5.0),
            removal * max(0, energy) / 500.0,  # Combined efficiency
            0.0
        ]
    
    def _encode_optimization_targets(self, sensors):
        """Current optimization priorities"""
        return [0.5, 0.5, 0.5, 0.5]  # Placeholder
    
    def _encode_pattern_recognition(self, sensors):
        """Learned pattern features"""
        return [0.5, 0.5, 0.5, 0.5]  # Placeholder
    
    def _encode_long_term_health(self, sensors):
        """Long-term ecosystem trajectory"""
        return [0.5, 0.5, 0.5, 0.5]  # Placeholder
    
    def _encode_community_service(self, sensors):
        """Community benefit metrics"""
        return [0.5, 0.5, 0.5, 0.5]  # Placeholder
    
    def _encode_generational_impact(self, sensors):
        """Sustainability metrics"""
        return [0.5, 0.5, 0.5, 0.5]  # Placeholder
    
    def _compute_ideal_state(self, sensors):
        """Compute ideal attractor state"""
        # This is the state the system "wants" to be in
        ideal = np.zeros(64)
        
        # Ideal thermal: moderate temperature
        ideal[0:4] = [0.5, 0.2, 1.0, 0.0]
        
        # Ideal flow: steady and adequate
        ideal[4:8] = [0.6, 0.6, 1.0, 0.0]
        
        # Ideal energy: net positive
        ideal[8:12] = [0.5, 1.0, 0.5, 0.0]
        
        # Ideal phosphorus: high removal
        ideal[12:16] = [0.9, 0.8, 1.0, 0.0]
        
        # Ideal health: high DO, neutral pH
        ideal[16:20] = [0.7, 0.5, 1.0, 1.0]
        
        # Fill rest with moderate values
        ideal[20:] = 0.5
        
        return ideal / (np.linalg.norm(ideal) + 1e-12)
    
    def coordinate_with_neighbor(self, neighbor_site_id, neighbor_bio_agent, dt=0.1):
        """
        Perform bioswarm handshake with neighboring site
        
        This enables:
        - Trust-based information sharing
        - Coordinated decision-making
        - Manipulation-resistant cooperation
        - Energy-aware coupling
        """
        # Compute coupling via relational game layer
        kappa, synergy, phase = self.rg_layer.compute_kappa(
            self.bio_agent, 
            neighbor_bio_agent,
            step=0  # Would track actual time
        )
        
        # Check for manipulation
        if (self.bio_agent.manip_post > 0.3 or 
            neighbor_bio_agent.manip_post > 0.3):
            # Veto coupling - potential manipulation detected
            return {
                "coupled": False,
                "reason": "manipulation_detected",
                "kappa": 0.0,
                "trust": self.bio_agent.trust_levels.get(neighbor_site_id, 0.5)
            }
        
        # Apply coupling if safe
        if kappa > 0.1:
            self.bio_agent.apply_coupling(
                neighbor_bio_agent.x, 
                kappa, 
                partner_id=neighbor_site_id,
                dt=dt
            )
            
            # Update trust based on interaction quality
            interaction_quality = kappa * (1.0 - max(
                self.bio_agent.manip_post,
                neighbor_bio_agent.manip_post
            ))
            
            self.bio_agent.update_trust(neighbor_site_id, interaction_quality, dt)
            
            return {
                "coupled": True,
                "kappa": kappa,
                "synergy": synergy,
                "phase": phase,
                "trust": self.bio_agent.trust_levels[neighbor_site_id],
                "shared_insights": self._extract_shareable_insights()
            }
        
        return {
            "coupled": False,
            "reason": "insufficient_synergy",
            "kappa": kappa,
            "trust": self.bio_agent.trust_levels.get(neighbor_site_id, 0.5)
        }
    
    def _extract_shareable_insights(self):
        """Extract insights that are safe to share with trusted neighbors"""
        return {
            "current_efficiency": self.eco_agent.sensors.get("phosphate_removal_pct", 0),
            "energy_balance": self.eco_agent.sensors.get("energy_net_kWh", 0),
            "ecosystem_health": self.eco_agent.sensors.get("DO_mgL", 0),
            "consciousness_level": self.eco_agent.amplification,
            "current_strategy": self.eco_agent.control_actions
        }
    
    def integrate_neighbor_insights(self, neighbor_insights, trust_level):
        """
        Incorporate trusted neighbor's insights into local decision-making
        
        Only integrates if trust > 0.6
        """
        if trust_level < 0.6:
            return  # Don't trust enough to integrate
        
        # Weight neighbor insights by trust
        weighted_influence = trust_level * 0.3  # Max 30% influence
        
        # Could adjust local strategies based on neighbor success
        neighbor_efficiency = neighbor_insights.get("current_efficiency", 0)
        my_efficiency = self.eco_agent.sensors.get("phosphate_removal_pct", 0)
        
        if neighbor_efficiency > my_efficiency * 1.2:  # Neighbor doing significantly better
            # Learn from their strategy (implement learning logic)
            pass
    
    def update_full_system(self, sensors, dt=0.1):
        """
        Complete system update: local consciousness + relational intelligence
        """
        # 1. Update local ecological consciousness
        self.eco_agent.sensors = sensors
        control_actions = self.eco_agent.decide_actions()
        consciousness_state = {
            "amplification": self.eco_agent.amplification,
            "dimensionality": len(self.eco_agent.active_dimensions),
            "confidence": self.eco_agent.decision_confidence
        }
        
        # 2. Encode into bioswarm IPF
        ipf_vector = self.encode_ecological_state_to_ipf(sensors, consciousness_state)
        
        # 3. Update bioswarm intrinsic dynamics
        self.bio_agent.intrinsic_update(dt)
        
        # 4. Update hook energy (consciousness costs energy)
        coherence_bonus = max(0, self.bio_agent.C - 0.7) * 0.1
        self.bio_agent.update_hook(dt, intrinsic_gain=coherence_bonus)
        
        # 5. Update valence (how the system "feels" about its state)
        performance_reward = (sensors.get("phosphate_removal_pct", 0) - 70) / 30.0
        health_reward = (sensors.get("DO_mgL", 5) - 5) / 5.0
        combined_reward = (performance_reward + health_reward) / 2.0
        
        self.bio_agent.update_valence(dt, local_reward=combined_reward, 
                                     coherence_bonus=coherence_bonus)
        
        return {
            "control_actions": control_actions,
            "ipf_vector": ipf_vector,
            "consciousness_state": consciousness_state,
            "bio_state": {
                "energy": self.bio_agent.H,
                "valence": self.bio_agent.v,
                "coherence": self.bio_agent.C
            }
        }

# ============================================================
# MULTI-SITE WATERSHED COORDINATION
# ============================================================

class WatershedCoordinationNetwork:
    """
    Coordinates multiple ecological sites using bioswarm relational dynamics
    """
    
    def __init__(self, site_ids):
        self.sites = {
            site_id: EcologicalBioswarmSystem(site_id) 
            for site_id in site_ids
        }
        self.coordination_log = []
    
    def update_all_sites(self, site_sensors_dict, dt=0.1):
        """Update all sites and coordinate"""
        
        # 1. Update each site independently
        site_results = {}
        for site_id, sensors in site_sensors_dict.items():
            if site_id in self.sites:
                site_results[site_id] = self.sites[site_id].update_full_system(sensors, dt)
        
        # 2. Perform inter-site coordination
        coordination_results = self._coordinate_sites(dt)
        
        # 3. Log watershed-level state
        self.coordination_log.append({
            "timestamp": sensors.get("timestamp", 0),
            "site_results": site_results,
            "coordination": coordination_results
        })
        
        return site_results, coordination_results
    
    def _coordinate_sites(self, dt):
        """Perform pairwise coordination between neighboring sites"""
        coordination = []
        
        site_ids = list(self.sites.keys())
        for i, site_a_id in enumerate(site_ids):
            for site_b_id in site_ids[i+1:]:
                # Coordinate sites A and B
                result = self.sites[site_a_id].coordinate_with_neighbor(
                    site_b_id,
                    self.sites[site_b_id].bio_agent,
                    dt
                )
                
                coordination.append({
                    "site_a": site_a_id,
                    "site_b": site_b_id,
                    **result
                })
        
        return coordination


##Add-on example

# Create watershed network
sites = ["creek_alpha", "creek_beta", "creek_gamma"]
watershed = WatershedCoordinationNetwork(sites)

# Simulate coordinated operation
for step in range(1000):
    # Gather sensor data from all sites
    site_sensors = {
        "creek_alpha": read_sensors_alpha(),
        "creek_beta": read_sensors_beta(),
        "creek_gamma": read_sensors_gamma()
    }
    
    # Update and coordinate
    results, coordination = watershed.update_all_sites(site_sensors, dt=0.1)
    
    # Apply control actions at each site
    for site_id, result in results.items():
        apply_controls(site_id, result["control_actions"])
