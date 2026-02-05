"""Vesicle interaction mechanics - absorption, growth, and division."""

import taichi as ti
from config import SimulationConfig
from fields import SimulationFields
from chemistry import ParticleType


@ti.data_oriented
class VesicleSystem:
    """Handles vesicle-monomer and vesicle-vesicle interactions."""

    def __init__(self, config: SimulationConfig, fields: SimulationFields):
        self.config = config
        self.fields = fields

    @ti.kernel
    def absorb_monomers(self):
        """Vesicles absorb monomers on contact."""
        # Iterate through all vesicles
        for i in self.fields.pos:
            if self.fields.particle_type[i] != int(ParticleType.VESICLE):
                continue

            # Skip if vesicle is at max capacity
            if self.fields.radius[i] >= self.fields.radius_threshold[i]:
                continue

            vesicle_pos = self.fields.pos[i]
            vesicle_radius = self.fields.radius[i]
            # Convert radius from pixels to normalized coordinates (screen is 800x800)
            vesicle_radius_normalized = vesicle_radius / 800.0

            # Check all monomers for collision (use range-for to avoid nested struct-for)
            for j in range(self.config.n_particles):
                if self.fields.particle_type[j] != int(ParticleType.MONOMER):
                    continue

                # Skip if monomer is already absorbed
                if self.fields.parent_vesicle[j] >= 0:
                    continue

                monomer_pos = self.fields.pos[j]

                # Check distance (in normalized coordinates)
                dist = ti.sqrt(
                    (vesicle_pos.x - monomer_pos.x) ** 2
                    + (vesicle_pos.y - monomer_pos.y) ** 2
                )

                # If within vesicle radius, absorb it (compare in normalized space)
                if dist < vesicle_radius_normalized:
                    # Probabilistic absorption using per-vesicle rate (for variety)
                    if ti.random() < self.fields.absorption_rate[i]:
                        # Mark monomer as absorbed by this vesicle
                        self.fields.parent_vesicle[j] = i

                        # Set random offset within vesicle (in normalized coordinates)
                        scale = self.config.growth_factor * vesicle_radius_normalized
                        self.fields.offset[j] = ti.Vector([
                            (ti.random() - 0.5) * scale,
                            (ti.random() - 0.5) * scale,
                        ])

                        # Grow vesicle
                        self.fields.radius[i] += self.config.growth_per_monomer
                        self.fields.monomers_eaten[i] += 1
                    else:
                        # Absorption rejected - apply repulsion force
                        # Calculate direction from monomer to vesicle
                        if dist > 0.0001:  # Avoid division by zero
                            dir_x = (monomer_pos.x - vesicle_pos.x) / dist
                            dir_y = (monomer_pos.y - vesicle_pos.y) / dist

                            # Repulsion strength (stronger for closer particles)
                            repulsion_strength = self.config.absorption_rejection_repulsion * (1.0 - dist / vesicle_radius_normalized)

                            # Push vesicle away (horizontal bias: 2x horizontal force)
                            self.fields.vel[i].x -= dir_x * repulsion_strength * self.config.horizontal_force_bias
                            self.fields.vel[i].y -= dir_y * repulsion_strength

                            # Push monomer away (horizontal bias: 2x horizontal force)
                            self.fields.vel[j].x += dir_x * repulsion_strength * self.config.horizontal_force_bias
                            self.fields.vel[j].y += dir_y * repulsion_strength

    @ti.kernel
    def update_absorbed_monomers(self):
        """Update positions of absorbed monomers to follow their parent vesicle."""
        for i in range(self.config.n_particles):
            if self.fields.particle_type[i] != int(ParticleType.MONOMER):
                continue

            parent_id = self.fields.parent_vesicle[i]
            if parent_id < 0:
                continue  # Not absorbed

            # Position monomer relative to parent vesicle center
            parent_pos = self.fields.pos[parent_id]
            self.fields.pos[i] = parent_pos + self.fields.offset[i] * self.config.absorbed_monomer_offset_scale

            # Monomers inside vesicles don't move independently
            self.fields.vel[i] = ti.Vector([0.0, 0.0])

    @ti.func
    def calculate_vesicle_bias(self, vesicle_id: int) -> ti.types.vector(4, ti.f32):
        """Calculate aggregate bias scores for a vesicle based on its absorbed monomers.
        Returns [absorption_bias, division_bias, attraction_bias, repulsion_bias]."""
        absorption_sum = 0.0
        division_sum = 0.0
        attraction_sum = 0.0
        repulsion_sum = 0.0
        count = 0

        # Initialize averages to default values
        absorption_avg = self.config.default_bias_value
        division_avg = self.config.default_bias_value
        attraction_avg = self.config.default_bias_value
        repulsion_avg = self.config.default_bias_value

        # Sum bias scores from all absorbed monomers
        for i in range(self.config.n_particles):
            if self.fields.parent_vesicle[i] == vesicle_id:
                absorption_sum += self.fields.absorption_bias[i]
                division_sum += self.fields.division_bias[i]
                attraction_sum += self.fields.attraction_bias[i]
                repulsion_sum += self.fields.repulsion_bias[i]
                count += 1

        # Calculate averages if we have monomers
        if count > 0:
            absorption_avg = absorption_sum / count
            division_avg = division_sum / count
            attraction_avg = attraction_sum / count
            repulsion_avg = repulsion_sum / count

        return ti.Vector([absorption_avg, division_avg, attraction_avg, repulsion_avg])

    @ti.kernel
    def vesicle_competition(self):
        """Larger vesicles absorb smaller ones based on monomer composition."""
        # Iterate through all vesicles
        for i in self.fields.pos:
            if self.fields.particle_type[i] != int(ParticleType.VESICLE):
                continue

            # Skip dead vesicles
            if self.fields.radius[i] < self.config.death_radius:
                continue

            vesicle_i_pos = self.fields.pos[i]
            vesicle_i_radius = self.fields.radius[i]
            vesicle_i_radius_norm = vesicle_i_radius / 800.0

            # Calculate vesicle i's aggregate bias
            bias_i = self.calculate_vesicle_bias(i)
            absorption_bias_i = bias_i[0]

            # Check all other vesicles
            for j in range(self.config.n_particles):
                if j == i:
                    continue

                if self.fields.particle_type[j] != int(ParticleType.VESICLE):
                    continue

                # Skip dead vesicles
                if self.fields.radius[j] < self.config.death_radius:
                    continue

                vesicle_j_pos = self.fields.pos[j]
                vesicle_j_radius = self.fields.radius[j]
                vesicle_j_radius_norm = vesicle_j_radius / 800.0

                # Check distance
                dist = ti.sqrt(
                    (vesicle_i_pos.x - vesicle_j_pos.x) ** 2
                    + (vesicle_i_pos.y - vesicle_j_pos.y) ** 2
                )

                # If vesicles are colliding
                collision_dist = vesicle_i_radius_norm + vesicle_j_radius_norm
                if dist < collision_dist:
                    # Calculate vesicle j's aggregate bias
                    bias_j = self.calculate_vesicle_bias(j)
                    absorption_bias_j = bias_j[0]
                    resistance_j = bias_j[3]  # repulsion_bias acts as absorption resistance

                    # Determine winner based on size AND absorption bias vs resistance
                    # Higher absorption bias gives competitive advantage
                    # Higher resistance makes vesicle harder to absorb
                    effective_size_i = vesicle_i_radius * (self.config.absorption_bias_base + absorption_bias_i)
                    effective_size_j = vesicle_j_radius * (self.config.absorption_bias_base + absorption_bias_j) * (1.0 + resistance_j * self.config.resistance_multiplier)

                    # If i is dominant, absorb j
                    if effective_size_i > effective_size_j:
                        # Transfer monomers from j to i (limited rate per frame)
                        monomers_transferred = 0
                        for k in range(self.config.n_particles):
                            if monomers_transferred >= self.config.monomer_move_rate:
                                break

                            # If monomer belongs to vesicle j, transfer to i
                            if self.fields.parent_vesicle[k] == j:
                                self.fields.parent_vesicle[k] = i

                                # Randomize offset within new parent
                                scale = self.config.growth_factor * vesicle_i_radius_norm
                                self.fields.offset[k] = ti.Vector([
                                    (ti.random() - 0.5) * scale,
                                    (ti.random() - 0.5) * scale,
                                ])

                                monomers_transferred += 1

                        # Shrink j, grow i
                        transfer_size = ti.min(
                            vesicle_j_radius * self.config.transfer_size_fraction,
                            self.config.growth_per_monomer * self.config.monomer_move_rate
                        )
                        self.fields.radius[j] -= transfer_size
                        self.fields.radius[i] += transfer_size * self.config.growth_efficiency

                        # Update stats
                        self.fields.monomers_eaten[i] += monomers_transferred
                        self.fields.monomers_eaten[j] = ti.max(0, self.fields.monomers_eaten[j] - monomers_transferred)

    @ti.kernel
    def vesicle_division(self):
        """Vesicles divide when they reach division size, based on division bias.
        Larger vesicles split into more children: 2-way, 3-way, or 4-way splits."""
        for i in self.fields.pos:
            if self.fields.particle_type[i] != int(ParticleType.VESICLE):
                continue

            # Skip if not large enough
            if self.fields.radius[i] < self.config.division_size_min:
                continue

            # Calculate division bias
            bias = self.calculate_vesicle_bias(i)
            division_bias = bias[1]

            # Probabilistic division based on bias (higher bias = more likely)
            division_probability = division_bias * self.config.mechanical_event_probability
            if ti.random() < division_probability:
                parent_radius = self.fields.radius[i]

                # Determine number of children based on size
                num_children = 2  # Default: 2-way split
                if parent_radius > self.config.division_3way_max:
                    num_children = 4  # Large vesicles: 4-way split
                elif parent_radius > self.config.division_2way_max:
                    num_children = 3  # Medium vesicles: 3-way split

                # Find empty slots for all children
                child_slots = ti.Vector([-1, -1, -1, -1])  # Max 4 children
                slots_found = 0

                for j in range(self.config.n_particles):
                    if slots_found >= num_children:
                        break

                    # Look for dead vesicles to repurpose
                    if self.fields.particle_type[j] == int(ParticleType.VESICLE) and self.fields.radius[j] < self.config.death_radius:
                        child_slots[slots_found] = j
                        slots_found += 1

                # Only proceed if we found enough slots
                if slots_found >= num_children:
                    # Calculate child radius (conserve area: A_parent = N * A_child)
                    # For circles: π*r_p² = N * π*r_c² → r_c = r_p / sqrt(N)
                    child_radius = parent_radius / ti.sqrt(float(num_children))

                    # Calculate monomers per child
                    total_monomers = self.fields.monomers_eaten[i]
                    monomers_per_child = total_monomers // num_children

                    # Get parent bias for push calculations
                    parent_bias = self.calculate_vesicle_bias(i)

                    # Create all children positioned in a circle around parent
                    for child_idx in range(num_children):
                        j = child_slots[child_idx]

                        # Position in a circle around parent (evenly spaced angles)
                        angle = (float(child_idx) / float(num_children)) * 6.28318  # 2*pi
                        offset_distance = self.config.division_offset_range * 2.0  # Larger spread for multi-way
                        offset_x = ti.cos(angle) * offset_distance
                        offset_y = ti.sin(angle) * offset_distance
                        self.fields.pos[j] = self.fields.pos[i] + ti.Vector([offset_x, offset_y])

                        # Set child radius
                        self.fields.radius[j] = child_radius

                        # Initialize child properties
                        self.fields.particle_type[j] = int(ParticleType.VESICLE)
                        self.fields.radius_threshold[j] = self.config.division_size_min
                        self.fields.vel[j] = self.fields.vel[i] * self.config.division_velocity_inheritance
                        self.fields.colors[j] = ti.Vector([0.2, 0.8, 0.8])
                        self.fields.absorption_rate[j] = self.config.absorption_rate_min + ti.random() * (self.config.absorption_rate_max - self.config.absorption_rate_min)

                        # Transfer monomers to this child
                        monomers_transferred = 0
                        for k in range(self.config.n_particles):
                            if monomers_transferred >= monomers_per_child:
                                break

                            if self.fields.parent_vesicle[k] == i:
                                # Transfer to new vesicle
                                self.fields.parent_vesicle[k] = j
                                monomers_transferred += 1

                                # Randomize offset within new parent
                                scale = self.config.growth_factor * child_radius / 800.0
                                self.fields.offset[k] = ti.Vector([
                                    (ti.random() - 0.5) * scale,
                                    (ti.random() - 0.5) * scale,
                                ])

                        self.fields.monomers_eaten[j] = monomers_transferred

                    # Update parent (becomes first child)
                    self.fields.radius[i] = child_radius
                    self.fields.monomers_eaten[i] = total_monomers - (monomers_per_child * (num_children - 1))

                    # Apply violent mutual repulsion between all children (including parent)
                    # Collect all child IDs including parent
                    all_children = ti.Vector([-1, -1, -1, -1])
                    all_children[0] = i  # Parent becomes first child
                    for idx in range(num_children - 1):
                        all_children[idx + 1] = child_slots[idx]

                    # Apply repulsion between all pairs
                    for idx_a in range(num_children):
                        vesicle_a = all_children[idx_a]
                        bias_a = self.calculate_vesicle_bias(vesicle_a)

                        for idx_b in range(idx_a + 1, num_children):
                            vesicle_b = all_children[idx_b]
                            bias_b = self.calculate_vesicle_bias(vesicle_b)

                            # Violent size-scaled push - scales with original parent size²
                            # Multi-way splits are even more explosive (extra 1.5× multiplier)
                            size_factor = parent_radius * parent_radius * 1.5
                            push_strength = (bias_a[3] + bias_b[3]) * self.config.division_push_strength * size_factor

                            # Direction from a to b
                            dir_x = self.fields.pos[vesicle_b].x - self.fields.pos[vesicle_a].x
                            dir_y = self.fields.pos[vesicle_b].y - self.fields.pos[vesicle_a].y
                            dist = ti.sqrt(dir_x * dir_x + dir_y * dir_y)

                            if dist > 0.0001:
                                dir_x /= dist
                                dir_y /= dist

                                # Push them apart (horizontal bias)
                                self.fields.vel[vesicle_a].x -= dir_x * push_strength * self.config.horizontal_force_bias
                                self.fields.vel[vesicle_a].y -= dir_y * push_strength
                                self.fields.vel[vesicle_b].x += dir_x * push_strength * self.config.horizontal_force_bias
                                self.fields.vel[vesicle_b].y += dir_y * push_strength

    @ti.kernel
    def vesicle_interactions(self):
        """Attraction and repulsion between vesicles based on monomer composition."""
        for i in self.fields.pos:
            if self.fields.particle_type[i] != int(ParticleType.VESICLE):
                continue

            if self.fields.radius[i] < self.config.death_radius:
                continue

            vesicle_i_pos = self.fields.pos[i]
            bias_i = self.calculate_vesicle_bias(i)
            attraction_bias_i = bias_i[2]
            repulsion_bias_i = bias_i[3]

            # Check other vesicles
            for j in range(self.config.n_particles):
                if j == i:
                    continue

                if self.fields.particle_type[j] != int(ParticleType.VESICLE):
                    continue

                if self.fields.radius[j] < self.config.death_radius:
                    continue

                vesicle_j_pos = self.fields.pos[j]

                # Calculate distance
                dist = ti.sqrt(
                    (vesicle_i_pos.x - vesicle_j_pos.x) ** 2
                    + (vesicle_i_pos.y - vesicle_j_pos.y) ** 2
                )

                if dist > 0.0001 and dist < self.config.interaction_range:
                    # Calculate j's biases
                    bias_j = self.calculate_vesicle_bias(j)
                    attraction_bias_j = bias_j[2]
                    repulsion_bias_j = bias_j[3]

                    # Direction from i to j
                    dir_x = (vesicle_j_pos.x - vesicle_i_pos.x) / dist
                    dir_y = (vesicle_j_pos.y - vesicle_i_pos.y) / dist

                    # Calculate size similarity for ambient pressure effects
                    vesicle_i_radius = self.fields.radius[i]
                    vesicle_j_radius = self.fields.radius[j]
                    # Size ratio: 1.0 = identical sizes, 0.0 = very different
                    size_ratio = ti.min(vesicle_i_radius, vesicle_j_radius) / ti.max(vesicle_i_radius, vesicle_j_radius)

                    # Ambient pressure: stronger repulsion for similar-sized vesicles
                    # Simulates fluid mechanics and pressure equilibrium
                    ambient_pressure = size_ratio * self.config.ambient_pressure_strength

                    # Net attraction/repulsion based on both vesicles' biases
                    attraction_strength = (attraction_bias_i + attraction_bias_j) * self.config.attraction_strength_multiplier
                    repulsion_strength = (repulsion_bias_i + repulsion_bias_j) * self.config.repulsion_strength_multiplier + ambient_pressure

                    # Net force (positive = attract, negative = repel)
                    net_force = attraction_strength - repulsion_strength

                    # Apply force (horizontal bias)
                    self.fields.vel[i].x += dir_x * net_force * self.config.horizontal_force_bias
                    self.fields.vel[i].y += dir_y * net_force
