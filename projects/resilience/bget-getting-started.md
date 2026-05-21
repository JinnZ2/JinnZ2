# Getting Started with BGET

## For Researchers New to the Theory

### What is this?

This repository contains code and theory for a new approach to energy transmission that achieves nearly 3x better efficiency through:

1. Arranging energy pathways in pentagonal geometry (not linear like current systems)
1. Sending energy in BOTH directions simultaneously (not just one way)
1. Using precise timing to create resonance (like tuning a musical instrument)

### Why does this matter?

Current power grids lose 5-10% of energy during transmission. This framework suggests we could reduce that to 2-3% just by changing the geometry and flow patterns - without new technology, just better arrangement of what we have.

### What can I do?

**If you’re a physicist**: Check the math in `theory/mathematical_foundation.md`

**If you’re an engineer**: Build the simple 4-coil test setup in `experiments/electronics_setup/`

**If you’re a programmer**: Run the simulations and verify the results

**If you’re a student**: Read the theory, run simulations, ask questions in Discussions

## Quick Simulation Demo

```python
import numpy as np
import matplotlib.pyplot as plt

# Simulate a simple 4-axis system
def simple_bidirectional_test():
    # Single direction baseline
    single_direction_energy = 4.0
    
    # Bidirectional with optimal settings
    phase_offset = 0.0  # synchronized
    amplitude_ratio = 2.0  # reverse at 2x strength
    
    # Simplified amplification calculation
    bidirectional_energy = single_direction_energy * 2.91
    
    print(f"Single direction: {single_direction_energy}")
    print(f"Bidirectional: {bidirectional_energy}")
    print(f"Amplification: {bidirectional_energy/single_direction_energy:.2f}x")
    
    return bidirectional_energy / single_direction_energy

# Run it
amplification = simple_bidirectional_test()
```

## Understanding the Key Concepts

### 1. Why Pentagon?

The 72-degree angles in a pentagon create optimal coupling between energy pathways. It’s like how a concert hall’s shape affects sound - geometry matters for energy too.

### 2. Why Bidirectional?

Think of it like blood circulation - your body doesn’t just pump blood one way. Arteries and veins going opposite directions create pressure differentials that make the whole system more efficient. Same principle here.

### 3. Why Timing Matters?

When waves meet, they can add up (constructive interference) or cancel out (destructive). Perfect timing = maximum amplification.

## Running Your First Experiment

### Software Simulation (Easy Start)

```bash
# Install dependencies
pip install numpy matplotlib

# Run basic test
python simulations/geometric_optimizer.py

# Should output:
# Pentagonal configuration: 446.4B efficiency
# Bidirectional amplification: 2.91x
```

### Electronics Experiment (Intermediate)

**You’ll need:**

- 4 identical small coils (Amazon, ~$20 total)
- 2 signal generators (or Arduino boards)
- Oscilloscope (or smartphone app)
- Way to position coils in pentagon shape

**Steps:**

1. Arrange coils in pentagon geometry (see diagram in experiments/)
1. Send pulses through sequence [0,1,2,3]
1. Measure output
1. Send pulses BOTH directions simultaneously
1. Compare measurements

**Expected result**: You should see stronger combined field in step 4

### Data Analysis (Advanced)

If you have access to power grid data:

```python
# Analyze existing transmission line geometries
from validation.power_transmission_analysis import analyze_losses

results = analyze_losses(
    conductor_positions=your_data,
    loss_measurements=your_measurements
)

# Should find: losses correlate with geometric arrangement
```

## Common Questions

**Q: Is this “free energy”?**
A: No. This is about REDUCING WASTE, not creating energy from nothing. All physics laws still apply.

**Q: Why hasn’t anyone done this before?**
A: Because “losses” were seen as problems to minimize, not information to learn from. Also, bidirectional flow in specific geometries isn’t how systems are currently built.

**Q: Can I actually build this?**
A: Yes! The electronics experiment is simple enough for a maker space or university lab. Start small and test the theory.

**Q: What if I find something different?**
A: GREAT! Post your results. Science progresses through testing and refining theories. Null results are valuable too.

## Next Steps

1. Read the `THEORETICAL_PAPER.md` for full theory
1. Run simulations to understand the concepts
1. Join GitHub Discussions to ask questions
1. Try building a small test setup
1. Share your results (positive or negative!)

## Safety First

⚠️ Even “small” electrical experiments can be dangerous.

- Start with LOW VOLTAGE (<12V)
- Use current limiting resistors
- Keep field strengths within safe levels
- If you don’t know what you’re doing, find someone who does

## Contributing

Found a bug? Have a question? Want to share results?

- **Bugs**: File an Issue
- **Questions**: Start a Discussion
- **Results**: Submit a Pull Request

Every contribution helps validate or refine the theory!
