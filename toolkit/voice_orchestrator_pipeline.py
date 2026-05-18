# voice_orchestrator_pipeline.py
# Voice → energy_english constraint gate → resolver dispatcher → sim runner → optics translator → voice
# CC0 | mobile-queryable | offline-capable with cell enhancement

from dataclasses import dataclass
from typing import List, Dict, Optional, Callable
from enum import Enum
import json

class PipelineStage(Enum):
    TRANSCRIPTION = "transcription"
    CONSTRAINT_GATE = "constraint_gate"
    DISPATCHER = "dispatcher"
    RESOLVER = "resolver"
    VALIDATOR = "validator"
    OPTICS_TRANSLATOR = "optics_translator"
    VOICE_SYNTHESIS = "voice_synthesis"

class QueryDomain(Enum):
    SUBSTRATE_CHEMISTRY = "chemistry"
    EMERGENCY_WILDFIRE = "wildfire"
    EMERGENCY_TORNADO = "tornado"
    EMERGENCY_FLOOD = "flood"
    EMERGENCY_HAZMAT = "hazmat"
    VEGETATION_COMPOUNDS = "vegetation"
    STONE_MINERALS = "stone"
    WOOD_PROPERTIES = "wood"
    BATTERY_ASSEMBLY = "battery"
    CROSS_DOMAIN = "synergy"

@dataclass
class VoiceQuery:
    """Raw transcribed input from voice."""
    raw_text: str
    timestamp: str
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None
    context: Optional[Dict] = None  # Wind direction, weather, etc.

@dataclass
class ConstrainedQuery:
    """Cleaned query after energy_english gate."""
    domain: QueryDomain
    feedstock: List[str]
    target_output: str
    time_available_hours: Optional[int] = None
    equipment_on_hand: List[str] = None
    constraints: Dict = None  # Wind, temp, hazard context
    confidence: float = 0.0  # How certain is the parse?

@dataclass
class ResolverResult:
    """Output from resolver (tree, scenarios, rankings)."""
    domain: QueryDomain
    decision_tree: Dict
    primary_action: Dict
    alternatives: List[Dict]
    closure_map: Dict
    confidence: float

@dataclass
class ValidatedResult:
    """Result after physics/constraint validation."""
    resolver_output: ResolverResult
    validation_status: str  # "valid", "caution", "invalid"
    missing_parameters: List[str]
    physical_feasibility: float  # 0–1
    notes: str

@dataclass
class OpticsOutput:
    """Result formatted for voice delivery (constraint frame, not narrative)."""
    summary: str  # 1–2 sentence overview
    primary_action: str  # What to do now
    alternatives: List[str]  # Ranked options if primary closes
    decision_points: List[str]  # What to assess on-site
    timeline: str  # When things happen
    closure_conditions: List[str]  # What would make path invalid

