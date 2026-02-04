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

    @property
    def cell_size(self) -> float:
        """Grid cell size."""
        return 1.0 / self.n_grid
