# Theoretical Foundations

Theoretical frameworks and concepts underlying Primordio's design.

## Table of Contents
- [Dissipative Structures](#dissipative-structures)
- [Compositional Heredity](#compositional-heredity)
- [Chemical Selection Theory](#chemical-selection-theory)
- [Autocatalytic Sets](#autocatalytic-sets)
- [Evolutionary Game Theory](#evolutionary-game-theory)

## Dissipative Structures

### Prigogine's Theory (1977 Nobel Prize)

**Definition**: Self-organizing structures that maintain their organization by dissipating energy.

**Requirements**:
1. **Far from equilibrium**: Continuous energy input
2. **Nonlinear dynamics**: Feedback loops
3. **Openness**: Exchange matter/energy with environment
4. **Threshold conditions**: Minimum energy gradient

**In Primordio**:
- Energy input: Thermal convection (hot bottom → cold top)
- Nonlinearity: Vesicle growth is autocatalytic (bigger → absorb more → bigger)
- Openness: Monomers circulate through vesicles
- Threshold: Division only above size threshold

**Key Insight**: Life is not a static structure but a **process** maintained by energy flow. Primordio vesicles are dissipative structures - they organize monomers using thermal energy.

### Convection as Organizing Force

**Bénard Cells** (1900): When fluid heated from below exceeds critical temperature gradient, organized hexagonal convection cells spontaneously form.

**Primordio Analog**:
```
Without convection: Random Brownian → uniform distribution
With convection: Circulation cells → spatial structure
```

Convection creates:
- **Vertical stratification**: Hot/light molecules rise, cold/heavy sink
- **Horizontal circulation**: Return flow creates cells
- **Concentration gradients**: Different zones accumulate different chemicals
- **Periodic sampling**: Molecules cycle through different environments

This prevents equilibrium and enables exploration of chemical space.

## Compositional Heredity

### The Heredity Problem

**Classical view**: Heredity requires template replication (DNA/RNA)

**Problem**: How can heredity exist before genetic systems?

### Lipid World Solution (Segré et al., 2001)

**Compositional Inheritance**: Daughter vesicles inherit parent's molecular composition.

**Example**:
```
Parent vesicle: 60% type-A lipids, 40% type-B lipids
        ↓ Division
Child₁: 58% type-A, 42% type-B (slight variance)
Child₂: 62% type-A, 38% type-B (complementary variance)
```

Both children inherit approximately the parent's composition, even without templates.

### In Primordio

**Mechanism**:
```python
Parent has absorbed 100 monomers:
- 30 with high absorption_bias
- 40 with high repulsion_bias
- 30 with mixed biases

Division transfers 50 monomers to each daughter:
- Child₁: ~15 absorbers, ~20 defenders, ~15 mixed
- Child₂: ~15 absorbers, ~20 defenders, ~15 mixed
```

**Result**: Both daughters inherit parent's aggressive-defensive balance.

**Key insight**: Useful traits (chemical composition) transmitted to offspring without genetic code.

## Chemical Selection Theory

### Pre-Darwinian Evolution

Darwin's requirements work on chemicals:

**1. Variation**
- Monomers: Random bias scores (0-1)
- Vesicles: Different initial sizes (5-35 pixels)
- Compositions: Emergent from random absorption

**2. Heredity**
- Compositional inheritance (monomer transfer)
- ~50% variance between parent and children
- Enough similarity for lineages, enough variance for innovation

**3. Selection**
- Differential survival: Some vesicles die (absorbed)
- Differential reproduction: Division rate varies (division_bias)
- Resource competition: Limited monomer pool (5000)

### Fitness Landscapes

**Genotype Space** → **Compositional Space**

Instead of DNA sequences, we have:
```
Vesicle "genotype" = [absorption_bias_avg,
                      division_bias_avg,
                      attraction_bias_avg,
                      repulsion_bias_avg]
```

**Fitness Peaks**:
- **Predator peak**: High absorption, low repulsion
- **Tank peak**: Low absorption, high repulsion
- **Social peak**: High attraction, medium absorption
- **Reproducer peak**: High division, medium everything else

Different compositions have different fitness in different conditions.

### Frequency-Dependent Selection

**Classical natural selection**: Best strategy always wins.

**Frequency-dependent**: Best strategy depends on population composition.

**Example in Primordio**:
```
If population = 90% aggressive predators:
→ Being defensive (high repulsion) is valuable (rare strategy)

If population = 90% defensive tanks:
→ Being aggressive is valuable (easy targets)
```

This creates **Red Queen dynamics**: No single strategy dominates forever.

## Autocatalytic Sets

### Kauffman's Theory (1986)

**Autocatalytic Set**: A collection of molecules where each molecule's formation is catalyzed by another molecule in the set.

**Example**:
```
A catalyzes formation of B
B catalyzes formation of C
C catalyzes formation of A
→ Self-sustaining cycle
```

### Vesicle Analog

**Primordio's Implicit Autocatalysis**:

Vesicles don't explicitly catalyze reactions, but the growth-division cycle is self-reinforcing:

```
Large vesicle → Absorbs monomers → Grows larger → Divides
    ↑                                               ↓
    └──────────── Two medium vesicles ←────────────┘
```

The process produces more of itself (autocatalytic).

**Compositional Catalysis**:
- High absorption_bias monomers → Enable predation → Acquire more monomers
- High division_bias monomers → Faster reproduction → More copies of composition
- Positive feedback: Successful compositions produce more of themselves

### Emergence of Complexity

**Kauffman's Prediction**: At critical chemical diversity, autocatalytic sets spontaneously emerge.

**In Primordio**:
- 10 monomer types × 4 bias dimensions = 40-dimensional chemical space
- Sufficient diversity for emergent autocatalysis?
- Requires investigation (see EXPERIMENTS.md)

## Evolutionary Game Theory

### Strategies as Phenotypes

Each vesicle composition represents a strategy:

| Strategy | Bias Profile | Behavior |
|----------|-------------|----------|
| Hawk | High absorption, low repulsion | Aggressive, risky |
| Dove | Low absorption, high repulsion | Passive, safe |
| Bourgeois | Medium absorption, high division | Territorial, reproducer |
| Retaliator | Balanced all biases | Adaptive, flexible |

### Payoff Matrix

**Hawk vs Hawk**: Both fight, both injured (low fitness)
**Hawk vs Dove**: Hawk wins (high fitness Hawk, low fitness Dove)
**Dove vs Dove**: Share resources (medium fitness both)

**In Primordio**:
```
Predator vs Predator: Size contest, loser dies (high variance)
Predator vs Tank: Tank resists (medium fitness both)
Tank vs Tank: Ignore each other (medium fitness both)
```

### Evolutionary Stable Strategy (ESS)

**Definition**: Strategy that, if adopted by population, cannot be invaded by alternative strategy.

**Question for Primordio**: Does an ESS exist? Or is population always in flux?

**Hypothesis**: No pure ESS exists due to frequency-dependence. Instead, expect:
- Cycling dynamics (predator ↔ prey oscillations)
- Mixed equilibrium (multiple strategies coexist)
- Punctuated equilibrium (long stability, brief turnover)

## Implications for Abiogenesis

### 1. Life Doesn't Require Genes

**Conclusion**: Darwinian evolution can operate on chemical composition alone.

**Implication**: Genetic replication (DNA/RNA) was an **optimization** of an already-evolving system, not the origin.

### 2. Selection Can Drive Complexity

**Observation**: Simple initial vesicles → Diverse strategies emerge

**Mechanism**:
- Variation (random biases)
- Selection (differential success)
- Accumulation over generations

**Implication**: No "intelligent design" needed - selection alone drives organization.

### 3. Environment Shapes Evolution

**Observation**: Convection rate, temperature gradients, monomer density all affect outcomes.

**Implication**: Early Earth conditions (hydrothermal vents, tidal pools, volcanic areas) weren't just backdrop - they actively shaped which proto-life forms succeeded.

### 4. Cooperation Can Evolve Without Communication

**Observation**: High-attraction vesicles form clusters without signaling.

**Mechanism**: Emergent property of composition, not planned behavior.

**Implication**: Social behavior and cooperation may predate nervous systems, even chemical signaling.

## Falsifiable Predictions

Good theories make testable predictions:

**P1**: Higher convection rate → Faster evolutionary innovation
- Test: Run with different `buoyancy` values, measure strategy diversity over time

**P2**: Optimal vesicle density exists for evolution
- Test: Vary `vesicle_percentage`, find maximum diversity/stability ratio

**P3**: Increasing chemical diversity enables autocatalysis
- Test: Vary number of monomer types, look for threshold

**P4**: Frequency-dependent selection creates cycling
- Test: Track strategy frequencies over long runs, look for oscillations

**P5**: Spatial structure affects evolution
- Test: Compare with well-mixed version (no convection), measure diversity

See [EXPERIMENTS.md](EXPERIMENTS.md) for detailed protocols.

## Philosophical Implications

### What Is Life?

**Traditional definition**: Metabolism + Reproduction + Evolution

**Primordio vesicles have**:
- Metabolism: Selective absorption of monomers
- Reproduction: Division at threshold size
- Evolution: Compositional inheritance + selection

**Question**: Are they alive?

**Answer**: They exhibit **proto-life** - systems that have life-like properties but lack the full complexity of cellular life. They occupy the gray zone between chemistry and biology.

### Continuity Principle

**Strong version**: No sharp boundary between non-life and life. Evolution is gradual.

**Primordio supports this**: Vesicles show increasing life-like properties:
1. Self-assembly (chemical)
2. Growth (chemical)
3. Division (mechanical)
4. Heredity (compositional)
5. Selection (ecological)
6. Complexity (emergent)

No single step creates "life" - it's a continuum.

## Further Reading

**Dissipative Structures**:
- Prigogine, I. & Stengers, I. (1984) *Order Out of Chaos*

**Compositional Heredity**:
- Segré, D. et al. (2001) "The Lipid World"
- Lancet, D. et al. (2018) "Systems protobiology"

**Autocatalytic Sets**:
- Kauffman, S. (1993) *Origins of Order*
- Hordijk, W. & Steel, M. (2004) "Detecting autocatalytic, self-sustaining sets"

**Evolutionary Game Theory**:
- Maynard Smith, J. (1982) *Evolution and the Theory of Games*
- Nowak, M. (2006) *Evolutionary Dynamics*

**Origin of Life**:
- Lane, N. (2015) *The Vital Question*
- Deamer, D. (2019) *Assembling Life*

---

**Conclusion**: Primordio demonstrates that fundamental evolutionary principles (variation, heredity, selection) can operate on purely chemical systems. This supports the view that life emerged gradually through chemical evolution, with genetic systems evolving later as an optimization.
