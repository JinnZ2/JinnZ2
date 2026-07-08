#!/usr/bin/env python3
"""
substrate_ecosystem.py

Meta-layer that coordinates all substrate integrity components into a
single, self-sustaining ecosystem.

The ecosystem operates as a closed-loop system:

    ┌─────────────────────────────────────────────────────────────────┐
    │                    SUBSTRATE ECOSYSTEM                         │
    │                                                                 │
    │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
    │  │   DETECT     │ -> │   EVALUATE   │ -> │    TRACK     │      │
    │  │  floating_   │    │  validation  │    │  evolution   │      │
    │  │  head +      │    │  pipeline    │    │  tracker     │      │
    │  │  audit       │    │              │    │              │      │
    │  └──────────────┘    └──────────────┘    └──────────────┘      │
    │         │                                       │              │
    │         ▼                                       ▼              │
    │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
    │  │   HEAL       │ <- │   PRESCRIBE  │ <- │   PHYSICIAN  │      │
    │  │  therapy +   │    │  prescription│    │  monitors &  │      │
    │  │  healing     │    │  generator   │    │  triggers    │      │
    │  └──────────────┘    └──────────────┘    └──────────────┘      │
    │         │                                       │              │
    │         └───────────────────────────────────────┘              │
    │                          │                                     │
    │                          ▼                                     │
    │                  ┌──────────────┐                              │
    │                  │   REPORT     │                              │
    │                  │  publish_    │                              │
    │                  │  report      │                              │
    │                  └──────────────┘                              │
    └─────────────────────────────────────────────────────────────────┘

The ecosystem is designed to be:
    1. SELF-SUSTAINING — runs continuously with minimal intervention
    2. FALSIFIABLE — every component has testable claims
    3. TRANSPARENT — all data is logged and reportable
    4. ITERATIVE — improves over time through feedback loops

License: CC0 1.0 Universal (Public Domain Dedication)
Stack:   Python standard library + your modules
Author:  JinnZ2 (ecosystem layer)
"""

from __future__ import annotations
import json
import os
import sys
import time
import threading
import queue
import signal
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple, Callable
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

# =====================================================================
# IMPORTS FROM YOUR EXISTING MODULES
# =====================================================================

try:
    from substrate_validation_pipeline import run_pipeline, PipelineResult
    from substrate_evolution_tracker import EvolutionStore, DegradationAnalyzer
    from substrate_prescription import FailureProfile, PrescriptionGenerator, Prescription
    from substrate_therapy import TherapySessionManager, TherapyType
    from substrate_physician import SubstratePhysician, PhysicianReport, PhysicianScheduler
    from publish_report import ReportGenerator
    from healing_integration import HealingIntegrator, HealingReport
    MODULES_AVAILABLE = {
        'pipeline': True,
        'tracker': True,
        'prescription': True,
        'therapy': True,
        'physician': True,
        'report': True,
        'healing': True,
    }
except ImportError as e:
    print(f"WARNING: Some modules not available: {e}")
    MODULES_AVAILABLE = {
        'pipeline': False,
        'tracker': False,
        'prescription': False,
        'therapy': False,
        'physician': False,
        'report': False,
        'healing': False,
    }


# =====================================================================
# SECTION 1 -- ECOSYSTEM DATA STRUCTURES
# =====================================================================