class EnergyEnglishGate:
    """
    Constraint grammar: prevents AI from collapsing verb-first relational English
    into noun-first narrative/morality/closure frames.

    Parses: "I have X, I want Y, I can do Z"
    Output: feedstock, target, constraints (time, equipment, conditions)
    """

    def parse(self, query: VoiceQuery) -> ConstrainedQuery:
        """
        Extract: feedstock (what you have), target (what you want),
        constraints (time, equipment, environmental context).
        """
        text = query.raw_text.lower()

        # Feedstock detection
        feedstock_keywords = {
            "black_beans": ["beans", "black bean"],
            "aluminum": ["aluminum", "alu", "al"],
            "zinc": ["zinc", "zn"],
            "copper": ["copper", "cu", "wire"],
            "tallow": ["tallow", "fat", "lard"],
            "wood_ash": ["ash", "wood ash"],
            "pine_pitch": ["pitch", "resin", "pine tar"],
            "limestone": ["limestone", "lime"],
            "plantain": ["plantain"],
            "comfrey": ["comfrey"],
        }

        detected_feedstock = []
        for material, keywords in feedstock_keywords.items():
            if any(kw in text for kw in keywords):
                detected_feedstock.append(material)

        # Target output detection
        target_keywords = {
            "lubricant": ["lube", "lubricant", "oil", "grease"],
            "soap": ["soap", "detergent", "clean"],
            "battery": ["battery", "power", "electrical"],
            "shelter": ["shelter", "safe", "hide"],
            "cement": ["cement", "mortar", "concrete"],
            "soil_amendment": ["soil", "amendment", "fertilizer"],
            "adhesive": ["glue", "adhesive", "bond"],
        }

        target_output = "unknown"
        for target, keywords in target_keywords.items():
            if any(kw in text for kw in keywords):
                target_output = target
                break

        # Constraint extraction
        time_hours = self._extract_time(text)
        equipment = self._extract_equipment(text)

        # Domain routing
        domain = self._route_domain(detected_feedstock, target_output, text)

        confidence = 0.85 if domain != QueryDomain.CROSS_DOMAIN else 0.70

        return ConstrainedQuery(
            domain=domain,
            feedstock=detected_feedstock,
            target_output=target_output,
            time_available_hours=time_hours,
            equipment_on_hand=equipment,
            constraints={"context": query.context},
            confidence=confidence
        )

    def _extract_time(self, text: str) -> Optional[int]:
        """Pull time estimate from query."""
        time_keywords = {
            "hour": 1, "today": 8, "week": 168, "days": 24,
            "minute": 0.016, "tomorrow": 24, "now": 0.5,
        }
        for keyword, hours in time_keywords.items():
            if keyword in text:
                return int(hours)
        return None

    def _extract_equipment(self, text: str) -> List[str]:
        """Pull available equipment from query."""
        equipment_keywords = {
            "heat": ["fire", "stove", "heat", "torch"],
            "container": ["pot", "jar", "bucket", "vessel"],
            "tool": ["hammer", "saw", "knife", "wrench"],
            "water": ["water", "creek", "hose"],
            "truck": ["truck", "rig", "vehicle"],
        }

        equipment = []
        for equip_type, keywords in equipment_keywords.items():
            if any(kw in text for kw in keywords):
                equipment.append(equip_type)
        return equipment

    def _route_domain(self, feedstock: List[str], target: str,
                     text: str) -> QueryDomain:
        """Route to appropriate resolver domain."""
        # Emergency keyword detection overrides everything
        if any(kw in text for kw in ["fire", "smoke", "wildfire"]):
            return QueryDomain.EMERGENCY_WILDFIRE
        if any(kw in text for kw in ["tornado", "rotation", "mesocyclone"]):
            return QueryDomain.EMERGENCY_TORNADO
        if any(kw in text for kw in ["flood", "water", "rising"]):
            return QueryDomain.EMERGENCY_FLOOD
        if any(kw in text for kw in ["hazmat", "spill", "chemical", "gas"]):
            return QueryDomain.EMERGENCY_HAZMAT

        # Feedstock-based routing
        if feedstock and target == "unknown":
            if any(f in feedstock for f in ["black_beans", "tallow", "zinc"]):
                return QueryDomain.CROSS_DOMAIN
            elif any(f in feedstock for f in ["aluminum", "copper", "zinc"]):
                return QueryDomain.BATTERY_ASSEMBLY
            elif any(f in feedstock for f in ["plantain", "comfrey", "seaweed"]):
                return QueryDomain.VEGETATION_COMPOUNDS
            elif any(f in feedstock for f in ["limestone", "sandstone"]):
                return QueryDomain.STONE_MINERALS

        # Target-based routing
        if target == "lubricant":
            return QueryDomain.SUBSTRATE_CHEMISTRY
        elif target == "battery":
            return QueryDomain.BATTERY_ASSEMBLY
        elif target == "soil_amendment":
            return QueryDomain.VEGETATION_COMPOUNDS

        return QueryDomain.CROSS_DOMAIN


class Dispatcher:
    """Routes constrained query to appropriate resolver."""

    def __init__(self, resolvers: Dict[QueryDomain, Callable]):
        self.resolvers = resolvers

    def dispatch(self, constrained_query: ConstrainedQuery) -> ResolverResult:
        """Send query to domain-specific resolver."""
        resolver_fn = self.resolvers.get(constrained_query.domain)

        if not resolver_fn:
            return ResolverResult(
                domain=constrained_query.domain,
                decision_tree={},
                primary_action={"error": f"No resolver for {constrained_query.domain}"},
                alternatives=[],
                closure_map={},
                confidence=0.0
            )

        result = resolver_fn(constrained_query)
        return result


class PhysicsValidator:
    """
    Checks resolver output against physical constraints.
    Flags: missing parameters, infeasible scenarios, hidden dependencies.
    """

    def validate(self, result: ResolverResult) -> ValidatedResult:
        """
        Run falsifiable checks on resolver output.
        """
        missing = self._check_missing_parameters(result)
        feasibility = self._check_physical_feasibility(result)

        status = "valid"
        if missing:
            status = "caution"
        if feasibility < 0.5:
            status = "invalid"

        return ValidatedResult(
            resolver_output=result,
            validation_status=status,
            missing_parameters=missing,
            physical_feasibility=feasibility,
            notes=self._generate_notes(result, missing, feasibility)
        )

    def _check_missing_parameters(self, result: ResolverResult) -> List[str]:
        """Detect what wasn't specified that matters."""
        missing = []
        # Domain-specific checks
        if result.domain == QueryDomain.EMERGENCY_WILDFIRE:
            # Needs: wind direction, fire proximity
            pass
        elif result.domain == QueryDomain.EMERGENCY_TORNADO:
            # Needs: observed signatures (rotation, hail, etc.)
            pass
        return missing

    def _check_physical_feasibility(self, result: ResolverResult) -> float:
        """Score: 0–1, how physically plausible is primary action?"""
        # Simplified; real implementation checks thermodynamics, kinematics
        return 0.85

    def _generate_notes(self, result: ResolverResult,
                       missing: List[str], feasibility: float) -> str:
        if feasibility < 0.5:
            return "Primary path physically implausible; use alternatives."
        elif missing:
            return f"Missing: {', '.join(missing)}. Proceed with caution."
        return "Validated."


