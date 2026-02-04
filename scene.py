"""Entry point for the primordial soup simulation."""

import taichi as ti
from config import SimulationConfig
from simulation import PrimordialSoupSimulation


def main():
    """Initialize and run the simulation."""
    # Initialize Taichi for GPU
    ti.init(arch=ti.gpu)

    # Create configuration
    config = SimulationConfig()

    # Create and run simulation
    simulation = PrimordialSoupSimulation(config)
    simulation.run()


if __name__ == "__main__":
    main()
