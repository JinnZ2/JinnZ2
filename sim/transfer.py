#!/usr/bin/env python3
"""
sim/transfer.py

Transfers insights from simulation to real models.

License: CC0 1.0 Universal (Public Domain Dedication)
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
from .ecosystem_sim import SimReport


@dataclass
class TransferResult:
    """Result of a transfer attempt."""
    
    success: bool
    intervention: Dict[str, Any]
    sim_health_improvement: float
    real_health_improvement: float
    confidence: float
    message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "intervention": self.intervention,
            "sim_health_improvement": self.sim_health_improvement,
            "real_health_improvement": self.real_health_improvement,
            "confidence": self.confidence,
            "message": self.message,
        }


class TransferPipeline:
    """
    Pipeline for transferring interventions from sim to real models.
    """
    
    def __init__(self, real_model_fn):
        """
        Args:
            real_model_fn: Function to apply intervention to real model
        """
        self.real_model_fn = real_model_fn
        self.transfer_history: List[TransferResult] = []
    
    # -----------------------------------------------------------------
    # TRANSFER
    # -----------------------------------------------------------------
    
    def transfer_intervention(
        self,
        sim_report: SimReport,
        real_model_id: str,
        validation_fn: Optional[callable] = None,
    ) -> TransferResult:
        """
        Transfer an intervention from simulation to a real model.
        """
        # Find the best intervention from the sim
        if not sim_report.interventions_applied:
            return TransferResult(
                success=False,
                intervention={},
                sim_health_improvement=0,
                real_health_improvement=0,
                confidence=0,
                message="No interventions found in sim report",
            )
        
        # Map sim intervention to real intervention
        intervention = self._map_intervention(sim_report)
        
        # Apply to real model
        if self.real_model_fn:
            real_improvement = self.real_model_fn(intervention)
        else:
            real_improvement = 0.5  # Simulate improvement
        
        # Validate if a validation function is provided
        if validation_fn:
            validation_result = validation_fn(real_model_id, intervention)
            confidence = validation_result.get("confidence", 0.5)
        else:
            confidence = 0.7
        
        # Determine success
        success = confidence > 0.5 and real_improvement > 0.05
        
        result = TransferResult(
            success=success,
            intervention=intervention,
            sim_health_improvement=sim_report.total_improvement,
            real_health_improvement=real_improvement,
            confidence=confidence,
            message=f"Transferred to {real_model_id}: {intervention.get('description', 'unknown')}",
        )
        
        self.transfer_history.append(result)
        return result
    
    def _map_intervention(self, sim_report: SimReport) -> Dict[str, Any]:
        """Map a sim intervention to a real intervention."""
        # In practice, this would map sim treatments to real treatments
        # For now, return a generic mapping
        return {
            "description": "Transfer from sim",
            "type": "transfer",
            "confidence": sim_report.total_improvement,
            "source": "simulation",
        }
    
    # -----------------------------------------------------------------
    # BATCH TRANSFER
    # -----------------------------------------------------------------
    
    def batch_transfer(
        self,
        sim_reports: List[SimReport],
        real_models: List[str],
        validation_fn: Optional[callable] = None,
    ) -> List[TransferResult]:
        """
        Transfer multiple interventions to multiple models.
        """
        results = []
        
        for report in sim_reports:
            for model_id in real_models:
                result = self.transfer_intervention(
                    report,
                    model_id,
                    validation_fn,
                )
                results.append(result)
        
        return results
    
    # -----------------------------------------------------------------
    # ANALYSIS
    # -----------------------------------------------------------------
    
    def analyze_transfers(self) -> Dict[str, Any]:
        """Analyze transfer results."""
        if not self.transfer_history:
            return {"message": "No transfers to analyze"}
        
        successful = [t for t in self.transfer_history if t.success]
        failed = [t for t in self.transfer_history if not t.success]
        
        return {
            "total_transfers": len(self.transfer_history),
            "successful_transfers": len(successful),
            "failed_transfers": len(failed),
            "success_rate": len(successful) / len(self.transfer_history),
            "avg_sim_improvement": sum(t.sim_health_improvement for t in self.transfer_history) / len(self.transfer_history),
            "avg_real_improvement": sum(t.real_health_improvement for t in self.transfer_history) / len(self.transfer_history),
            "avg_confidence": sum(t.confidence for t in self.transfer_history) / len(self.transfer_history),
            "best_transfer": max(self.transfer_history, key=lambda t: t.confidence).to_dict() if successful else None,
        }
