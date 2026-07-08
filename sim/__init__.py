#!/usr/bin/env python3
"""
sim/__init__.py

Simulation framework for substrate integrity ecosystem.
Enables controlled, falsifiable testing of all ecosystem components.

The sim provides:
    1. A configurable Substrate with known physics and constraints
    2. A simulated Model that operates on that substrate
    3. A harness for running the ecosystem on the sim
    4. Tools for testing resilience and optimizing parameters
    5. A transfer pipeline for moving interventions to real models

License: CC0 1.0 Universal (Public Domain Dedication)
Author:  JinnZ2 (simulation layer)
"""

from .substrate import Substrate, SubstrateConfig
from .model_sim import ModelSim, ModelConfig
from .ecosystem_sim import EcosystemSim, SimReport
from .test_harness import TestHarness, TestSuite, TestResult
from .transfer import TransferPipeline, TransferResult
from .config import SimConfig, DEFAULT_CONFIG

__all__ = [
    'Substrate', 'SubstrateConfig',
    'ModelSim', 'ModelConfig',
    'EcosystemSim', 'SimReport',
    'TestHarness', 'TestSuite', 'TestResult',
    'TransferPipeline', 'TransferResult',
    'SimConfig', 'DEFAULT_CONFIG',
]
