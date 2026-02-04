"""Field definitions and initialization for the simulation."""

import taichi as ti
from config import SimulationConfig


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
        """Initialize all particles as hot/rising with random mass."""
        for i in self.pos:
            self.pos[i] = ti.Vector([ti.random(), ti.random()])

            # All particles start hot (rising state)
            self.particle_temp[i] = 0.5 + ti.random() * 0.5

            # Random mass - heavier particles cool faster and sink more
            self.mass[i] = 0.5 + ti.random() * 1.5

            # Start with slight upward velocity
            self.vel[i] = ti.Vector([0.0, ti.random() * 0.05])

            # Color based on initial temperature (all hot colors)
            self.colors[i] = ti.Vector([
                ti.min(1.0, 0.8 + self.particle_temp[i] * 0.2),
                ti.min(1.0, 0.3 + self.particle_temp[i] * 0.3),
                0.1,
            ])

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
