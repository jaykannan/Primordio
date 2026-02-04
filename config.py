"""Configuration constants for the primordial soup simulation."""

from dataclasses import dataclass


@dataclass
class SimulationConfig:
    """Simulation parameters and constants."""

    # Display
    width: int = 800
    height: int = 800

    # Particles
    n_particles: int = 5000

    # Grid
    n_grid: int = 128

    # Time
    dt: float = 0.016

    # Physics constants
    buoyancy: float = 1.5
    viscosity: float = 0.95
    diffusion: float = 0.995
    heat_source_strength: float = 0.3
    cooling_strength: float = 0.5
    ambient_temp: float = 0.0

    # Particle physics
    particle_buoyancy: float = 0.15
    particle_gravity: float = 0.025
    particle_damping: float = 0.98
    max_particle_velocity: float = 0.15

    # Temperature zones
    heating_zone_height: float = 0.15  # Bottom zone for heating
    cooling_zone_height: float = 0.85  # Top zone for cooling

    # Brownian motion
    brownian_strength: float = 0.003

    # Rendering
    particle_radius: int = 2
    background_color: int = 0x112233
    stats_print_interval: int = 50

    # Vesicle parameters (from ChemoTaxis)
    vesicle_percentage: float = 0.01  # 1% of particles are vesicles
    vesicle_min_radius: float = 10.0
    vesicle_max_radius: float = 25.0
    growth_per_monomer: float = 0.25  # Radius increase per absorbed monomer
    growth_factor: float = 1.5  # Spatial distribution factor for monomers
    absorb_rate: float = 2.5  # Vesicle-vesicle absorption rate (units/sec)
    mechanical_event_probability: float = 0.2  # 20% chance of division per frame
    division_size_min: float = 50.0  # Minimum radius for division
    division_size_max: float = 75.0  # Maximum radius for division
    death_radius: float = 1.0  # Vesicles below this radius die
    monomer_move_rate: int = 5  # Max monomers transferred during vesicle absorption

    @property
    def cell_size(self) -> float:
        """Grid cell size."""
        return 1.0 / self.n_grid

    @property
    def n_vesicles(self) -> int:
        """Number of initial vesicles."""
        return int(self.n_particles * self.vesicle_percentage)

    @property
    def n_monomers(self) -> int:
        """Number of initial monomers."""
        return self.n_particles - self.n_vesicles
