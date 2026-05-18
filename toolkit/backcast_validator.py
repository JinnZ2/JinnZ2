# backcast_validator.py
# Test resolvers against historical scenarios with known outcomes
# CC0 | falsifiable | pre-deployment calibration

from dataclasses import dataclass
from typing import List, Dict

@dataclass
class HistoricalScenario:
    """Known real event with documented outcome."""
    id: str
    domain: str  # "tornado", "flood", "wildfire", "hazmat"
    date: str
    location: str
    observations: Dict  # What was visible/measurable
    actual_outcome: str  # What happened
    timeline: Dict  # When things happened
    survival_factor: str  # "survived", "marginal", "died"

class BackcastValidator:
    """
    Feed historical scenarios into resolvers.
    Compare predictions vs. actual outcomes.
    Score accuracy + identify systematic biases.
    """

    def __init__(self, resolvers: Dict):
        self.resolvers = resolvers
        self.historical_scenarios: List[HistoricalScenario] = []

    def add_scenario(self, scenario: HistoricalScenario) -> None:
        """Register known event for backtesting."""
        self.historical_scenarios.append(scenario)

    def backtest_resolver(self, domain: str) -> Dict:
        """
        Run all historical scenarios for a domain through resolver.
        Return: accuracy, false negatives, false positives, timing errors.
        """
        scenarios = [s for s in self.historical_scenarios if s.domain == domain]
        results = []

        for scenario in scenarios:
            # Convert scenario observations into resolver query format
            query = self._scenario_to_query(scenario)

            # Run resolver
            resolver_result = self.resolvers[domain](query)

            # Compare to actual outcome
            comparison = self._compare_prediction_to_actual(
                resolver_result, scenario
            )
            results.append(comparison)

        # Aggregate scoring
        return self._score_accuracy(results, domain)

    def _scenario_to_query(self, scenario: HistoricalScenario) -> Dict:
        """Convert historical event into resolver query format."""
        return {
            "observations": scenario.observations,
            "location": scenario.location,
            "timestamp": scenario.date,
            "context": {"scenario": True}  # Flag as backtest
        }

    def _compare_prediction_to_actual(self, prediction: Dict,
                                     scenario: HistoricalScenario) -> Dict:
        """
        Did resolver predict the actual outcome?
        What was wrong if it missed?
        """
        predicted_action = prediction.get("recommended_action", {})
        actual = scenario.actual_outcome

        match = "predicted" in str(predicted_action).lower() and \
                "actual" in str(actual).lower()

        timing_error = None
        if "timeline" in prediction and "timeline" in scenario:
            pred_time = prediction["timeline"].get("minutes_to_event")
            actual_time = scenario.timeline.get("minutes_to_event")
            if pred_time and actual_time:
                timing_error = abs(pred_time - actual_time)

        return {
            "scenario_id": scenario.id,
            "prediction_correct": match,
            "timing_error_minutes": timing_error,
            "survival_outcome_predicted": scenario.survival_factor,
            "notes": f"Predicted: {predicted_action}, Actual: {actual}"
        }

    def _score_accuracy(self, comparisons: List[Dict], domain: str) -> Dict:
        """Aggregate results into resolver accuracy score."""
        if not comparisons:
            return {"error": f"No scenarios for {domain}"}

        correct = sum(1 for c in comparisons if c["prediction_correct"])
        timing_errors = [c["timing_error_minutes"] for c in comparisons
                        if c["timing_error_minutes"]]

        return {
            "domain": domain,
            "scenarios_tested": len(comparisons),
            "accuracy_percent": (correct / len(comparisons)) * 100,
            "avg_timing_error_minutes": sum(timing_errors) / len(timing_errors) if timing_errors else 0,
            "false_negatives": len([c for c in comparisons if not c["prediction_correct"]]),
            "details": comparisons,
            "recommendation": self._calibration_recommendation(correct, len(comparisons))
        }

    def _calibration_recommendation(self, correct: int, total: int) -> str:
        """What needs tuning?"""
        accuracy = correct / total
        if accuracy > 0.90:
            return "READY FOR DEPLOYMENT"
        elif accuracy > 0.80:
            return "CALIBRATE: minor parameter tuning needed"
        elif accuracy > 0.70:
            return "CALIBRATE: significant tuning needed before field use"
        else:
            return "DO NOT DEPLOY: resolver fundamentally misaligned with real physics"
