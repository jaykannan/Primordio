"""Fluid physics kernels for the simulation."""

import taichi as ti
from config import SimulationConfig
from fields import SimulationFields


@ti.data_oriented
class FluidPhysics:
    """Handles fluid dynamics computations."""

    def __init__(self, config: SimulationConfig, fields: SimulationFields):
        self.config = config
        self.fields = fields

    @ti.func
    def sample_bilinear(self, field: ti.template(), pos_x: ti.f32, pos_y: ti.f32):
        """Bilinear interpolation for sampling fields."""
        grid_pos_x = pos_x * self.config.n_grid - 0.5
        grid_pos_y = pos_y * self.config.n_grid - 0.5

        i = int(ti.floor(grid_pos_x))
        j = int(ti.floor(grid_pos_y))

        fx = grid_pos_x - i
        fy = grid_pos_y - j

        i = ti.max(0, ti.min(self.config.n_grid - 2, i))
        j = ti.max(0, ti.min(self.config.n_grid - 2, j))

        return (
            (1 - fx) * (1 - fy) * field[i, j]
            + fx * (1 - fy) * field[i + 1, j]
            + (1 - fx) * fy * field[i, j + 1]
            + fx * fy * field[i + 1, j + 1]
        )

    @ti.kernel
    def apply_heat_sources(self):
        """Apply heat sources at the bottom (hydrothermal vents)."""
        for i, j in self.fields.temperature_field:
            # Heat from bottom (many small geothermal vents)
            if j < 8:
                vent_pattern = (i % 8 < 3) or (i % 13 < 2) or (i % 21 < 3)
                if vent_pattern:
                    depth_factor = 1.0 - (j / 8.0)
                    self.fields.temperature_field[i, j] += (
                        self.config.heat_source_strength * depth_factor
                    )

            # Strong cooling at top (many small cooling zones)
            if j > self.config.n_grid - 12:
                cool_pattern = (i % 7 < 3) or (i % 11 < 2) or (i % 19 < 3)
                if cool_pattern:
                    height_factor = (j - (self.config.n_grid - 12)) / 12.0
                    self.fields.temperature_field[i, j] -= (
                        self.config.cooling_strength * height_factor
                    )

            # Ambient cooling (heat dissipation)
            self.fields.temperature_field[i, j] *= self.config.diffusion

            # Clamp temperature to reasonable bounds
            self.fields.temperature_field[i, j] = ti.max(
                -0.5, ti.min(1.0, self.fields.temperature_field[i, j])
            )

    @ti.kernel
    def apply_buoyancy(self):
        """Apply buoyancy force based on temperature (hot rises, cool sinks)."""
        for i, j in self.fields.velocity_field:
            temp_diff = self.fields.temperature_field[i, j] - self.config.ambient_temp
            self.fields.velocity_field[i, j].y += (
                temp_diff * self.config.buoyancy * self.config.dt
            )

            # Clamp velocity magnitude
            vel_mag = ti.sqrt(
                self.fields.velocity_field[i, j].x ** 2
                + self.fields.velocity_field[i, j].y ** 2
            )
            if vel_mag > 0.5:
                self.fields.velocity_field[i, j] *= 0.5 / vel_mag

    @ti.kernel
    def advect_velocity(self):
        """Advect velocity field (self-advection)."""
        for i, j in self.fields.velocity_field:
            pos_x = (i + 0.5) * self.config.cell_size
            pos_y = (j + 0.5) * self.config.cell_size

            vel_sample = self.fields.velocity_field[i, j]
            prev_x = pos_x - vel_sample.x * self.config.dt
            prev_y = pos_y - vel_sample.y * self.config.dt

            prev_x = ti.max(0.0, ti.min(1.0, prev_x))
            prev_y = ti.max(0.0, ti.min(1.0, prev_y))

            self.fields.new_velocity[i, j] = self.sample_bilinear(
                self.fields.velocity_field, prev_x, prev_y
            )
            self.fields.new_velocity[i, j] *= self.config.viscosity

    @ti.kernel
    def advect_temperature(self):
        """Advect temperature field."""
        for i, j in self.fields.temperature_field:
            pos_x = (i + 0.5) * self.config.cell_size
            pos_y = (j + 0.5) * self.config.cell_size

            vel_sample = self.fields.velocity_field[i, j]
            prev_x = pos_x - vel_sample.x * self.config.dt
            prev_y = pos_y - vel_sample.y * self.config.dt

            prev_x = ti.max(0.0, ti.min(1.0, prev_x))
            prev_y = ti.max(0.0, ti.min(1.0, prev_y))

            self.fields.new_temperature[i, j] = self.sample_bilinear(
                self.fields.temperature_field, prev_x, prev_y
            )

    @ti.kernel
    def copy_velocity(self):
        """Copy new velocity to current."""
        for i, j in self.fields.velocity_field:
            self.fields.velocity_field[i, j] = self.fields.new_velocity[i, j]

    @ti.kernel
    def copy_temperature(self):
        """Copy new temperature to current."""
        for i, j in self.fields.temperature_field:
            self.fields.temperature_field[i, j] = self.fields.new_temperature[i, j]

    @ti.kernel
    def enforce_boundaries(self):
        """Enforce boundary conditions."""
        for i, j in self.fields.velocity_field:
            # No-slip boundaries
            if i == 0 or i == self.config.n_grid - 1:
                self.fields.velocity_field[i, j].x = 0
            if j == 0 or j == self.config.n_grid - 1:
                self.fields.velocity_field[i, j].y = 0

            # Clamp velocity magnitude
            vel_mag = ti.sqrt(
                self.fields.velocity_field[i, j].x ** 2
                + self.fields.velocity_field[i, j].y ** 2
            )
            max_vel = 0.5
            if vel_mag > max_vel:
                self.fields.velocity_field[i, j] *= max_vel / vel_mag

    @ti.kernel
    def add_turbulence(self):
        """Add random turbulence for mixing."""
        for i, j in self.fields.velocity_field:
            if ti.random() < 0.005:
                self.fields.velocity_field[i, j] += ti.Vector([
                    (ti.random() - 0.5) * 0.2,
                    (ti.random() - 0.5) * 0.2,
                ])
