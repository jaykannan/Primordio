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
    vesicle_percentage: float = 0.005  # 0.5% of particles are vesicles (moderate density)
    vesicle_min_radius: float = 5.0  # Wider size range for variety
    vesicle_max_radius: float = 35.0
    growth_per_monomer: float = 0.08  # Radius increase per absorbed monomer (slower growth)
    growth_factor: float = 1.5  # Spatial distribution factor for monomers
    absorb_rate: float = 2.5  # Vesicle-vesicle absorption rate (units/sec)
    absorption_probability: float = 0.05  # 5% chance per frame to absorb a colliding monomer
    vesicle_fluid_coupling: float = 0.05  # How much vesicles respond to fluid currents (light influence)
    mechanical_event_probability: float = 0.2  # 20% chance of division per frame
    division_size_min: float = 50.0  # Minimum radius for division
    division_size_max: float = 75.0  # Maximum radius for division
    death_radius: float = 1.0  # Vesicles below this radius die
    monomer_move_rate: int = 5  # Max monomers transferred during vesicle absorption

    # Vesicle movement
    vesicle_horizontal_drift: float = 0.025  # Random horizontal drift strength (autonomous motion)
    vesicle_brownian_horizontal: float = 0.005  # Horizontal Brownian motion (autonomous)
    vesicle_brownian_vertical: float = 0.001  # Vertical Brownian motion (autonomous)
    vesicle_damping: float = 0.99  # Velocity retention per frame (maintains momentum)
    vesicle_max_velocity: float = 0.06  # Maximum velocity cap for vesicles

    # Boundary handling
    edge_repulsion_margin: float = 0.05  # Distance from edge where repulsion starts (5%)
    edge_repulsion_strength: float = 0.02  # Strength of edge repulsion force
    vesicle_boundary_dampening_horizontal: float = 0.7  # Velocity retention on horizontal wrap
    vesicle_boundary_dampening_vertical: float = 0.4  # Velocity retention on vertical bounce
    vesicle_surface_margin_bottom: float = 0.02  # Bottom surface boundary position
    vesicle_surface_margin_top: float = 0.98  # Top surface boundary position
    monomer_boundary_dampening_horizontal: float = 0.3  # Monomer horizontal wrap dampening
    monomer_boundary_dampening_vertical: float = 0.5  # Monomer vertical wrap dampening

    # Monomer absorption mechanics
    absorption_rejection_repulsion: float = 0.008  # Repulsion when absorption rejected
    horizontal_force_bias: float = 2.0  # Multiplier for horizontal forces (anisotropic)
    absorbed_monomer_offset_scale: float = 0.5  # Scale factor for monomer positioning inside vesicle

    # Vesicle competition mechanics
    absorption_bias_base: float = 0.5  # Base multiplier for absorption advantage
    resistance_multiplier: float = 0.5  # Multiplier for resistance effect
    transfer_size_fraction: float = 0.1  # Fraction of losing vesicle transferred per frame (10%)
    growth_efficiency: float = 0.8  # Efficiency of size transfer (80% retained)

    # Vesicle division mechanics
    division_offset_range: float = 0.05  # Spatial offset range for child vesicles
    division_size_split: float = 0.5  # Size split ratio (50% each)
    division_velocity_inheritance: float = 0.5  # Velocity inherited by child (50%)
    division_push_strength: float = 0.001  # Base push strength multiplier (violent size-scaled repulsion)
    division_size_instability: float = 2.0  # Multiplier for size-dependent division probability
    absorption_rate_min: float = 0.005  # Minimum absorption rate (0.5%)
    absorption_rate_max: float = 0.05  # Maximum absorption rate (5%)

    # Multi-way division thresholds
    division_2way_max: float = 60.0  # Maximum radius for 2-way split
    division_3way_max: float = 70.0  # Maximum radius for 3-way split
    # 4+ way split for anything larger

    # Vesicle interaction mechanics
    interaction_range: float = 0.15  # Maximum distance for vesicle-vesicle interactions
    ambient_pressure_strength: float = 0.004  # Strength of size-similarity repulsion (5× stronger)
    attraction_strength_multiplier: float = 0.0003  # Multiplier for attraction forces
    repulsion_strength_multiplier: float = 0.0005  # Multiplier for repulsion forces

    # Default bias values
    default_bias_value: float = 0.5  # Default bias when vesicle has no monomers

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
