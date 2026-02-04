"""Main simulation orchestration."""

import numpy as np
import taichi as ti
from config import SimulationConfig
from fields import SimulationFields
from particles import ParticleSystem
from physics import FluidPhysics


class PrimordialSoupSimulation:
    """Orchestrates the complete simulation."""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.fields = SimulationFields(config)
        self.physics = FluidPhysics(config, self.fields)
        self.particles = ParticleSystem(config, self.fields, self.physics)
        self.frame = 0

    def initialize(self):
        """Initialize all simulation components."""
        print("Initializing Primordial Soup Simulation...")
        print(f"Particles: {self.config.n_particles}")
        print(f"Grid: {self.config.n_grid}x{self.config.n_grid}")
        self.fields.initialize()

    def step(self):
        """Execute a single simulation step."""
        # Apply heat sources and cooling
        self.physics.apply_heat_sources()

        # Apply buoyancy forces
        self.physics.apply_buoyancy()

        # Advect velocity field
        self.physics.advect_velocity()
        self.physics.copy_velocity()

        # Advect temperature field
        self.physics.advect_temperature()
        self.physics.copy_temperature()

        # Enforce boundary conditions
        self.physics.enforce_boundaries()

        # Add turbulence
        self.physics.add_turbulence()

        # Update particles
        self.particles.update_particles()

    def get_stats(self) -> dict:
        """Get simulation statistics."""
        vel_field = self.fields.velocity_field.to_numpy()
        temp_field = self.fields.temperature_field.to_numpy()

        vel_mag = (vel_field[:, :, 0] ** 2 + vel_field[:, :, 1] ** 2) ** 0.5

        return {
            "max_velocity": vel_mag.max(),
            "avg_velocity": vel_mag.mean(),
            "max_temp": temp_field.max(),
            "min_temp": temp_field.min(),
            "avg_temp": temp_field.mean(),
        }

    def print_stats(self):
        """Print simulation statistics."""
        stats = self.get_stats()
        print(
            f"Frame {self.frame:4d} | "
            f"Vel: max={stats['max_velocity']:.3f} avg={stats['avg_velocity']:.3f} | "
            f"Temp: max={stats['max_temp']:.3f} min={stats['min_temp']:.3f} avg={stats['avg_temp']:.3f}"
        )

    def get_particle_data(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Get particle positions, colors, radii, and types for rendering."""
        positions = self.fields.pos.to_numpy()
        colors = self.fields.colors.to_numpy()
        radii = self.fields.radius.to_numpy()
        types = self.fields.particle_type.to_numpy()
        return positions, colors, radii, types

    def run(self):
        """Run the simulation with GUI."""
        self.initialize()

        # Create GUI
        gui = ti.GUI(
            "Primordial Soup",
            res=(self.config.width, self.config.height),
            background_color=self.config.background_color,
        )

        print("Running simulation... (Close window to exit)")

        while gui.running:
            # Run multiple substeps for stability
            for _ in range(2):
                self.step()

            # Get particle data for rendering
            positions, colors, radii, types = self.get_particle_data()

            # Separate monomers and vesicles
            monomer_mask = types == 0  # ParticleType.MONOMER
            vesicle_mask = types == 1  # ParticleType.VESICLE

            # Render monomers (solid, colorful)
            if np.any(monomer_mask):
                monomer_pos = positions[monomer_mask]
                monomer_colors = colors[monomer_mask]
                monomer_radii = radii[monomer_mask]

                # Convert to hex
                colors_hex = (monomer_colors * 255).astype(int)
                colors_hex = (
                    (colors_hex[:, 0] << 16)
                    | (colors_hex[:, 1] << 8)
                    | colors_hex[:, 2]
                )

                gui.circles(monomer_pos, radius=monomer_radii, color=colors_hex)

            # Render vesicles (dark outline effect - draw with very dark color)
            if np.any(vesicle_mask):
                vesicle_pos = positions[vesicle_mask]
                vesicle_radii = radii[vesicle_mask]

                # Dark cyan outline color (low brightness for outline effect)
                vesicle_color_dark = 0x1A4D4D  # Dark teal

                gui.circles(vesicle_pos, radius=vesicle_radii, color=vesicle_color_dark)
            gui.show()

            self.frame += 1

            # Print stats periodically
            if self.frame % self.config.stats_print_interval == 0:
                self.print_stats()