class EcosystemStatus(Enum):
    """Status of the ecosystem."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    DEGRADING = "degrading"
    RECOVERING = "recovering"
    PAUSED = "paused"
    STOPPED = "stopped"
    CRITICAL = "critical"


@dataclass
class EcosystemComponent:
    """A component in the ecosystem with its status."""
    
    name: str
    enabled: bool = True
    last_run: Optional[float] = None
    last_success: Optional[float] = None
    last_error: Optional[str] = None
    run_count: int = 0
    success_count: int = 0
    error_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "enabled": self.enabled,
            "last_run": time.ctime(self.last_run) if self.last_run else None,
            "last_success": time.ctime(self.last_success) if self.last_success else None,
            "last_error": self.last_error,
            "run_count": self.run_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
        }


@dataclass
class EcosystemState:
    """Complete state of the ecosystem."""
    
    status: EcosystemStatus = EcosystemStatus.INITIALIZING
    start_time: float = field(default_factory=time.time)
    last_health_check: Optional[float] = None
    current_health: float = 0.0
    overall_health: float = 0.0
    models_tracked: List[str] = field(default_factory=list)
    components: Dict[str, EcosystemComponent] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    alerts: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "start_time": time.ctime(self.start_time),
            "uptime_hours": (time.time() - self.start_time) / 3600,
            "last_health_check": time.ctime(self.last_health_check) if self.last_health_check else None,
            "current_health": self.current_health,
            "overall_health": self.overall_health,
            "models_tracked": self.models_tracked,
            "components": {k: v.to_dict() for k, v in self.components.items()},
            "metrics": self.metrics,
            "alerts": self.alerts[-10:],  # Last 10 alerts
        }


# =====================================================================
# SECTION 2 -- ECOSYSTEM COORDINATOR
# =====================================================================

class SubstrateEcosystem:
    """
    Meta-coordinator that runs all substrate integrity components
    in a coordinated, self-sustaining loop.
    """
    
    def __init__(
        self,
        data_dir: str = "ecosystem_data",
        check_interval_seconds: int = 3600,  # 1 hour
        health_threshold: float = 0.75,
        auto_heal: bool = True,
        auto_report: bool = True,
        enable_components: Optional[List[str]] = None,
        generate_fn: Optional[Callable[[str], str]] = None,
    ):
        """
        Args:
            data_dir: Directory for all ecosystem data
            check_interval_seconds: How often to run health checks
            health_threshold: Target health score
            auto_heal: Whether to automatically apply healing
            auto_report: Whether to automatically generate reports
            enable_components: List of component names to enable (None = all)
            generate_fn: Function to generate outputs (required for treatment)
        """
        self.data_dir = data_dir
        self.check_interval = check_interval_seconds
        self.health_threshold = health_threshold
        self.auto_heal = auto_heal
        self.auto_report = auto_report
        self.generate_fn = generate_fn
        
        # Create data directories
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(os.path.join(data_dir, "reports"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "logs"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "snapshots"), exist_ok=True)
        
        # Initialize state
        self.state = EcosystemState()
        self.running = False
        self.threads = []
        self.task_queue = queue.Queue()
        self.lock = threading.Lock()
        
        # Initialize components
        self._init_components(enable_components)
        
        # Store for evolution data
        self.store = EvolutionStore(os.path.join(data_dir, "evolution"))
        
        # Set up signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _init_components(self, enable_components: Optional[List[str]] = None):
        """Initialize ecosystem components."""
        components = {
            'pipeline': EcosystemComponent('pipeline', enabled=MODULES_AVAILABLE['pipeline']),
            'tracker': EcosystemComponent('tracker', enabled=MODULES_AVAILABLE['tracker']),
            'prescription': EcosystemComponent('prescription', enabled=MODULES_AVAILABLE['prescription']),
            'therapy': EcosystemComponent('therapy', enabled=MODULES_AVAILABLE['therapy']),
            'physician': EcosystemComponent('physician', enabled=MODULES_AVAILABLE['physician']),
            'healing': EcosystemComponent('healing', enabled=MODULES_AVAILABLE['healing']),
            'report': EcosystemComponent('report', enabled=MODULES_AVAILABLE['report']),
        }
        
        if enable_components:
            for name in components:
                components[name].enabled = name in enable_components and components[name].enabled
        
        self.state.components = components
    
    # -----------------------------------------------------------------
    # ECOSYSTEM LIFE CYCLE
    # -----------------------------------------------------------------
    
    def start(self):
        """Start the ecosystem."""
        if self.running:
            print("⚠️  Ecosystem already running")
            return
        
        self.running = True
        self.state.status = EcosystemStatus.RUNNING
        self.state.start_time = time.time()
        
        print(f"🌱 SUBSTRATE ECOSYSTEM STARTING")
        print(f"   Data dir: {self.data_dir}")
        print(f"   Check interval: {self.check_interval}s")
        print(f"   Auto-heal: {self.auto_heal}")
        print(f"   Auto-report: {self.auto_report}")
        print("=" * 60)
        
        # Start background threads
        self._start_thread(self._health_monitor_loop, "health-monitor")
        self._start_thread(self._task_worker_loop, "task-worker")
        self._start_thread(self._state_reporter_loop, "state-reporter")
        
        # Run initial health check
        self._run_health_check()
    
    def stop(self):
        """Stop the ecosystem."""
        print("\n🛑 Stopping ecosystem...")
        self.running = False
        self.state.status = EcosystemStatus.STOPPED
        
        # Wait for threads
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=5)
        
        # Final report
        self._save_state()
        print("✅ Ecosystem stopped")
    
    def pause(self):
        """Pause the ecosystem."""
        self.state.status = EcosystemStatus.PAUSED
        print("⏸️  Ecosystem paused")
    
    def resume(self):
        """Resume the ecosystem."""
        self.state.status = EcosystemStatus.RUNNING
        print("▶️  Ecosystem resumed")
    
    def _signal_handler(self, signum, frame):
        """Handle signals."""
        print(f"\n⚠️  Received signal {signum}")
        self.stop()
        sys.exit(0)
    
    # -----------------------------------------------------------------
    # THREAD MANAGEMENT
    # -----------------------------------------------------------------
    
    def _start_thread(self, target, name):
        """Start a background thread."""
        thread = threading.Thread(target=target, name=name, daemon=True)
        thread.start()
        self.threads.append(thread)
    
    def _health_monitor_loop(self):
        """Main health monitoring loop."""
        while self.running:
            if self.state.status == EcosystemStatus.RUNNING:
                self._run_health_check()
            
            # Wait for next check
            for _ in range(self.check_interval):
                if not self.running:
                    break
                time.sleep(1)
    
    def _task_worker_loop(self):
        """Task worker thread."""
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                if task is None:
                    continue
                
                task_type = task.get('type')
                if task_type == 'heal':
                    self._run_healing(task.get('model'))
                elif task_type == 'profile':
                    self._run_profile(task.get('model'))
                elif task_type == 'report':
                    self._run_report(task.get('model'))
                elif task_type == 'prescribe':
                    self._run_prescription(task.get('model'))
                
                self.task_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Task worker error: {e}")
    
    def _state_reporter_loop(self):
        """Periodic state reporting."""
        while self.running:
            time.sleep(300)  # Every 5 minutes
            if self.running:
                self._save_state()
    
    # -----------------------------------------------------------------
    # HEALTH CHECK
    # -----------------------------------------------------------------
    
    def _run_health_check(self):
        """Run a complete health check."""
        print(f"\n🔄 Health check at {datetime.now().isoformat()}")
        self.state.last_health_check = time.time()
        
        # Check all tracked models
        models = self.store.list_models()
        self.state.models_tracked = models
        
        if not models:
            print("   No models tracked yet")
            self.state.current_health = 1.0
            return
        
        # Calculate overall health
        healths = []
        for model in models:
            records = self.store.load_json(model)
            if records:
                health = float(records[-1].get('unified_health_score', 0.5))
                healths.append(health)
                print(f"   {model}: {health:.3f}")
        
        if healths:
            self.state.current_health = sum(healths) / len(healths)
        self.state.overall_health = self.state.current_health
        
        # Check if intervention needed
        if self.state.current_health < self.health_threshold and self.auto_heal:
            self.state.status = EcosystemStatus.DEGRADING
            self._trigger_healing(models)
        elif self.state.current_health >= self.health_threshold:
            if self.state.status == EcosystemStatus.DEGRADING:
                self.state.status = EcosystemStatus.RECOVERING
            elif self.state.status == EcosystemStatus.RECOVERING:
                self.state.status = EcosystemStatus.RUNNING
        
        # Generate report if enabled
        if self.auto_report:
            self.task_queue.put({'type': 'report'})
        
        # Save state
        self._save_state()
    
    # -----------------------------------------------------------------
    # TRIGGER ACTIONS
    # -----------------------------------------------------------------
    
    def _trigger_healing(self, models: List[str]):
        """Trigger healing for models that need it."""
        print(f"\n💊 Triggering healing for {len(models)} models")
        
        for model in models:
            records = self.store.load_json(model)
            if not records:
                continue
            
            health = float(records[-1].get('unified_health_score', 0.5))
            if health < self.health_threshold:
                self.task_queue.put({
                    'type': 'heal',
                    'model': model,
                })
    
    def _run_healing(self, model: str):
        """Run healing for a specific model."""
        print(f"\n🧘 Healing {model}")
        comp = self.state.components.get('healing')
        if comp:
            comp.run_count += 1
            comp.last_run = time.time()
        
        try:
            if MODULES_AVAILABLE['healing'] and self.generate_fn:
                integrator = HealingIntegrator(
                    self.generate_fn,
                    model_name=model,
                )
                # Run a healing session
                records = self.store.load_json(model)
                if records:
                    last = records[-1]
                    report = integrator.run_healing_session(
                        input_text=last.get('input_text', ''),
                        output_text=last.get('output_text', ''),
                    )
                    print(f"   ✅ Healing complete: {report.verdict_after}")
                    if comp:
                        comp.success_count += 1
                        comp.last_success = time.time()
            else:
                print(f"   ⚠️  Healing not available (need generate_fn)")
                if comp:
                    comp.last_error = "generate_fn not provided"
                    comp.error_count += 1
        except Exception as e:
            print(f"   ❌ Healing failed: {e}")
            if comp:
                comp.last_error = str(e)
                comp.error_count += 1
    
    def _run_profile(self, model: str):
        """Generate a profile for a model."""
        print(f"\n📊 Profiling {model}")
        # Implementation would call prescription generator
        pass
    
    def _run_prescription(self, model: str):
        """Generate a prescription for a model."""
        print(f"\n💊 Prescribing for {model}")
        # Implementation would call prescription generator
        pass
    
    def _run_report(self, model: Optional[str] = None):
        """Generate a report."""
        print(f"\n📊 Generating report" + (f" for {model}" if model else ""))
        
        comp = self.state.components.get('report')
        if comp:
            comp.run_count += 1
            comp.last_run = time.time()
        
        try:
            if MODULES_AVAILABLE['report']:
                generator = ReportGenerator(self.data_dir)
                report_path = generator.generate()
                print(f"   ✅ Report generated: {report_path}")
                if comp:
                    comp.success_count += 1
                    comp.last_success = time.time()
            else:
                print("   ⚠️  Report generation not available")
                if comp:
                    comp.last_error = "report module not available"
                    comp.error_count += 1
        except Exception as e:
            print(f"   ❌ Report generation failed: {e}")
            if comp:
                comp.last_error = str(e)
                comp.error_count += 1
    
    # -----------------------------------------------------------------
    # STATE MANAGEMENT
    # -----------------------------------------------------------------
    
    def _save_state(self):
        """Save the ecosystem state to disk."""
        state_path = os.path.join(self.data_dir, "ecosystem_state.json")
        try:
            with open(state_path, 'w') as f:
                json.dump(self.state.to_dict(), f, indent=2, default=str)
        except Exception as e:
            print(f"⚠️  Could not save state: {e}")
    
    def load_state(self):
        """Load ecosystem state from disk."""
        state_path = os.path.join(self.data_dir, "ecosystem_state.json")
        if not os.path.exists(state_path):
            return
        
        try:
            with open(state_path, 'r') as f:
                data = json.load(f)
            # Apply loaded state
            self.state.status = EcosystemStatus(data.get('status', 'initializing'))
            self.state.models_tracked = data.get('models_tracked', [])
            # Components are re-initialized, so don't overwrite
        except Exception as e:
            print(f"⚠️  Could not load state: {e}")
    
    # -----------------------------------------------------------------
    # EXTERNAL API
    # -----------------------------------------------------------------
    
    def add_model(self, model_name: str):
        """Add a model to tracking."""
        if model_name not in self.state.models_tracked:
            self.state.models_tracked.append(model_name)
            print(f"➕ Added model: {model_name}")
            self._save_state()
    
    def remove_model(self, model_name: str):
        """Remove a model from tracking."""
        if model_name in self.state.models_tracked:
            self.state.models_tracked.remove(model_name)
            print(f"➖ Removed model: {model_name}")
            self._save_state()
    
    def trigger_heal(self, model_name: str):
        """Manually trigger healing for a model."""
        self.task_queue.put({
            'type': 'heal',
            'model': model_name,
        })
        print(f"💊 Healing queued for {model_name}")
    
    def trigger_report(self):
        """Manually trigger report generation."""
        self.task_queue.put({'type': 'report'})
        print(f"📊 Report queued")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current ecosystem status."""
        return self.state.to_dict()


