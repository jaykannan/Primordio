"""Particle update logic."""

import taichi as ti
from config import SimulationConfig
from fields import SimulationFields
from physics import FluidPhysics


@ti.data_oriented
class ParticleSystem:
    """Handles particle dynamics and rendering."""

    def __init__(
        self, config: SimulationConfig, fields: SimulationFields, physics: FluidPhysics
    ):
        self.config = config
        self.fields = fields
        self.physics = physics

    @ti.kernel
    def update_particles(self):
        """Update particles with mass-based cooling and position-based heating."""
        for i in self.fields.pos:
            y_pos = self.fields.pos[i].y

            # Heat particles near the bottom
            if y_pos < self.config.heating_zone_height:
                heat_rate = (
                    self.config.heating_zone_height - y_pos
                ) / self.config.heating_zone_height
                self.fields.particle_temp[i] += heat_rate * 0.02
                self.fields.particle_temp[i] = ti.min(1.0, self.fields.particle_temp[i])

            # Cool particles near the top (mass-based)
            if y_pos > self.config.cooling_zone_height:
                cool_rate = (
                    (y_pos - self.config.cooling_zone_height)
                    / (1.0 - self.config.cooling_zone_height)
                    * self.fields.mass[i]
                    * 0.015
                )
                self.fields.particle_temp[i] -= cool_rate
                self.fields.particle_temp[i] = ti.max(
                    -0.5, self.fields.particle_temp[i]
                )

            # Buoyancy and gravity forces
            buoyancy_force = (
                self.fields.particle_temp[i] * self.config.particle_buoyancy
            )
            gravity_force = -self.fields.mass[i] * self.config.particle_gravity

            # Update velocity
            self.fields.vel[i].y += (
                buoyancy_force + gravity_force
            ) * self.config.dt

            # Damping
            self.fields.vel[i] *= self.config.particle_damping

            # Fluid coupling
            fluid_vel = self.physics.sample_bilinear(
                self.fields.velocity_field,
                self.fields.pos[i].x,
                self.fields.pos[i].y,
            )
            self.fields.vel[i] += fluid_vel * 0.1 * self.config.dt

            # Cap velocity
            vel_mag = ti.sqrt(
                self.fields.vel[i].x ** 2 + self.fields.vel[i].y ** 2
            )
            if vel_mag > self.config.max_particle_velocity:
                self.fields.vel[i] *= self.config.max_particle_velocity / vel_mag

            # Update position
            self.fields.pos[i] += self.fields.vel[i] * self.config.dt

            # Brownian motion
            thermal_energy = ti.max(0.0, self.fields.particle_temp[i] + 0.5)
            brownian_strength = self.config.brownian_strength * thermal_energy

            brownian_motion = ti.Vector([
                (ti.random() - 0.5) * brownian_strength,
                (ti.random() - 0.5) * brownian_strength,
            ])
            self.fields.pos[i] += brownian_motion

            # Wrap around boundaries
            if self.fields.pos[i].x < 0:
                self.fields.pos[i].x += 1.0
            if self.fields.pos[i].x > 1:
                self.fields.pos[i].x -= 1.0
            if self.fields.pos[i].y < 0:
                self.fields.pos[i].y += 1.0
            if self.fields.pos[i].y > 1:
                self.fields.pos[i].y -= 1.0

            # Update color based on temperature
            self._update_particle_color(i)

    @ti.func
    def _update_particle_color(self, i: int):
        """Update particle color based on temperature."""
        temp = self.fields.particle_temp[i]

        if temp > 0.3:
            # Hot: red/orange
            self.fields.colors[i] = ti.Vector([
                ti.min(1.0, 0.8 + temp * 0.2),
                ti.min(1.0, 0.3 + temp * 0.3),
                0.1,
            ])
        elif temp > 0.1:
            # Warm: yellow
            self.fields.colors[i] = ti.Vector([
                ti.min(1.0, 0.8 + temp * 2),
                ti.min(1.0, 0.8 + temp),
                0.3,
            ])
        elif temp < -0.2:
            # Cold: dark blue
            self.fields.colors[i] = ti.Vector([0.1, 0.3, 0.7])
        else:
            # Cool/Neutral: blue/cyan
            self.fields.colors[i] = ti.Vector([0.3, 0.6, 0.9])