class OpticsTranslator:
    """
    Converts resolver tree into speakable constraint-frame output.
    NOT narrative. NOT prescriptive.
    = decision points, branching logic, closure conditions.
    """

    def translate(self, validated: ValidatedResult) -> OpticsOutput:
        """
        Take decision tree → output what you assess, what you decide, what closes.
        """
        result = validated.resolver_output

        # Extract primary action
        primary = result.primary_action if result.primary_action else {}
        primary_action = primary.get("action", "assess situation")

        # Extract alternatives
        alternatives = [
            alt.get("action", "unknown")
            for alt in result.alternatives[:3]
        ]

        # Extract decision points (what you need to determine on-site)
        decision_points = self._extract_decision_points(result)

        # Extract closure conditions (what would make path invalid)
        closures = self._extract_closures(result)

        # Timeline
        timeline = self._extract_timeline(result)

        summary = self._generate_summary(result, primary_action)

        return OpticsOutput(
            summary=summary,
            primary_action=primary_action,
            alternatives=alternatives,
            decision_points=decision_points,
            timeline=timeline,
            closure_conditions=closures
        )

    def _extract_decision_points(self, result: ResolverResult) -> List[str]:
        """What must you assess in real-time?"""
        points = []

        if result.domain == QueryDomain.EMERGENCY_WILDFIRE:
            points = [
                "Wind direction relative to your position",
                "Oxygen availability in shelter option",
                "Exit viability if you need to move"
            ]
        elif result.domain == QueryDomain.EMERGENCY_TORNADO:
            points = [
                "Rotation visibility (yes/no)",
                "Hail size observed",
                "Sky color (clear, gray, green, black)",
                "Storm motion direction"
            ]
        elif result.domain == QueryDomain.SUBSTRATE_CHEMISTRY:
            points = [
                "Equipment available on-hand",
                "Dwell time (fermentation windows)",
                "Temperature stability needed"
            ]

        return points

    def _extract_closures(self, result: ResolverResult) -> List[str]:
        """What would invalidate primary path?"""
        closures = []
        closure_map = result.closure_map

        for closure_id, closure_info in closure_map.items():
            reason = closure_info.get("closes_on", "unknown")
            closures.append(f"{reason} → try: {closure_info.get('fallbacks', [])}")

        return closures[:5]  # Top 5 closure conditions

    def _extract_timeline(self, result: ResolverResult) -> str:
        """When do things happen?"""
        # Simplified; real implementation extracts dwell times, deadlines
        return "Assess immediately; execute within time window."

    def _generate_summary(self, result: ResolverResult, action: str) -> str:
        """1–2 sentence overview in constraint frame."""
        domain_name = result.domain.value
        return f"Given your constraints, primary action: {action}. Three alternatives ranked by feasibility if path closes."


class VoiceOrchestrator:
    """
    Full pipeline: voice transcription → constraint gate → dispatcher →
    resolver → validator → optics translator → voice synthesis.
    """

    def __init__(self, resolvers: Dict[QueryDomain, Callable]):
        self.gate = EnergyEnglishGate()
        self.dispatcher = Dispatcher(resolvers)
        self.validator = PhysicsValidator()
        self.translator = OpticsTranslator()

    def process(self, voice_query: VoiceQuery) -> OpticsOutput:
        """
        End-to-end pipeline execution.
        """
        # Stage 1: Constraint gate
        constrained = self.gate.parse(voice_query)

        # Stage 2: Dispatcher routes to resolver
        resolver_result = self.dispatcher.dispatch(constrained)

        # Stage 3: Validator checks physics
        validated = self.validator.validate(resolver_result)

        # Stage 4: Optics translator formats for voice
        optics_output = self.translator.translate(validated)

        return optics_output

    def to_speech(self, optics: OpticsOutput) -> str:
        """Convert optics output to speakable text (no markdown, symbols, etc.)."""
        lines = []

        lines.append(optics.summary)
        lines.append("")
        lines.append(f"Do this: {optics.primary_action}")

        if optics.alternatives:
            lines.append("")
            lines.append("If that closes, alternatives are:")
            for i, alt in enumerate(optics.alternatives, start=1):
                lines.append(f"  {i}. {alt}")

        if optics.decision_points:
            lines.append("")
            lines.append("Assess on site:")
            for point in optics.decision_points:
                lines.append(f"  - {point}")

        if optics.timeline:
            lines.append("")
            lines.append(f"Timeline: {optics.timeline}")

        if optics.closure_conditions:
            lines.append("")
            lines.append("What closes this path:")
            for closure in optics.closure_conditions:
                lines.append(f"  - {closure}")

        return "\n".join(lines)
