# CLAUDE.md

## Project Overview

Primordio is a GPU-accelerated agent-based simulation of primordial soup chemistry, modeling vesicle dynamics, chemical selection, and emergent proto-cellular reproduction. Built with Taichi for real-time GPU computation.

## Tech Stack

- **Python** 3.9+ with **Taichi** (GPU-accelerated computation)
- **NumPy** for array operations and statistics
- Package management via **uv** (fallback: pip)

## Quick Reference

```bash
# Install dependencies
uv sync
# OR: pip install taichi numpy

# Run the simulation
python scene.py
```

There is no build step — Taichi JIT-compiles kernels at runtime. No formal test suite exists; verification is done visually and via console statistics (printed every 50 frames).

## Architecture

Flat module structure, no subdirectories:

```
scene.py          → Entry point, GUI loop
simulation.py     → Orchestration facade (PrimordialSoupSimulation)
config.py         → SimulationConfig dataclass (100+ parameters)
fields.py         → Taichi field definitions and initialization
physics.py        → Fluid dynamics (Rayleigh-Bénard convection)
particles.py      → Monomer particle system
vesicles.py       → Vesicle mechanics (absorption, division, competition)
chemistry.py      → Chemical property enums and monomer type definitions
```

**Dependency flow** (no circular deps):
`scene → simulation → {config, fields, physics, particles, vesicles} → {fields, chemistry}`

**Key patterns:**
- `@ti.data_oriented` classes with `@ti.kernel` methods for GPU execution
- Dependency injection — components receive fields/config via constructors
- Centralized configuration via `SimulationConfig` dataclass in `config.py`
- Facade pattern — `PrimordialSoupSimulation` exposes a simple `step()`/`render()` interface

## Key Domain Concepts

- **Monomers**: 10 types with chemical properties (ATTACH, REPEL, SPLIT, etc.) and 4 bias scores
- **Vesicles**: Proto-cells that absorb monomers, grow, compete, polymerize internal contents, and divide
- **Division**: Multi-way splitting (2/3/4-way) based on size, with polymer stabilization and monomer loss
- **Convection**: Heated bottom / cooled top fluid dynamics driving particle transport

## Code Conventions

- All GPU-parallel code uses Taichi decorators (`@ti.kernel`, `@ti.func`)
- Classes with Taichi kernels must have `@ti.data_oriented` decorator
- Grid resolution is 128x128; display is 800x800
- Default particle count: 5000 (25 vesicles, 4975 monomers)
- Statistics output to console every 50 frames
