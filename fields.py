"""Field definitions and initialization for the simulation."""

import taichi as ti
from config import SimulationConfig
from chemistry import ChemicalProperty, ParticleType, NUM_MONOMER_TYPES, PROPERTY_COLORS


@ti.data_oriented
class SimulationFields:
    """Container for all Taichi fields used in the simulation."""

    def __init__(self, config: SimulationConfig):
        self.config = config

        # Particle fields
        self.pos = ti.Vector.field(2, dtype=ti.f32, shape=config.n_particles)
        self.vel = ti.Vector.field(2, dtype=ti.f32, shape=config.n_particles)
        self.colors = ti.Vector.field(3, dtype=ti.f32, shape=config.n_particles)
        self.mass = ti.field(dtype=ti.f32, shape=config.n_particles)
        self.particle_temp = ti.field(dtype=ti.f32, shape=config.n_particles)

        # Monomer/Vesicle fields
        self.particle_type = ti.field(dtype=ti.i32, shape=config.n_particles)
        self.monomer_type = ti.field(dtype=ti.i32, shape=config.n_particles)
        self.chemical_property = ti.field(dtype=ti.i32, shape=config.n_particles)
        self.radius = ti.field(dtype=ti.f32, shape=config.n_particles)
        self.radius_threshold = ti.field(dtype=ti.f32, shape=config.n_particles)

        # Monomer bias scores (determine behavior)
        self.absorption_bias = ti.field(dtype=ti.f32, shape=config.n_particles)  # 0-1: tendency to absorb
        self.division_bias = ti.field(dtype=ti.f32, shape=config.n_particles)    # 0-1: tendency to divide
        self.attraction_bias = ti.field(dtype=ti.f32, shape=config.n_particles)  # 0-1: tendency to attract
        self.repulsion_bias = ti.field(dtype=ti.f32, shape=config.n_particles)   # 0-1: tendency to repel

        # Vesicle polymer tracking
        # Each monomer that's absorbed by a vesicle stores the vesicle's ID
        self.parent_vesicle = ti.field(dtype=ti.i32, shape=config.n_particles)
        # Offset position relative to vesicle center (for monomers inside vesicles)
        self.offset = ti.Vector.field(2, dtype=ti.f32, shape=config.n_particles)

        # Vesicle statistics and properties
        self.monomers_eaten = ti.field(dtype=ti.i32, shape=config.n_particles)
        self.life_timer = ti.field(dtype=ti.f32, shape=config.n_particles)
        self.volume_growth = ti.field(dtype=ti.f32, shape=config.n_particles)
        self.absorption_rate = ti.field(dtype=ti.f32, shape=config.n_particles)  # Per-vesicle absorption probability
        self.polymer_level = ti.field(dtype=ti.f32, shape=config.n_particles)  # Polymerization level (0-1, higher = more stable)

        # Fluid grid fields
        self.velocity_field = ti.Vector.field(
            2, dtype=ti.f32, shape=(config.n_grid, config.n_grid)
        )
        self.temperature_field = ti.field(
            dtype=ti.f32, shape=(config.n_grid, config.n_grid)
        )
        self.pressure_field = ti.field(
            dtype=ti.f32, shape=(config.n_grid, config.n_grid)
        )

        # Temporary fields for advection
        self.new_velocity = ti.Vector.field(
            2, dtype=ti.f32, shape=(config.n_grid, config.n_grid)
        )
        self.new_temperature = ti.field(
            dtype=ti.f32, shape=(config.n_grid, config.n_grid)
        )

    @ti.kernel
    def init_particles(self):
        """Initialize particles as monomers and vesicles for abiogenesis."""
        n_vesicles = int(self.config.n_particles * self.config.vesicle_percentage)

        for i in self.pos:
            self.pos[i] = ti.Vector([ti.random(), ti.random()])
            self.particle_temp[i] = 0.5 + ti.random() * 0.5
            self.mass[i] = 0.5 + ti.random() * 1.5
            self.vel[i] = ti.Vector([0.0, ti.random() * 0.05])

            # Initialize parent tracking
            self.parent_vesicle[i] = -1
            self.offset[i] = ti.Vector([0.0, 0.0])

            # Initialize stats
            self.monomers_eaten[i] = 0
            self.life_timer[i] = 0.0
            self.volume_growth[i] = 0.0
            self.absorption_rate[i] = 0.0  # Default for monomers

            # Initialize monomer bias scores (random distribution)
            self.absorption_bias[i] = ti.random()
            self.division_bias[i] = ti.random()
            self.attraction_bias[i] = ti.random()
            self.repulsion_bias[i] = ti.random()

            # First 0.2% are vesicles, rest are monomers
            if i < n_vesicles:
                # Initialize as vesicle with varied properties
                self.particle_type[i] = int(ParticleType.VESICLE)

                # Wider size range for more variety
                self.radius[i] = (
                    self.config.vesicle_min_radius
                    + ti.random()
                    * (self.config.vesicle_max_radius - self.config.vesicle_min_radius)
                )

                # Set threshold to division size so vesicles can grow before dividing
                self.radius_threshold[i] = self.config.division_size_min
                self.monomer_type[i] = -1  # Vesicles don't have a monomer type
                self.chemical_property[i] = int(ChemicalProperty.NONE)

                # Random absorption rate per vesicle
                self.absorption_rate[i] = self.config.absorption_rate_min + ti.random() * (self.config.absorption_rate_max - self.config.absorption_rate_min)

                # Initial polymer level (starts at 0, builds up over time)
                self.polymer_level[i] = 0.0

                # Vesicle color (cyan/green to distinguish from monomers)
                self.colors[i] = ti.Vector([0.2, 0.8, 0.8])
            else:
                # Initialize as monomer
                self.particle_type[i] = int(ParticleType.MONOMER)
                self.radius[i] = self.config.particle_radius
                self.radius_threshold[i] = self.config.particle_radius

                # Random monomer type (0-9)
                self.monomer_type[i] = int(ti.random() * NUM_MONOMER_TYPES)

                # Random chemical property (0-9)
                prop = int(ti.random() * 10)
                self.chemical_property[i] = prop

                # Color based on chemical property
                if prop == int(ChemicalProperty.NONE):
                    self.colors[i] = ti.Vector([0.5, 0.5, 0.8])
                elif prop == int(ChemicalProperty.ATTACH):
                    self.colors[i] = ti.Vector([0.0, 0.0, 1.0])
                elif prop == int(ChemicalProperty.SUBTRACT):
                    self.colors[i] = ti.Vector([0.0, 0.0, 0.0])
                elif prop == int(ChemicalProperty.ATTRACT):
                    self.colors[i] = ti.Vector([1.0, 0.41, 0.71])
                elif prop == int(ChemicalProperty.REPEL):
                    self.colors[i] = ti.Vector([0.5, 0.5, 0.0])
                elif prop == int(ChemicalProperty.SPLIT):
                    self.colors[i] = ti.Vector([0.65, 0.16, 0.16])
                elif prop == int(ChemicalProperty.COMBINE):
                    self.colors[i] = ti.Vector([0.5, 0.0, 0.5])
                elif prop == int(ChemicalProperty.COPY):
                    self.colors[i] = ti.Vector([1.0, 0.0, 0.0])
                elif prop == int(ChemicalProperty.INCREASE_PH):
                    self.colors[i] = ti.Vector([1.0, 0.65, 0.0])
                else:  # DECREASE_PH
                    self.colors[i] = ti.Vector([1.0, 1.0, 0.0])

    @ti.kernel
    def init_fluid(self):
        """Initialize fluid fields."""
        for i, j in self.velocity_field:
            self.velocity_field[i, j] = ti.Vector([0.0, 0.0])
            self.temperature_field[i, j] = 0.0
            self.pressure_field[i, j] = 0.0

    def initialize(self):
        """Initialize all fields."""
        self.init_particles()
        self.init_fluid()
