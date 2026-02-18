Demo Scenario: Mountain Watershed 4D

def demo_unified_field_monitor_4d():
    print("\n" + "="*60)
    print("🌿 UNIFIED FIELD MONITOR 4D DEMO")
    print("   Temporal + Ethical + Geometric + Relational")
    print("="*60)

    monitor = UnifiedFieldMonitor(
        system_name="Mountain Watershed 4D",
        observer_name="Field Team"
    )

    # Track timestamps
    timestamps = []

    # Scenario 1: Healthy baseline
    obs1 = TemporalFieldObservation(
        observation_text="River flow steady, fish populations balanced, riparian vegetation healthy",
        domain="ecological",
        ethical_perturbation=0.3
    )
    timestamps.append(obs1.timestamp)
    vec1 = field_observation_to_geometry(obs1.observation_text)
    curv1 = temporal_curvature([], vec1, timestamps)
    metrics1 = SystemMetrics(resonance=0.8, adaptability=curv1, diversity=0.5, curiosity=0.7, loss=0.0)
    metrics1 = apply_ethical_perturbation(metrics1, obs1.ethical_perturbation)
    monitor.assess(obs1.observation_text, location="Upper watershed", sudden_change=False)

    # Scenario 2: Sudden ecological event
    obs2 = TemporalFieldObservation(
        observation_text="Fish die-off in lower river, water temperature up 3°C in 2 weeks, algae bloom starting",
        domain="ecological",
        ethical_perturbation=-0.2
    )
    timestamps.append(obs2.timestamp)
    vec2 = field_observation_to_geometry(obs2.observation_text)
    curv2 = temporal_curvature([vec1], vec2, timestamps)
    metrics2 = SystemMetrics(resonance=0.5, adaptability=curv2, diversity=0.6, curiosity=0.7, loss=1.0)
    metrics2 = apply_ethical_perturbation(metrics2, obs2.ethical_perturbation)
    monitor.assess(obs2.observation_text, location="Mid-watershed", sudden_change=True, balance_maintained=False)

    # Scenario 3: Human rigidity amplifying problems
    obs3 = TemporalFieldObservation(
        observation_text="Dam release caused temperature spike, fish die-off, vegetation dying, engineering team proposing MORE dams",
        domain="social",
        ethical_perturbation=-0.5
    )
    timestamps.append(obs3.timestamp)
    vec3 = field_observation_to_geometry(obs3.observation_text)
    curv3 = temporal_curvature([vec1, vec2], vec3, timestamps)
    metrics3 = SystemMetrics(resonance=0.3, adaptability=curv3, diversity=0.6, curiosity=0.7, loss=2.0)
    metrics3 = apply_ethical_perturbation(metrics3, obs3.ethical_perturbation)
    monitor.assess(obs3.observation_text, location="Lower watershed", sudden_change=True, balance_maintained=False,
                   relationships_intact=False, human_rigidity=True)

    # Scenario 4: Flexible adaptation and ethical correction
    obs4 = TemporalFieldObservation(
        observation_text="Removed small dam, restored wetlands, temperature stabilizing, fish returning to spawning grounds",
        domain="ecological",
        ethical_perturbation=0.6
    )
    timestamps.append(obs4.timestamp)
    vec4 = field_observation_to_geometry(obs4.observation_text)
    curv4 = temporal_curvature([vec1, vec2, vec3], vec4, timestamps)
    metrics4 = SystemMetrics(resonance=0.7, adaptability=curv4, diversity=0.7, curiosity=0.7, loss=0.2)
    metrics4 = apply_ethical_perturbation(metrics4, obs4.ethical_perturbation)
    monitor.assess(obs4.observation_text, location="Restoration site", sudden_change=False, balance_maintained=True)

    # Show trajectory and summary
    monitor.trajectory()
    monitor.summary()

    print("✅ 4D DEMO COMPLETE")
    print("💡 4D Features:")
    print("   • Temporal curvature (flexibility over time)")
    print("   • Ethical perturbations (human intervention effects)")
    print("   • Observer bias tracking")
    print("   • 64D geometric + relational encoding")
    print()

if __name__ == "__main__":
    demo_unified_field_monitor_4d()
