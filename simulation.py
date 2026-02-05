"""Main simulation orchestration."""

import numpy as np
import taichi as ti
from config import SimulationConfig
from fields import SimulationFields
from particles import ParticleSystem
from physics import FluidPhysics
from vesicles import VesicleSystem


class PrimordialSoupSimulation:
    """Orchestrates the complete simulation."""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.fields = SimulationFields(config)
        self.physics = FluidPhysics(config, self.fields)
        self.particles = ParticleSystem(config, self.fields, self.physics)
        self.vesicles = VesicleSystem(config, self.fields)
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

        # Vesicle absorption mechanics
        self.vesicles.absorb_monomers()
        self.vesicles.update_absorbed_monomers()

        # Polymerization: internal pressure causes monomers to form polymer chains
        self.vesicles.polymerize_monomers()

        # Vesicle-vesicle interactions (competition, division, attraction/repulsion)
        self.vesicles.vesicle_competition()
        self.vesicles.vesicle_division()
        self.vesicles.vesicle_interactions()

    def get_stats(self) -> dict:
        """Get simulation statistics."""
        vel_field = self.fields.velocity_field.to_numpy()
        temp_field = self.fields.temperature_field.to_numpy()
        parents = self.fields.parent_vesicle.to_numpy()
        radii = self.fields.radius.to_numpy()
        types = self.fields.particle_type.to_numpy()
        polymer_levels = self.fields.polymer_level.to_numpy()

        vel_mag = (vel_field[:, :, 0] ** 2 + vel_field[:, :, 1] ** 2) ** 0.5

        # Count absorbed monomers
        absorbed_count = (parents >= 0).sum()

        # Get vesicle stats (only count living vesicles)
        vesicle_mask = (types == 1) & (radii >= self.config.death_radius)
        vesicle_count = vesicle_mask.sum()
        avg_vesicle_radius = radii[vesicle_mask].mean() if vesicle_mask.any() else 0
        max_vesicle_radius = radii[vesicle_mask].max() if vesicle_mask.any() else 0
        avg_polymer_level = polymer_levels[vesicle_mask].mean() if vesicle_mask.any() else 0
        max_polymer_level = polymer_levels[vesicle_mask].max() if vesicle_mask.any() else 0

        return {
            "max_velocity": vel_mag.max(),
            "avg_velocity": vel_mag.mean(),
            "max_temp": temp_field.max(),
            "min_temp": temp_field.min(),
            "avg_temp": temp_field.mean(),
            "absorbed_monomers": absorbed_count,
            "vesicle_count": vesicle_count,
            "avg_vesicle_radius": avg_vesicle_radius,
            "max_vesicle_radius": max_vesicle_radius,
            "avg_polymer_level": avg_polymer_level,
            "max_polymer_level": max_polymer_level,
        }

    def print_stats(self):
        """Print simulation statistics."""
        stats = self.get_stats()
        print(
            f"Frame {self.frame:4d} | "
            f"Vesicles: {stats['vesicle_count']:2d} | "
            f"Absorbed: {stats['absorbed_monomers']:4d} | "
            f"Vesicle R: avg={stats['avg_vesicle_radius']:.1f} max={stats['max_vesicle_radius']:.1f} | "
            f"Polymer: avg={stats['avg_polymer_level']:.2f} max={stats['max_polymer_level']:.2f} | "
            f"Vel: max={stats['max_velocity']:.3f}"
        )

    def get_particle_data(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Get particle positions, colors, radii, types, and parent vesicle IDs for rendering."""
        positions = self.fields.pos.to_numpy()
        colors = self.fields.colors.to_numpy()
        radii = self.fields.radius.to_numpy()
        types = self.fields.particle_type.to_numpy()
        parents = self.fields.parent_vesicle.to_numpy()
        return positions, colors, radii, types, parents

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
            positions, colors, radii, types, parents = self.get_particle_data()

            # Separate free monomers, absorbed monomers, and vesicles
            monomer_mask = types == 0  # ParticleType.MONOMER
            vesicle_mask = types == 1  # ParticleType.VESICLE
            free_monomer_mask = monomer_mask & (parents < 0)  # Free monomers
            absorbed_monomer_mask = monomer_mask & (parents >= 0)  # Absorbed monomers

            # RENDER ORDER: free monomers → vesicles → absorbed monomers

            # 1. Render free monomers (solid, colorful)
            if np.any(free_monomer_mask):
                free_pos = positions[free_monomer_mask]
                free_colors = colors[free_monomer_mask]
                free_radii = radii[free_monomer_mask]

                # Convert to hex
                colors_hex = (free_colors * 255).astype(int)
                colors_hex = (
                    (colors_hex[:, 0] << 16)
                    | (colors_hex[:, 1] << 8)
                    | colors_hex[:, 2]
                )

                gui.circles(free_pos, radius=free_radii, color=colors_hex)

            # 2. Render vesicles as outlined circles (ring effect)
            if np.any(vesicle_mask):
                vesicle_pos = positions[vesicle_mask]
                vesicle_radii = radii[vesicle_mask]

                # Draw outer circle (cyan border)
                vesicle_color = 0x33CCCC  # Bright cyan
                gui.circles(vesicle_pos, radius=vesicle_radii, color=vesicle_color)

                # Draw inner circle (background color) to create hollow effect
                inner_radii = vesicle_radii * 0.92  # 92% of outer radius (thinner border)
                gui.circles(
                    vesicle_pos, radius=inner_radii, color=self.config.background_color
                )

            # 3. Render absorbed monomers (drawn above vesicles, visible inside)
            if np.any(absorbed_monomer_mask):
                absorbed_pos = positions[absorbed_monomer_mask]
                absorbed_colors = colors[absorbed_monomer_mask]
                absorbed_radii = radii[absorbed_monomer_mask]

                # Convert to hex
                colors_hex = (absorbed_colors * 255).astype(int)
                colors_hex = (
                    (colors_hex[:, 0] << 16)
                    | (colors_hex[:, 1] << 8)
                    | colors_hex[:, 2]
                )

                gui.circles(absorbed_pos, radius=absorbed_radii, color=colors_hex)
            gui.show()

            self.frame += 1

            # Print stats periodically
            if self.frame % self.config.stats_print_interval == 0:
                self.print_stats()
