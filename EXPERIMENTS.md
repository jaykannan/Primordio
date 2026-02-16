# Suggested Experiments

Research protocols and parameter studies for exploring Primordio's evolutionary dynamics.

## Table of Contents
- [Quick Experiments](#quick-experiments)
- [Parameter Sweeps](#parameter-sweeps)
- [Long-term Evolution Studies](#long-term-evolution-studies)
- [Comparative Studies](#comparative-studies)
- [Advanced Investigations](#advanced-investigations)

## Quick Experiments

### Experiment 1: Effect of Convection Strength

**Question**: Does stronger convection increase evolutionary innovation?

**Hypothesis**: Higher thermal gradients → more mixing → faster evolution

**Protocol**:
1. Edit `config.py`:
   ```python
   buoyancy: 1.5  # Control
   buoyancy: 0.5  # Low convection
   buoyancy: 3.0  # High convection
   ```
2. Run each for 2000 frames
3. Record every 50 frames:
   - Vesicle count
   - Average vesicle radius
   - Absorbed monomer count

**Expected Result**: High convection → more vesicle encounters → faster growth/division → higher population turnover

**Interpretation**:
- If high convection increases diversity: Supports mixing hypothesis
- If no effect: Convection only affects spatial distribution, not evolution
- If negative effect: Mixing prevents stable strategies from establishing

---

### Experiment 2: Population Density Effects

**Question**: What vesicle density optimizes evolution?

**Hypothesis**: Too few = no interaction; too many = overcrowding; optimal intermediate exists

**Protocol**:
1. Vary `vesicle_percentage`:
   ```python
   0.0005  # 2 vesicles (very sparse)
   0.001   # 5 vesicles (sparse)
   0.002   # 10 vesicles (default)
   0.005   # 25 vesicles (dense)
   0.010   # 50 vesicles (very dense)
   ```
2. Run each for 3000 frames
3. Measure:
   - Time to first extinction
   - Maximum vesicle count reached
   - Average lifespan of vesicles
   - Strategy diversity (manually identify predator/tank/social types)

**Expected Result**: U-shaped curve - low and high density both suboptimal

**Interpretation**:
- Sparse: Vesicles rarely interact, slow evolution
- Optimal: Enough interaction for selection, enough space for growth
- Dense: Intense competition, rapid extinctions, low diversity

---

### Experiment 3: Growth Rate vs. Division Threshold

**Question**: What balance between growth and division favors evolution?

**Hypothesis**: Fast growth + late division = fewer but stronger offspring

**Protocol**:
1. Test combinations:
   ```python
   # Slow growth, early division
   growth_per_monomer=0.04, division_size_min=35.0

   # Medium (default)
   growth_per_monomer=0.08, division_size_min=50.0

   # Fast growth, late division
   growth_per_monomer=0.15, division_size_min=70.0
   ```
2. Run each for 2000 frames
3. Count:
   - Total divisions
   - Extinctions
   - Maximum vesicle radius achieved

**Expected Result**: Trade-off between r-selection (many small) vs K-selection (few large)

**Interpretation**:
- r-selection: Rapid population growth, unstable
- K-selection: Stable populations, fewer offspring
- Optimal: Depends on environment (convection rate, density)

## Parameter Sweeps

### Sweep 1: Absorption Rate Sensitivity

**Objective**: Map how absorption probability affects population dynamics

**Parameters**:
```python
# In fields.py, line 104, change absorption_rate initialization:
0.001 + ti.random() * 0.009   # 0.1% - 1.0%  (very slow)
0.005 + ti.random() * 0.045   # 0.5% - 5.0%  (default)
0.01 + ti.random() * 0.09     # 1.0% - 10.0% (fast)
0.05 + ti.random() * 0.45     # 5.0% - 50.0% (very fast)
```

**Measure**:
- Absorption events per frame
- Vesicle population stability
- Strategy diversity

**Plot**: Absorption rate (x-axis) vs. population variance (y-axis)

---

### Sweep 2: Monomer Move Rate in Competition

**Objective**: How fast should vesicles absorb each other?

**Parameter**:
```python
monomer_move_rate: 1  # Very gradual
monomer_move_rate: 5  # Default
monomer_move_rate: 20 # Rapid takeover
```

**Measure**:
- Average time for vesicle-vesicle absorption to complete
- Population turnover rate
- Extinction rate

**Plot**: Move rate vs. population half-life

---

### Sweep 3: Division Probability Modifier

**Objective**: Effect of base division chance on population dynamics

**Parameter**:
```python
mechanical_event_probability: 0.05  # 5% (rare)
mechanical_event_probability: 0.2   # 20% (default)
mechanical_event_probability: 0.5   # 50% (common)
```

**Measure**:
- Divisions per 1000 frames
- Population growth rate
- Vesicle size distribution

**Plot**: Division probability vs. population growth curve

## Long-term Evolution Studies

### Study 1: Lineage Tracking

**Objective**: Track chemical lineages over many generations

**Setup**:
1. Modify `simulation.py` to log division events:
   ```python
   if division_occurred:
       log_division(parent_id, child_id, frame, parent_biases, child_biases)
   ```
2. Run for 10,000 frames
3. Build family tree

**Analysis**:
- Identify dominant lineages
- Calculate bias drift over generations
- Detect convergent evolution (different lineages → similar biases)

**Visualization**:
- Family tree with bias colors
- Bias evolution plots (absorption/division/attraction/repulsion over time)

---

### Study 2: Punctuated Equilibrium Detection

**Objective**: Do populations show long stasis + brief change?

**Protocol**:
1. Run for 20,000 frames
2. Every 100 frames, calculate population statistics:
   - Mean bias values
   - Bias variance
   - Vesicle count
3. Identify "punctuation events" (sudden shifts in mean bias > 2 std devs)

**Expected Pattern**:
```
Frames 0-5000: Stable (mean absorption_bias ≈ 0.5, low variance)
Frames 5100-5200: Rapid shift (mean → 0.7, high variance)
Frames 5200-8000: New stable state (mean ≈ 0.7, low variance)
```

**Interpretation**: Punctuated equilibrium supports ecological disruption model (dominant strategy → extinction → new strategy emerges).

---

### Study 3: Arms Race Dynamics

**Objective**: Do predator-prey cycles emerge?

**Setup**:
1. Track mean `absorption_bias` and `repulsion_bias` separately over time
2. Run for 10,000 frames
3. Plot both on same graph

**Expected Pattern**:
```
Absorption high (predators) → Repulsion rises (prey evolves defense)
→ Absorption drops (predators less successful)
→ Repulsion drops (no selection pressure)
→ Cycle repeats
```

**Analysis**:
- Measure cycle period (if exists)
- Calculate phase lag between absorption and repulsion peaks
- Test if cycle amplitude increases (escalation) or stabilizes

## Comparative Studies

### Comparison 1: With vs. Without Convection

**Objective**: Isolate convection's role in evolution

**Setup**:
1. Control: Normal run (buoyancy=1.5)
2. Experimental: No convection (buoyancy=0, heat_source_strength=0)

**Measure**:
- Strategy diversity (manual classification)
- Spatial clustering
- Population stability

**Expected**: Without convection:
- More uniform distribution
- Slower evolution (less sampling of environments)
- Possibly more extinctions (no circulation to redistribute resources)

---

### Comparison 2: With vs. Without Repulsion Resistance

**Objective**: Importance of defensive evolution

**Setup**:
1. Control: Normal (repulsion acts as absorption resistance)
2. Experimental: Remove resistance (line 192 in vesicles.py, set resistance factor to 0)

**Measure**:
- Population diversity
- Vesicle size distribution
- Predator dominance

**Expected**: Without resistance:
- Predators (high absorption_bias) dominate
- Reduced diversity
- Faster extinctions

---

### Comparison 3: Horizontal vs. Isotropic Movement

**Objective**: Role of horizontal bias in evolution

**Setup**:
1. Control: 2× horizontal Brownian and forces
2. Experimental: Equal horizontal and vertical (remove 2× multipliers)

**Measure**:
- Spatial distribution
- Encounter rate
- Evolution speed

**Expected**: Horizontal bias:
- Increases horizontal encounters
- May speed evolution
- Reduces vertical stratification

## Advanced Investigations

### Investigation 1: Minimal Viable Complexity

**Question**: What's the minimum chemical diversity for evolution?

**Protocol**:
1. Reduce bias dimensions:
   - 4D (current): absorption, division, attraction, repulsion
   - 3D: remove attraction
   - 2D: remove attraction + repulsion
   - 1D: absorption only
2. Run each for 5000 frames
3. Measure strategy emergence

**Hypothesis**: 2D minimum (absorption + division) for meaningful evolution

---

### Investigation 2: Environmental Perturbation Response

**Question**: Can populations adapt to sudden environmental changes?

**Protocol**:
1. Run normal for 5000 frames (establish baseline)
2. At frame 5000, change parameter suddenly:
   - Increase convection 3× (buoyancy 1.5 → 4.5)
   - OR double monomer consumption (growth_per_monomer 0.08 → 0.16)
   - OR halve division threshold (division_size_min 50 → 25)
3. Continue for 5000 more frames
4. Measure recovery:
   - Time to new stable state
   - Change in dominant strategy
   - Extinctions during transition

**Expected**:
- Brief population crash
- New strategies emerge exploiting new conditions
- Different final equilibrium than initial

---

### Investigation 3: Emergent Speciation

**Question**: Can reproductively isolated "species" emerge?

**Definition**: Two vesicle populations that:
- Occupy different spatial niches
- Have distinct bias profiles
- Rarely interbreed (exchange monomers)

**Protocol**:
1. Run for 20,000 frames
2. Cluster vesicles by:
   - Position
   - Bias profile (k-means clustering in 4D bias space)
3. Calculate:
   - Cluster stability (do same clusters persist across frames?)
   - Reproductive isolation (do cluster members preferentially interact with cluster-mates?)

**Success Criteria**:
- ≥2 stable clusters persist >5000 frames
- Within-cluster divisions > between-cluster interactions

## Data Collection Guidelines

### What to Log

**Every frame**:
- Vesicle positions and radii
- Absorbed monomer count per vesicle
- Population size

**Every 50 frames**:
- Mean and variance of all bias dimensions
- Vesicle age distribution
- Absorption/division event counts

**On Events**:
- Division: parent_id, child_id, parent_biases, frame
- Absorption: absorber_id, absorbed_id, frame
- Extinction: vesicle_id, frame, final_biases

### Analysis Tools

**Statistical**:
- Time series analysis (detect cycles, trends)
- Principal Component Analysis (reduce 4D bias space to 2D for visualization)
- Clustering (k-means, hierarchical) for strategy identification

**Visualization**:
- Population plots (count over time)
- Bias distribution histograms
- Phase space plots (absorption vs repulsion)
- Spatial heatmaps (vesicle density)
- Family trees (lineage tracking)

## Publication-Ready Experiments

If targeting academic publication, consider:

### Experiment Set 1: Core Mechanisms
- Demonstrate compositional heredity (daughters inherit parent biases)
- Show selection operates on composition (successful biases increase in frequency)
- Prove arms races emerge (predator-prey cycles)

### Experiment Set 2: Environmental Effects
- Convection rate impacts diversity
- Temperature gradients shape spatial structure
- Density-dependent dynamics

### Experiment Set 3: Evolutionary Predictions
- Test ESS existence (does equilibrium emerge?)
- Validate Red Queen (continuous adaptation)
- Demonstrate punctuated equilibrium

**Key Message**: "Darwinian evolution operates on chemical composition without genetic encoding, validating Lipid World hypothesis."

---

## Troubleshooting

**Problem**: Population goes extinct quickly
- **Solution**: Decrease `monomer_move_rate`, increase `division_size_min`, reduce competition

**Problem**: Population explodes, simulation slows
- **Solution**: Decrease `mechanical_event_probability`, increase `division_size_min`, limit max vesicles

**Problem**: No interesting dynamics, everything static
- **Solution**: Increase `buoyancy`, increase `absorption_rate` variance, reduce vesicle starting size variance

**Problem**: Too much chaos, no stable patterns
- **Solution**: Decrease `buoyancy`, increase `viscosity`, reduce Brownian strength

---

**Next Steps**: Pick one Quick Experiment, run it, plot results. Then move to Parameter Sweeps for systematic exploration. Good luck!