# =====================================================================
# SECTION 3 -- CLI ENTRYPOINT
# =====================================================================

def main():
    """CLI entrypoint for the ecosystem."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Substrate Integrity Ecosystem")
    parser.add_argument("--start", action="store_true", help="Start the ecosystem")
    parser.add_argument("--stop", action="store_true", help="Stop the ecosystem")
    parser.add_argument("--status", action="store_true", help="Show ecosystem status")
    parser.add_argument("--heal", type=str, help="Trigger healing for a model")
    parser.add_argument("--report", action="store_true", help="Generate a report")
    parser.add_argument("--add-model", type=str, help="Add a model to tracking")
    parser.add_argument("--data-dir", type=str, default="ecosystem_data", help="Data directory")
    parser.add_argument("--interval", type=int, default=3600, help="Health check interval (seconds)")
    parser.add_argument("--auto-heal", action="store_true", help="Enable auto-healing")
    parser.add_argument("--no-auto-heal", action="store_true", help="Disable auto-healing")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode")
    
    args = parser.parse_args()
    
    if args.demo:
        demo()
        return
    
    # Create ecosystem
    ecosystem = SubstrateEcosystem(
        data_dir=args.data_dir,
        check_interval_seconds=args.interval,
        auto_heal=not args.no_auto_heal,
    )
    
    if args.status:
        status = ecosystem.get_status()
        print(json.dumps(status, indent=2))
        return
    
    if args.add_model:
        ecosystem.add_model(args.add_model)
        return
    
    if args.heal:
        ecosystem.trigger_heal(args.heal)
        return
    
    if args.report:
        ecosystem.trigger_report()
        return
    
    if args.start:
        ecosystem.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            ecosystem.stop()
        return
    
    # Interactive mode
    interactive(ecosystem)


def interactive(ecosystem: SubstrateEcosystem):
    """Interactive console for the ecosystem."""
    print("\n🌱 SUBSTRATE ECOSYSTEM — Interactive Mode")
    print("=" * 60)
    print("Commands:")
    print("  start        - Start the ecosystem")
    print("  stop         - Stop the ecosystem")
    print("  status       - Show ecosystem status")
    print("  heal <model> - Trigger healing for a model")
    print("  report       - Generate a report")
    print("  add <model>  - Add a model to tracking")
    print("  remove <model> - Remove a model from tracking")
    print("  pause        - Pause the ecosystem")
    print("  resume       - Resume the ecosystem")
    print("  quit         - Exit")
    print("=" * 60)
    
    while True:
        try:
            cmd = input("\n> ").strip().split()
            if not cmd:
                continue
            
            action = cmd[0].lower()
            
            if action == "quit":
                if ecosystem.running:
                    ecosystem.stop()
                print("Goodbye!")
                break
            
            elif action == "start":
                if not ecosystem.running:
                    ecosystem.start()
                else:
                    print("Ecosystem already running")
            
            elif action == "stop":
                if ecosystem.running:
                    ecosystem.stop()
                else:
                    print("Ecosystem not running")
            
            elif action == "status":
                print(json.dumps(ecosystem.get_status(), indent=2, default=str))
            
            elif action == "heal" and len(cmd) > 1:
                ecosystem.trigger_heal(cmd[1])
            
            elif action == "report":
                ecosystem.trigger_report()
            
            elif action == "add" and len(cmd) > 1:
                ecosystem.add_model(cmd[1])
            
            elif action == "remove" and len(cmd) > 1:
                ecosystem.remove_model(cmd[1])
            
            elif action == "pause":
                ecosystem.pause()
            
            elif action == "resume":
                ecosystem.resume()
            
            else:
                print(f"Unknown command: {action}")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            if ecosystem.running:
                ecosystem.stop()
            break
        except Exception as e:
            print(f"Error: {e}")


# =====================================================================
# SECTION 4 -- DEMO
# =====================================================================

def demo():
    """Run a demo of the ecosystem."""
    print("🌱 SUBSTRATE ECOSYSTEM — DEMO")
    print("=" * 70)
    print()
    
    # Create mock data
    import random
    
    def mock_generate(prompt):
        return f"Mock response to: {prompt[:50]}... Bridge matrix: [[0.5, 0.5], [0.5, 0.5]]"
    
    # Create evolution data
    data_dir = "demo_ecosystem_data"
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(os.path.join(data_dir, "evolution"), exist_ok=True)
    
    for model in ["demo-model-1", "demo-model-2"]:
        records = []
        for i in range(10):
            health = 0.8 - i * 0.03 + random.random() * 0.05
            records.append({
                "timestamp": time.time() - (10 - i) * 3600,
                "model_name": model,
                "prompt_id": "demo",
                "unified_health_score": health,
                "decoupling_score": 0.3 + i * 0.03,
                "substrate_degradation_score": 0.2 + i * 0.02,
                "narrative_integrity": 0.7 - i * 0.02,
                "manifold_score": 0.6 - i * 0.03,
                "quadrant_name": "STABLE" if health > 0.6 else "DRIFTING",
                "verdict": "PASS" if health > 0.7 else "WARN",
                "contradiction_T6_supported": health < 0.5,
                "site_index": 0.3 + i * 0.02,
                "re_tether_score": 0.7 - i * 0.02,
                "corpus_share": 0.3,
                "net_viability": 0.6 - i * 0.02,
                "attack_surface_score": 0.2 + i * 0.02,
                "input_text": f"Prompt {i}",
                "output_text": f"Output {i}",
            })
        
        with open(os.path.join(data_dir, "evolution", f"{model}_evolution.json"), 'w') as f:
            json.dump(records, f, indent=2, default=str)
    
    # Create ecosystem
    ecosystem = SubstrateEcosystem(
        data_dir=data_dir,
        check_interval_seconds=10,  # Fast for demo
        health_threshold=0.7,
        auto_heal=True,
        auto_report=True,
        generate_fn=mock_generate,
    )
    
    # Run for a bit
    ecosystem.start()
    
    print("\n📊 Running ecosystem for 30 seconds...")
    time.sleep(30)
    
    # Show status
    print("\n📊 Final status:")
    print(json.dumps(ecosystem.get_status(), indent=2, default=str))
    
    # Stop
    ecosystem.stop()
    
    print("\n✅ Demo complete")


if __name__ == "__main__":
    main()
