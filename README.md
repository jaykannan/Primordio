# Primordio

A particle-based primordial soup simulation featuring realistic thermal convection dynamics and Brownian motion.

## Overview

This project simulates a primordial ocean environment where particles undergo continuous convection cycles driven by temperature differences. The simulation models individual particles with unique properties (mass, temperature) creating emergent, non-uniform circulation patterns.

## Physics Model

### Particle Properties
- **Individual Mass**: Each particle has random mass (0.5-2.0), affecting cooling rate and sinking behavior
- **Individual Temperature**: Tracks thermal state independently per particle
- **Brownian Motion**: Temperature-dependent random molecular movement

### Convection Cycle
1. **All particles start hot** - Begin with thermal energy and rise
2. **Non-uniform rising** - Different masses create varied ascent rates
3. **Mass-based cooling at top** - Heavier particles cool faster when reaching the surface
4. **Gravity-driven sinking** - Cooled particles descend back to the bottom
5. **Reheat near bottom** - Only particles close to the floor (bottom 15%) regain thermal energy

### Key Features
- **Many small heat vents** at the bottom with varied sizes and positions
- **Multiple cooling zones** at the top with non-uniform distribution
- **Temperature-dependent Brownian motion** - Hotter particles jitter more
- **Velocity clamping** to prevent runaway speeds
- **Fluid coupling** - Weak interaction with background velocity field

## Technology

Built with **Taichi** - a high-performance parallel computing framework for GPU acceleration.

## Requirements

```toml
python = ">=3.12"
taichi = ">=1.7.2"
```

## Installation

Using [uv](https://github.com/astral-sh/uv):

```bash
uv sync
```

Or with pip:

```bash
pip install -r requirements.txt
```

## Usage

Run the simulation:

```bash
python scene.py
```

The simulation will open a GUI window showing the particle dynamics:
- **Red/Orange particles**: Hot, rising
- **Yellow particles**: Warm
- **Light blue particles**: Cool/neutral
- **Dark blue particles**: Cold, sinking

Console output displays real-time statistics every 50 frames:
- Velocity (max/average)
- Temperature (max/min/average)

## Parameters

Key simulation constants in [scene.py](scene.py):

```python
n_particles = 5000          # Number of particles
n_grid = 128               # Fluid grid resolution
buoyancy = 1.5             # Buoyancy force strength
brownian_strength = 0.003  # Molecular motion scale
```

## License

MIT

## Acknowledgments

Built with assistance from Claude (Anthropic).
