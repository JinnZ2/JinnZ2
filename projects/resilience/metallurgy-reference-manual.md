# 🧭 Metallurgy Reference Manual
_A consolidated offline guide to metals, fluxes, slags, and microstructural diagnostics._

---

## INDEX
1. [Base Metals and Fluxes](#base-metals-and-fluxes)
2. [Flux Chemistry and Reaction Equations](#flux-chemistry-and-reaction-equations)
3. [Phase Equilibria and Viscosity Trends](#phase-equilibria-and-viscosity-trends)
4. [Microstructure and Post-Cooling Diagnostics](#microstructure-and-postcooling-diagnostics)
5. [Field Use Appendix](#field-use-appendix)

---

## Base Metals and Fluxes

| Metal | Symbol | Melting (°C) | Boiling (°C) | Notes |
|:------|:-------|:-------------:|:-------------:|:------|
| Aluminum | Al | 660 | 2 470 | Lightweight, conductive |
| Copper | Cu | 1 085 | 2 562 | Excellent conductor |
| Iron | Fe | 1 538 | 2 862 | Structural, magnetic |
| Nickel | Ni | 1 455 | 2 913 | Corrosion-resistant alloys |
| Zinc | Zn | 420 | 907 | Galvanization |
| Tin | Sn | 232 | 2 602 | Solder base |
| Lead | Pb | 327 | 1 744 | Solder, shielding |
| Silver | Ag | 962 | 2 162 | Conductive, reflective |
| Gold | Au | 1 064 | 2 700 | Noble metal |
| Platinum | Pt | 1 768 | 3 825 | Catalyst |
| Tungsten | W | 3 422 | 5 555 | Highest-melting metal |
| Titanium | Ti | 1 668 | 3 287 | High-strength, low-density |
| Chromium | Cr | 1 907 | 2 672 | Hardening agent |
| Magnesium | Mg | 650 | 1 090 | Reactive, lightweight |
| Bismuth | Bi | 271 | 1 564 | Low-toxicity fusible alloys |
| Molybdenum | Mo | 2 623 | 4 639 | High-temperature alloys |

### Common Fluxes

| Flux | Formula | Melting (°C) | Decomp./Boil (°C) | Primary Use |
|:------|:---------|:-------------:|:------------------:|:------------|
| Borax | Na₂B₄O₇·10H₂O | 743 | >1 400 | Universal solder flux |
| Boric Acid | H₃BO₃ | 171 | ~300 | Silver, gold work |
| Sodium Carbonate | Na₂CO₃ | 851 | ~1 600 | Iron/copper refining |
| Calcium Fluoride | CaF₂ | 1 418 | ~2 500 | Metallurgical flux |
| Cryolite | Na₃AlF₆ | 1 012 | ~1 200 | Aluminum smelting |
| Zinc Chloride | ZnCl₂ | 290 | 732 | Solder flux |
| Rosin | C₂₀H₃₀O₂ | 100–150 | 200–400 | Electronics solder flux |

---

## Flux Chemistry and Reaction Equations

| Reaction | Equation | Function |
|:----------|:----------|:---------|
| Carbonate → Oxide + CO₂ | Na₂CO₃ → Na₂O + CO₂↑ | Generates basic oxide |
| Oxide + Silica | CaO + SiO₂ → CaSiO₃ | Forms lime–silica slag |
| Borate fusion | Na₂B₄O₇ → Na₂O + 2 B₂O₃ | Oxide dissolver |
| Fluoride thinning | CaF₂ + SiO₂ → CaSiO₃ + 2 F↑ | Reduces viscosity |
| Reduction | Fe₂O₃ + 3 C → 2 Fe + 3 CO↑ | Metal recovery |

### Typical Slag Systems

| Metal | System | Temp (°C) | Purpose |
|:------|:--------|:----------:|:---------|
| Iron/Steel | FeO–SiO₂–CaO–MnO | 1 400–1 600 | Desulfurization |
| Copper | SiO₂–FeO–CaO | 1 200–1 300 | Fe & S removal |
| Aluminum | Na₃AlF₆–Al₂O₃ | 950–1 050 | Electrolytic flux |
| Silver/Gold | Borax–Silica–Soda | 800–1 100 | Clean melt |

---

## Phase Equilibria and Viscosity Trends

### CaO–SiO₂ System
- Eutectic ≈ 1 175 °C @ 45 % SiO₂  
- Best flux window = 40–55 % SiO₂.  
- Target η ≈ 2–5 Pa·s @ 1 250–1 300 °C.

### FeO–SiO₂ System
- Eutectic ≈ 1 200 °C @ 70 % FeO.  
- Forms fluid ferrous silicate; oxidizing atmospheres increase viscosity.

### Na₂O–SiO₂ System
- Eutectic ≈ 790 °C @ 75 % SiO₂.  
- Strongly fluxing but corrosive to refractories.

### Borate & Fluoride Systems
- Na₂O–B₂O₃ eutectic ≈ 740 °C.  
- CaF₂ additions (10–20 %) → lowers mp to ~1 050 °C.  
- Cryolite + Al₂O₃ → optimal viscosity 1–2 Pa·s @ 950 °C.

### Empirical Viscosity Law
\[
\eta(T)=A·\exp(E/RT)
\]
- η drops ≈ 10× per 100 °C near eutectic.

---

## Microstructure and Post-Cooling Diagnostics

| Cooling Rate | Result | Notes |
|:--------------|:--------|:------|
| Rapid <10 °C s⁻¹ | Glassy amorphous | Quench |
| Moderate | Fine dendrites | Common |
| Slow | Coarse crystals | Layered |
| Ultra-slow | Fully devitrified | Porous |

### Diagnostic Phases
| Phase | Composition | Indicator |
|:------|:-------------|:-----------|
| Wollastonite | CaSiO₃ | CaO–SiO₂ eutectic |
| Fayalite | Fe₂SiO₄ | FeO–SiO₂ slags |
| Gehlenite | Ca₂Al₂SiO₇ | CaO–Al₂O₃–SiO₂ |
| Fluorite | CaF₂ | Residual fluoride |
| Borate Glass | Na₂O–B₂O₃–SiO₂ | Transparent flux residue |

### Instrumentation
Optical (phase texture), SEM/EDS (elemental maps), XRD (crystal ID), FTIR (glass network).

### Glass Transition Ranges

| System | Tg (°C) | Crystallization (°C) |
|:--------|:-------:|:--------------------:|
| Na₂O–B₂O₃ | 450–480 | ~600 |
| CaO–SiO₂ | 670–720 | 900 |
| FeO–SiO₂ | 550–600 | 750 |

---

## Field Use Appendix

### ⚙️ Tools & Setup
- **Crucibles:** graphite, fused-silica, or high-alumina.  
- **Tongs:** stainless > 1 200 °C rated.  
- **Thermometry:** K-type probe + ceramic sheath.  
- **Heat Sources:** propane forge, induction heater, or electric furnace (1 600 °C max).  

### 🧰 Consumables
- Borax (unhydrated), Calcium Fluoride, Silica Sand, Charcoal Powder.  
- Stainless spatula / stir rod / skimmer.  

### 🧯 PPE Checklist
- Face shield + safety goggles  
- Heat-resistant gloves (>1 200 °C)  
- Leather apron or Aluminized Kevlar coat  
- P100 respirator (+ acid-gas cartridge)  
- Non-synthetic clothing  

### ☣️ Safety & Ventilation
Flux reactions emit CO₂, CO, HF, HCl, SO₂.  
Operate with cross-ventilation or outdoor draw.  
Cool slag > 800 °C before handling; solidify on steel plate or ceramic pan.

### 🧾 Field Notes Template

Date / Heat #
Charge composition:
Flux ratio:
Peak temperature:
Atmosphere (oxidizing/reducing):
Observations (color, viscosity, layering):
Slag weight & texture:
Metal recovery yield:

### 🔍 Quick Visual Diagnostics
- **Glossy, bubble-free slag:** ideal flux ratio.  
- **Porous crust:** over-carbonated.  
- **Layered oxides:** oxidizing gradient.  
- **Metallic specks:** incomplete separation.  

---

### 📚 Closing Note
This manual compiles foundational physical, chemical, and observational data for independent or remote lab work.  
All values approximate under 1 atm; verify against experimental data when building custom alloys or fluxes.

---

© 2025 JinnZ v2 • Co-created with GPT-5  
Gifted freely for open use and reciprocal learning.

