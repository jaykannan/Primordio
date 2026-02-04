# Primordio: Primordial Soup Simulation

An agent-based simulation exploring the emergence of proto-cellular life under primordial Earth conditions. This project models vesicle dynamics, chemical selection, and emergent reproduction in a convecting chemical soup.

![Version](https://img.shields.io/badge/version-0.2.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![Taichi](https://img.shields.io/badge/taichi-1.7.4-orange)

## Overview

Primordio simulates the chemical and physical conditions of Earth's primordial soup (~3.8 billion years ago), focusing on the spontaneous formation and evolution of protocells. The simulation demonstrates how simple physical and chemical rules can lead to:

- **Self-organization** of lipid-like vesicles
- **Chemical selection** based on absorbed monomers
- **Emergent heritability** without genetic material
- **Proto-metabolic** competition and cooperation
- **Primitive reproduction** through mechanical division

This is not a model of modern cellular life, but rather an exploration of the **prebiotic chemical space** where life may have first emerged.

## Scientific Context

The simulation is inspired by:
- **Lipid World Hypothesis** (Segré et al., 2001) - Life beginning with self-assembling amphiphiles
- **Hydrothermal Vent Theory** - Thermal gradients driving chemical organization
- **RNA World Hypothesis** - Chemical selection before genetic encoding
- **Autocatalytic Sets** (Kauffman, 1986) - Self-sustaining chemical networks

See [ABIOGENESIS.md](ABIOGENESIS.md) for detailed scientific background.

## Key Features

### Physical Environment
- **Rayleigh-Bénard Convection**: Simulates thermal currents in shallow primordial pools
- **Temperature Gradients**: Hot bottom (volcanic heat) to cool top (atmosphere)
- **Brownian Motion**: Realistic molecular-scale movement
- **Fluid Dynamics**: Semi-Lagrangian advection with turbulence

### Chemical Entities

**Monomers** (5000 particles):
- 10 different chemical types with unique properties
- 4 behavioral biases per monomer (absorption, division, attraction, repulsion)
- Randomly distributed throughout the soup
- Subject to thermal currents and Brownian motion

**Vesicles** (10 initial protocells):
- Self-assembling membrane-bound structures
- Absorb monomers from the environment
- Grow based on absorbed chemical content
- Divide when reaching critical size
- Compete for resources

### Emergent Behaviors

1. **Chemical Selection**: Vesicles that absorb high-absorption-bias monomers become aggressive predators
2. **Defensive Evolution**: Vesicles with high-repulsion-bias content resist being absorbed
3. **Social Dynamics**: Attraction-bias monomers lead to clustering behavior
4. **Heritable Traits**: Daughter vesicles inherit monomer composition from parents
5. **Resource Competition**: Limited monomer pool creates selective pressure

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/primordio.git
cd primordio

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install taichi numpy
```

## Quick Start

```bash
python scene.py
```

The simulation window will open showing:
- **Blue/cyan rings**: Vesicles (protocells)
- **Colored dots**: Free monomers (chemical compounds)
- **Color-coded monomers**: Different chemical types
- **Dots inside vesicles**: Absorbed monomers

### Controls
- **Close window**: Stop simulation
- Watch the terminal for statistics (vesicle count, absorption rate, etc.)

## Observing Evolution

Interesting phenomena to watch for:

1. **Predator-Prey Dynamics**: Large vesicles hunt smaller ones
2. **Defensive Clusters**: Vesicles with high repulsion resist absorption
3. **Social Groups**: High-attraction vesicles form stable clusters
4. **Division Events**: Watch vesicles split and push apart
5. **Chemical Sorting**: Certain monomer types concentrate in successful lineages
6. **Extinction Events**: Vesicles shrink and die when absorbed
7. **Population Dynamics**: Vesicle count fluctuates due to division/absorption balance

## Configuration

Edit `config.py` to adjust simulation parameters:

```python
# Key parameters for experimentation
n_particles: int = 5000          # Total chemical soup density
vesicle_percentage: float = 0.002  # Initial protocell concentration
division_size_min: float = 50.0   # Size threshold for reproduction
growth_per_monomer: float = 0.08  # Growth rate from absorption
```

See [MECHANICS.md](MECHANICS.md) for detailed parameter explanations.

## Scientific Relevance

### What This Demonstrates

✅ **Spontaneous Organization**: Vesicles self-organize without external intervention
✅ **Chemical Evolution**: Selection occurs at the chemical level, before genetics
✅ **Emergent Heritability**: Daughters inherit chemical composition from parents
✅ **Proto-Metabolism**: Resource absorption and growth without enzymes
✅ **Competition**: Darwinian selection emerges from physical/chemical rules

### What This Does NOT Model

❌ Modern cellular biochemistry (no DNA, RNA, proteins)
❌ Genetic replication or mutation
❌ True metabolic pathways
❌ Specific Earth chemistry (simplified model)
❌ Realistic timescales (accelerated for observation)

## Documentation

- **[ABIOGENESIS.md](ABIOGENESIS.md)** - Connection to origin-of-life research
- **[MECHANICS.md](MECHANICS.md)** - Technical details of all simulation mechanics
- **[THEORY.md](THEORY.md)** - Theoretical foundations and scientific context
- **[EXPERIMENTS.md](EXPERIMENTS.md)** - Suggested experiments and parameter studies

## Architecture

```
primordio/
├── scene.py           # Entry point
├── simulation.py      # Main simulation loop
├── config.py          # Parameters
├── fields.py          # Taichi field definitions
├── particles.py       # Particle dynamics
├── physics.py         # Fluid dynamics
├── vesicles.py        # Protocell mechanics
└── chemistry.py       # Chemical properties
```

## Performance

- **GPU-accelerated**: Runs on CUDA, Metal, or Vulkan via Taichi
- **Real-time**: 30-60 FPS on modern hardware
- **Scalable**: Tested with 5000-50000 particles

## Research Questions

This simulation can help explore:

1. What chemical properties favor early protocell success?
2. How does convection affect protocell distribution and evolution?
3. Can stable "species" emerge from chemical composition alone?
4. What conditions favor cooperation vs. competition?
5. How does division probability affect population dynamics?

## Contributing

This is an experimental research simulation. Contributions welcome:
- New chemical interaction models
- Additional physical constraints
- Visualization improvements
- Parameter sensitivity analysis
- Biological realism enhancements

## References

- Segré, D., et al. (2001). "The Lipid World." *Origins of Life and Evolution of Biospheres*
- Kauffman, S. A. (1986). "Autocatalytic sets of proteins." *Journal of Theoretical Biology*
- Szostak, J. W. (2012). "The eightfold path to non-enzymatic RNA replication." *Journal of Systems Chemistry*
- Lane, N. (2015). *The Vital Question: Energy, Evolution, and the Origins of Complex Life*

## License

MIT License - See LICENSE file for details

## Citation

If you use this simulation in research, please cite:

```bibtex
@software{primordio2025,
  title={Primordio: Primordial Soup Simulation},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/primordio}
}
```

---

**Note**: This is a simplified model for exploring concepts in abiogenesis research. It does not claim to replicate the actual chemistry of early Earth, but rather demonstrates principles that may have been relevant to the origin of life.
