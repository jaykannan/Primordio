"""Particle update logic."""

import taichi as ti
from config import SimulationConfig
from fields import SimulationFields
from physics import FluidPhysics
from chemistry import ParticleType, ChemicalProperty, PROPERTY_COLORS


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
        """Update particles: monomers with drift, vesicles slow and stable."""
        for i in self.fields.pos:
            particle_type = self.fields.particle_type[i]
            y_pos = self.fields.pos[i].y

            # Skip absorbed particles
            if particle_type == int(ParticleType.ABSORBED):
                continue

            # Heat/cool based on position
            if y_pos < self.config.heating_zone_height:
                heat_rate = (
                    self.config.heating_zone_height - y_pos
                ) / self.config.heating_zone_height
                self.fields.particle_temp[i] += heat_rate * 0.02
                self.fields.particle_temp[i] = ti.min(1.0, self.fields.particle_temp[i])

            if y_pos > self.config.cooling_zone_height:
                cool_rate = (
                    (y_pos - self.config.cooling_zone_height)
                    / (1.0 - self.config.cooling_zone_height)
                    * self.fields.mass[i]
                    * 0.015
                )
                self.fields.particle_temp[i] -= cool_rate
                self.fields.particle_temp[i] = ti.max(-0.5, self.fields.particle_temp[i])

            if particle_type == int(ParticleType.VESICLE):
                # VESICLES: Move moderately - slower than monomers but visible
                buoyancy_force = self.fields.particle_temp[i] * 0.08  # ~50% of monomer speed
                gravity_force = -self.fields.mass[i] * 0.015  # ~50% of monomer speed

                self.fields.vel[i].y += (buoyancy_force + gravity_force) * self.config.dt
                self.fields.vel[i] *= 0.97  # Moderate damping

                # Fluid coupling for vesicles (respond to convection currents)
                fluid_vel = self.physics.sample_bilinear(
                    self.fields.velocity_field,
                    self.fields.pos[i].x,
                    self.fields.pos[i].y,
                )
                self.fields.vel[i] += fluid_vel * self.config.vesicle_fluid_coupling * self.config.dt

                # Enhanced horizontal drift for vesicles (simulate repelling forces)
                horizontal_bias = (ti.random() - 0.5) * 0.008  # 10x stronger horizontal drift
                self.fields.vel[i].x += horizontal_bias

                # Minimal Brownian motion for vesicles (more horizontal)
                brownian_motion = ti.Vector([
                    (ti.random() - 0.5) * 0.003,  # 4x stronger horizontal
                    (ti.random() - 0.5) * 0.0005,  # Reduced vertical
                ])
                self.fields.pos[i] += brownian_motion

                # Cap vesicle velocity moderately
                vel_mag = ti.sqrt(self.fields.vel[i].x ** 2 + self.fields.vel[i].y ** 2)
                if vel_mag > 0.06:  # Moderate max speed (vs 0.15 for monomers)
                    self.fields.vel[i] *= 0.06 / vel_mag

            else:  # MONOMERS
                # Standard buoyancy/gravity
                buoyancy_force = self.fields.particle_temp[i] * self.config.particle_buoyancy
                gravity_force = -self.fields.mass[i] * self.config.particle_gravity

                self.fields.vel[i].y += (buoyancy_force + gravity_force) * self.config.dt
                self.fields.vel[i] *= self.config.particle_damping

                # Fluid coupling
                fluid_vel = self.physics.sample_bilinear(
                    self.fields.velocity_field,
                    self.fields.pos[i].x,
                    self.fields.pos[i].y,
                )
                self.fields.vel[i] += fluid_vel * 0.1 * self.config.dt

                # Enhanced horizontal drift for monomers
                drift_strength = 0.002
                self.fields.vel[i].x += (ti.random() - 0.5) * drift_strength

                # Brownian motion
                thermal_energy = ti.max(0.0, self.fields.particle_temp[i] + 0.5)
                brownian_strength = self.config.brownian_strength * thermal_energy * 2.0  # 2x stronger

                brownian_motion = ti.Vector([
                    (ti.random() - 0.5) * brownian_strength * 3.0,  # 3x horizontal
                    (ti.random() - 0.5) * brownian_strength,
                ])
                self.fields.pos[i] += brownian_motion

                # Cap velocity
                vel_mag = ti.sqrt(self.fields.vel[i].x ** 2 + self.fields.vel[i].y ** 2)
                if vel_mag > self.config.max_particle_velocity:
                    self.fields.vel[i] *= self.config.max_particle_velocity / vel_mag

            # Update position
            self.fields.pos[i] += self.fields.vel[i] * self.config.dt

            # Wrap around boundaries with velocity dampening to prevent flickering
            if self.fields.pos[i].x < 0:
                self.fields.pos[i].x += 1.0
                self.fields.vel[i].x *= 0.3  # Dampen horizontal velocity
            if self.fields.pos[i].x > 1:
                self.fields.pos[i].x -= 1.0
                self.fields.vel[i].x *= 0.3  # Dampen horizontal velocity
            if self.fields.pos[i].y < 0:
                self.fields.pos[i].y += 1.0
                self.fields.vel[i].y *= 0.5  # Dampen vertical velocity
            if self.fields.pos[i].y > 1:
                self.fields.pos[i].y -= 1.0
                self.fields.vel[i].y *= 0.5  # Dampen vertical velocity

            # Update color
            self._update_particle_color(i)

    @ti.func
    def _update_particle_color(self, i: int):
        """Update particle color: vesicles stay cyan, monomers fade by temperature."""
        particle_type = self.fields.particle_type[i]
        temp = self.fields.particle_temp[i]

        if particle_type == int(ParticleType.VESICLE):
            # Vesicles always stay cyan - no color change
            self.fields.colors[i] = ti.Vector([0.2, 0.8, 0.8])

        else:  # MONOMER
            # Monomers: base color from chemical property, fade with temperature
            prop = self.fields.chemical_property[i]

            # Initialize base_color (required by Taichi)
            base_color = ti.Vector([0.5, 0.5, 0.8])

            # Get base color for this chemical property
            if prop == int(ChemicalProperty.NONE):
                base_color = ti.Vector([0.5, 0.5, 0.8])
            elif prop == int(ChemicalProperty.ATTACH):
                base_color = ti.Vector([0.0, 0.0, 1.0])
            elif prop == int(ChemicalProperty.SUBTRACT):
                base_color = ti.Vector([0.3, 0.3, 0.3])  # Lightened black
            elif prop == int(ChemicalProperty.ATTRACT):
                base_color = ti.Vector([1.0, 0.41, 0.71])
            elif prop == int(ChemicalProperty.REPEL):
                base_color = ti.Vector([0.5, 0.5, 0.0])
            elif prop == int(ChemicalProperty.SPLIT):
                base_color = ti.Vector([0.65, 0.16, 0.16])
            elif prop == int(ChemicalProperty.COMBINE):
                base_color = ti.Vector([0.5, 0.0, 0.5])
            elif prop == int(ChemicalProperty.COPY):
                base_color = ti.Vector([1.0, 0.0, 0.0])
            elif prop == int(ChemicalProperty.INCREASE_PH):
                base_color = ti.Vector([1.0, 0.65, 0.0])
            elif prop == int(ChemicalProperty.DECREASE_PH):
                base_color = ti.Vector([1.0, 1.0, 0.0])

            # Fade brightness based on temperature
            # temp range: -0.5 to 1.0 → fade factor: 0.3 to 1.0
            fade_factor = 0.5 + (temp + 0.5) * 0.33  # Maps [-0.5,1.0] to [0.3,1.0]
            fade_factor = ti.max(0.3, ti.min(1.0, fade_factor))

            self.fields.colors[i] = base_color * fade_factor
