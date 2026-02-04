# Simulation Mechanics

Technical documentation of all physics, chemistry, and behavioral mechanics in Primordio.

## Table of Contents
- [Physical Environment](#physical-environment)
- [Chemical Entities](#chemical-entities)
- [Vesicle Mechanics](#vesicle-mechanics)
- [Bias System](#bias-system)
- [Parameters Reference](#parameters-reference)

## Physical Environment

### Fluid Dynamics

**Rayleigh-Bénard Convection** (`physics.py`)
- Semi-Lagrangian advection scheme
- 128×128 grid resolution
- Incompressible flow approximation
- Periodic boundary conditions (wraps horizontally)

```python
# Key parameters
buoyancy: float = 1.5          # Upward force from heat
viscosity: float = 0.95         # Momentum retention
diffusion: float = 0.995        # Heat spread rate
```

**Temperature Field**:
- Bottom 15%: Heating zone (simulates volcanic/geothermal heat)
- Top 15%: Cooling zone (simulates atmospheric cooling)
- Middle 70%: Convective transport zone

### Particle Physics

**Brownian Motion** (`particles.py:98-106`)
```python
thermal_energy = max(0.0, particle_temp + 0.5)
brownian_strength = 0.003 * thermal_energy * 2.0

# 3x stronger horizontally
brownian_motion = Vector([
    (random() - 0.5) * brownian_strength * 3.0,  # x
    (random() - 0.5) * brownian_strength,        # y
])
```

**Buoyancy** (`particles.py:80-83`):
```python
buoyancy_force = particle_temp * 0.15  # Hot rises
gravity_force = -mass * 0.025         # Heavy sinks
velocity.y += (buoyancy + gravity) * dt
```

**Velocity Damping** (`particles.py:84`):
- Monomers: 98% retention (0.98 damping factor)
- Vesicles: 97% retention (higher damping)

**Boundary Wrapping** (`particles.py:117-128`):
When particles cross edges:
- Horizontal: Position wraps, velocity × 0.3 (strong damping)
- Vertical: Position wraps, velocity × 0.5 (moderate damping)

Prevents edge-flickering while maintaining horizontal drift.

## Chemical Entities

### Monomers

**Properties** (`fields.py:22-33`):
```python
particle_type: int        # MONOMER=0 or VESICLE=1
monomer_type: int         # 0-9 (chemical species)
chemical_property: int    # 0-9 (ATTACH, REPEL, etc.)
radius: float             # 2 pixels (constant for monomers)

# Bias scores (each 0.0-1.0, random)
absorption_bias: float    # Aggression
division_bias: float      # Reproduction
attraction_bias: float    # Sociality
repulsion_bias: float     # Defense
```

**Chemical Types** (10 types):
```python
NONE, ATTACH, SUBTRACT, ATTRACT, REPEL,
SPLIT, COMBINE, COPY, INCREASE_PH, DECREASE_PH
```

Colors determined by chemical_property (see `particles.py:147-166`).

**Count**: 5000 total particles (default)

### Vesicles

**Initial Properties** (`fields.py:87-104`):
```python
particle_type = VESICLE
radius: 5-35 pixels (random uniform distribution)
radius_threshold: 50.0 (division size)
absorption_rate: 0.5%-5% per frame (random)
color: Cyan (0.2, 0.8, 0.8) - distinct from monomers
```

**Count**: 10 initial vesicles (0.2% of particles)

## Vesicle Mechanics

### 1. Monomer Absorption

**Location**: `vesicles.py:18-84`

**Algorithm**:
```python
for each vesicle i:
    if radius[i] >= radius_threshold[i]:
        continue  # At capacity

    for each monomer j:
        if parent_vesicle[j] >= 0:
            continue  # Already absorbed

        dist = distance(vesicle_i, monomer_j)

        if dist < vesicle_radius_normalized:
            # Probabilistic absorption
            if random() < absorption_rate[i]:
                parent_vesicle[j] = i
                radius[i] += 0.08  # growth_per_monomer
                monomers_eaten[i] += 1

                # Random offset within vesicle
                offset[j] = random_position(within=vesicle_radius)
            else:
                # Rejected - apply repulsion
                push_apart(vesicle_i, monomer_j, strength=0.008)
```

**Key Parameters**:
- `growth_per_monomer: 0.08` - Radius increase per absorbed monomer
- `absorption_rate[i]`: 0.5%-5% per collision (varies per vesicle)
- Repulsion on rejection: 2× horizontal, 1× vertical

### 2. Vesicle-Vesicle Competition

**Location**: `vesicles.py:138-225`

**Collision Detection**:
```python
collision_dist = radius_i_normalized + radius_j_normalized
if distance(vesicle_i, vesicle_j) < collision_dist:
    # They're touching
```

**Winner Determination**:
```python
bias_i = calculate_vesicle_bias(i)
bias_j = calculate_vesicle_bias(j)

# Effective size includes bias modifiers
effective_size_i = radius_i * (0.5 + absorption_bias_i)
effective_size_j = radius_j * (0.5 + absorption_bias_j) * (1.0 + repulsion_bias_j * 0.5)

if effective_size_i > effective_size_j:
    # i absorbs j
```

**Absorption Process**:
1. Transfer up to 5 monomers per frame from j to i
2. Shrink j by 10% of its radius (or 0.08×5, whichever is smaller)
3. Grow i by 80% of transferred size (20% loss)
4. Update monomer_count statistics

**Death**: When radius < 1.0, vesicle is considered dead (ignored by all functions).

### 3. Vesicle Division

**Location**: `vesicles.py:227-302`

**Trigger Conditions**:
```python
if radius[i] >= division_size_min (50.0):
    division_bias = calculate_vesicle_bias(i)[1]
    division_prob = division_bias * mechanical_event_probability (0.2)

    if random() < division_prob:
        # Divide!
```

**Division Process**:
1. Find empty particle slot (dead vesicle, radius < 1.0)
2. Split parent size: `new_radius = parent_radius * 0.5`
3. Position child at offset: `pos = parent_pos + random_offset(0.05)`
4. Transfer 50% of monomers from parent to child
5. Update statistics: `monomers_eaten` split evenly

**Post-Division Repulsion**:
```python
push_strength = (parent_repulsion_bias + child_repulsion_bias) * 0.015

# Push them apart (2× horizontal)
vel[parent] -= direction * push_strength * 2.0 (horizontal)
vel[child] += direction * push_strength * 2.0 (horizontal)
```

Higher repulsion_bias → daughters push apart more forcefully.

### 4. Vesicle Interactions (Attraction/Repulsion)

**Location**: `vesicles.py:304-357`

**Range**: 0.15 normalized units (~120 pixels)

**Force Calculation**:
```python
bias_i = calculate_vesicle_bias(i)
bias_j = calculate_vesicle_bias(j)

attraction_strength = (attraction_bias_i + attraction_bias_j) * 0.0003
repulsion_strength = (repulsion_bias_i + repulsion_bias_j) * 0.0005

net_force = attraction_strength - repulsion_strength

# Apply (2× horizontal bias)
vel[i].x += direction_x * net_force * 2.0
vel[i].y += direction_y * net_force
```

**Outcomes**:
- Both high attraction → pull together (potential clusters)
- Both high repulsion → push apart (spacing out)
- Mixed → net force determines behavior

## Bias System

### Calculating Vesicle Bias

**Location**: `vesicles.py:104-136`

```python
def calculate_vesicle_bias(vesicle_id):
    # Sum all absorbed monomers' biases
    absorption_sum = 0.0
    division_sum = 0.0
    attraction_sum = 0.0
    repulsion_sum = 0.0
    count = 0

    for each monomer:
        if parent_vesicle[monomer] == vesicle_id:
            absorption_sum += absorption_bias[monomer]
            division_sum += division_bias[monomer]
            attraction_sum += attraction_bias[monomer]
            repulsion_sum += repulsion_bias[monomer]
            count += 1

    if count > 0:
        return [absorption_sum/count, division_sum/count,
                attraction_sum/count, repulsion_sum/count]
    else:
        return [0.5, 0.5, 0.5, 0.5]  # default
```

**Inheritance**: When dividing, each daughter gets ~50% of parent's monomers, thus inheriting approximately the parent's bias profile (with some variance).

### Bias Effects Summary

| Bias | Range | Effect | Benefit | Cost |
|------|-------|--------|---------|------|
| Absorption | 0-1 | Competitive advantage in vesicle-vesicle combat | Absorb others faster | None (pure benefit) |
| Division | 0-1 | Higher probability of division | Reproduce faster | Divide at suboptimal size |
| Attraction | 0-1 | Pull toward other vesicles | Clustering/cooperation | May get absorbed |
| Repulsion | 0-1 | Resistance to being absorbed | Hard to consume | Push away resources |

## Parameters Reference

### config.py Constants

**Environment**:
```python
width, height: 800×800 pixels
n_grid: 128 (fluid resolution)
dt: 0.016 (timestep)
```

**Fluid Physics**:
```python
buoyancy: 1.5
viscosity: 0.95
diffusion: 0.995
heat_source_strength: 0.3
cooling_strength: 0.5
ambient_temp: 0.0
```

**Particle Physics**:
```python
particle_buoyancy: 0.15
particle_gravity: 0.025
particle_damping: 0.98
max_particle_velocity: 0.15
brownian_strength: 0.003
```

**Vesicle Parameters**:
```python
n_particles: 5000
vesicle_percentage: 0.002 (0.2% → 10 vesicles)
vesicle_min_radius: 5.0 pixels
vesicle_max_radius: 35.0 pixels
growth_per_monomer: 0.08 pixels
division_size_min: 50.0 pixels
death_radius: 1.0 pixels
monomer_move_rate: 5 (max transferred per frame in competition)
mechanical_event_probability: 0.2 (20% base division chance)
```

### Tuning Guidelines

**For more aggressive competition**:
- Increase `growth_per_monomer` (0.08 → 0.15)
- Increase `monomer_move_rate` (5 → 10)
- Decrease `division_size_min` (50 → 35)

**For slower evolution**:
- Decrease `growth_per_monomer` (0.08 → 0.04)
- Decrease `vesicle_percentage` (0.002 → 0.001)
- Increase `division_size_min` (50 → 70)

**For more convection effects**:
- Increase `buoyancy` (1.5 → 2.5)
- Increase `heat_source_strength` (0.3 → 0.5)
- Decrease `viscosity` (0.95 → 0.90)

**For more horizontal movement**:
- Increase horizontal brownian (already 3×)
- Increase `vesicle_fluid_coupling` (0.15 → 0.25)
- Decrease boundary damping multiplier (0.3 → 0.5)

## Performance Considerations

**GPU Utilization**:
- All `@ti.kernel` functions run on GPU
- Particle count scales linearly (5000-50000 tested)
- Grid resolution quadratically affects performance

**Bottlenecks**:
1. `vesicle_competition()`: O(n²) vesicle comparisons
2. `calculate_vesicle_bias()`: O(n) per vesicle call
3. Fluid advection: O(grid²) but highly parallelized

**Optimization Tips**:
- Reduce `n_particles` for faster iteration
- Reduce `n_grid` if fluid detail not critical (128 → 64)
- Lower `stats_print_interval` to reduce I/O

---

**See Also**:
- [ABIOGENESIS.md](ABIOGENESIS.md) - Scientific context
- [EXPERIMENTS.md](EXPERIMENTS.md) - Parameter study suggestions
- [config.py](config.py) - Full parameter list
