# Code Architecture

## Overview

The codebase has been refactored into a modular architecture following software engineering best practices for maintainability, testability, and extensibility.

## File Structure

```
Primordio/
├── config.py           # Configuration and constants
├── fields.py           # Field definitions and initialization
├── physics.py          # Fluid physics kernels
├── particles.py        # Particle update logic
├── simulation.py       # Main simulation orchestration
├── scene.py            # Original monolithic version (legacy)
├── scene_refactored.py # New entry point
└── __init__.py         # Package initialization
```

## Module Descriptions

### config.py
**Purpose**: Centralized configuration management

**Key Classes**:
- `SimulationConfig`: Dataclass containing all simulation parameters

**Benefits**:
- Single source of truth for constants
- Easy to modify parameters
- Type-safe with dataclass
- Can be easily extended with validation logic

### fields.py
**Purpose**: Taichi field management and initialization

**Key Classes**:
- `SimulationFields`: Container for all Taichi fields (particles, grids, temporary)

**Responsibilities**:
- Create and manage Taichi fields
- Initialize particles with random properties
- Initialize fluid fields to zero

**Benefits**:
- Encapsulates field lifetime management
- Clear initialization interface
- Easy to add new fields

### physics.py
**Purpose**: Fluid dynamics computations

**Key Classes**:
- `FluidPhysics`: Handles all fluid simulation kernels

**Key Methods**:
- `sample_bilinear()`: Field interpolation
- `apply_heat_sources()`: Thermal boundary conditions
- `apply_buoyancy()`: Temperature-driven forces
- `advect_velocity()`: Velocity field transport
- `advect_temperature()`: Temperature field transport
- `enforce_boundaries()`: No-slip boundary conditions
- `add_turbulence()`: Random perturbations

**Benefits**:
- Separation of concerns (fluid vs particles)
- Each method has single responsibility
- Easy to test individual physics components

### particles.py
**Purpose**: Particle system dynamics

**Key Classes**:
- `ParticleSystem`: Handles particle updates and coloring

**Key Methods**:
- `update_particles()`: Main particle update kernel
- `_update_particle_color()`: Temperature-based coloring

**Responsibilities**:
- Particle heating/cooling based on position
- Buoyancy and gravity forces
- Brownian motion
- Fluid coupling
- Boundary wrapping
- Visual representation (colors)

**Benefits**:
- Particle logic isolated from fluid physics
- Color management separated into function
- Easy to modify particle behavior

### simulation.py
**Purpose**: Orchestrate the complete simulation

**Key Classes**:
- `PrimordialSoupSimulation`: Main simulation controller

**Key Methods**:
- `initialize()`: Setup all components
- `step()`: Execute single timestep
- `get_stats()`: Compute diagnostics
- `run()`: Main simulation loop with GUI

**Responsibilities**:
- Component coordination
- Simulation loop management
- Statistics gathering
- Rendering coordination

**Benefits**:
- Clear simulation lifecycle
- Easy to add monitoring/logging
- Headless mode possible (modify `run()`)
- Testable without GUI

### scene_refactored.py
**Purpose**: Application entry point

**Responsibilities**:
- Taichi initialization
- Configuration creation
- Simulation instantiation and execution

**Benefits**:
- Minimal, clean entry point
- Easy to modify for different configs
- Could support command-line arguments

## Design Patterns Used

### 1. **Dependency Injection**
- Components receive dependencies through constructors
- Example: `FluidPhysics(config, fields)`
- Benefits: Testability, flexibility, clear dependencies

### 2. **Single Responsibility Principle**
- Each class has one clear purpose
- Example: `FluidPhysics` only handles fluid, not particles

### 3. **Configuration Object**
- All parameters in `SimulationConfig`
- Avoids magic numbers throughout code

### 4. **Facade Pattern**
- `PrimordialSoupSimulation` provides simple interface
- Hides complexity of component interactions

## Advantages Over Monolithic Design

### Maintainability
- **Easier to locate code**: Want to change heating? Look in `physics.py`
- **Clear boundaries**: No mixing of concerns
- **Reduced cognitive load**: Each file is focused and understandable

### Testability
- **Unit testing**: Can test `FluidPhysics` independently
- **Mock dependencies**: Easy to substitute test doubles
- **Integration testing**: Can test component interactions

### Extensibility
- **Add new physics**: Extend `FluidPhysics` or create new class
- **Different particle types**: Subclass `ParticleSystem`
- **Multiple configurations**: Create different `SimulationConfig` instances
- **Plugins**: Easy to add new components

### Reusability
- **Use components separately**: Maybe just need fluid physics
- **Different frontends**: CLI, web, batch processing
- **Library usage**: Import as package in other projects

## Migration Path

The original `scene.py` remains functional. To use the refactored version:

```python
# Old way
python scene.py

# New way
python scene_refactored.py
```

Both produce identical simulation behavior.

## Future Enhancements

### Potential Improvements
1. **Type hints**: Add throughout for better IDE support
2. **Logging**: Replace prints with proper logging
3. **Configuration files**: Load from YAML/JSON
4. **Command-line interface**: argparse for runtime config
5. **Profiling hooks**: Performance monitoring
6. **Save/load state**: Checkpoint system
7. **Unit tests**: Test suite for each module
8. **Documentation**: Docstrings for all public APIs

### Extension Points
- **New physics models**: Create alternative physics classes
- **Renderers**: Separate rendering from simulation
- **Analysis tools**: Post-processing and visualization
- **Parameter sweeps**: Batch running with different configs

## Performance Considerations

The modular design has **no performance impact** because:
- Taichi kernels are still compiled the same way
- Method calls happen at Python level (outside kernel)
- Kernel boundaries unchanged
- Same GPU code generation

## Conclusion

This architecture balances:
- **Simplicity**: Easy to understand and navigate
- **Flexibility**: Easy to modify and extend
- **Maintainability**: Clear structure aids long-term development
- **Performance**: No overhead from good structure
