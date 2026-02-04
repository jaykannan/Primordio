import taichi as ti

# Initialize Taichi for GPU
ti.init(arch=ti.gpu)

# Simulation Parameters
width, height = 800, 800
n_particles = 15000
n_grid = 128

# Time step
dt = 0.016

# Particle fields
pos = ti.Vector.field(2, dtype=ti.f32, shape=n_particles)
vel = ti.Vector.field(2, dtype=ti.f32, shape=n_particles)
colors = ti.Vector.field(3, dtype=ti.f32, shape=n_particles)
mass = ti.field(dtype=ti.f32, shape=n_particles)  # Individual particle mass
particle_temp = ti.field(dtype=ti.f32, shape=n_particles)  # Individual particle temperature

# Fluid grid fields
velocity_field = ti.Vector.field(2, dtype=ti.f32, shape=(n_grid, n_grid))
temperature_field = ti.field(dtype=ti.f32, shape=(n_grid, n_grid))
pressure_field = ti.field(dtype=ti.f32, shape=(n_grid, n_grid))

# Temporary fields for advection
new_velocity = ti.Vector.field(2, dtype=ti.f32, shape=(n_grid, n_grid))
new_temperature = ti.field(dtype=ti.f32, shape=(n_grid, n_grid))

# Constants
cell_size = 1.0 / n_grid
buoyancy = 1.5  # Reduced from 5.0 to slow down convection
viscosity = 0.95  # Reduced from 0.999 to add more damping
diffusion = 0.995
heat_source_strength = 0.3
cooling_strength = 0.5  # Increased cooling at top
ambient_temp = 0.0  # Reference temperature for buoyancy

@ti.kernel
def init_particles():
    """Initialize all particles as hot/rising with random mass"""
    for i in pos:
        pos[i] = ti.Vector([ti.random(), ti.random()])

        # All particles start hot (rising state)
        particle_temp[i] = 0.5 + ti.random() * 0.5  # Temperature 0.5 to 1.0

        # Random mass - heavier particles cool faster and sink more
        mass[i] = 0.5 + ti.random() * 1.5  # Mass range: 0.5 to 2.0

        # Start with slight upward velocity (all rising initially)
        vel[i] = ti.Vector([0.0, ti.random() * 0.05])

        # Color based on initial temperature (all hot colors)
        colors[i] = ti.Vector([
            ti.min(1.0, 0.8 + particle_temp[i] * 0.2),
            ti.min(1.0, 0.3 + particle_temp[i] * 0.3),
            0.1
        ])  # Red/orange

@ti.kernel
def init_fluid():
    """Initialize fluid fields"""
    for i, j in velocity_field:
        velocity_field[i, j] = ti.Vector([0.0, 0.0])
        temperature_field[i, j] = 0.0
        pressure_field[i, j] = 0.0

@ti.func
def sample_bilinear(field: ti.template(), pos_x: ti.f32, pos_y: ti.f32):
    """Bilinear interpolation for sampling fields"""
    grid_pos_x = pos_x * n_grid - 0.5
    grid_pos_y = pos_y * n_grid - 0.5

    i = int(ti.floor(grid_pos_x))
    j = int(ti.floor(grid_pos_y))

    fx = grid_pos_x - i
    fy = grid_pos_y - j

    i = ti.max(0, ti.min(n_grid - 2, i))
    j = ti.max(0, ti.min(n_grid - 2, j))

    return (1 - fx) * (1 - fy) * field[i, j] + \
           fx * (1 - fy) * field[i + 1, j] + \
           (1 - fx) * fy * field[i, j + 1] + \
           fx * fy * field[i + 1, j + 1]

@ti.kernel
def apply_heat_sources():
    """Apply heat sources at the bottom (hydrothermal vents)"""
    for i, j in temperature_field:
        # Heat from bottom (many small geothermal vents)
        if j < 8:
            # Create many small heat plumes with noise pattern
            # Mix of different frequencies for varied vent sizes
            vent_pattern = (i % 8 < 3) or (i % 13 < 2) or (i % 21 < 3)
            if vent_pattern:
                # Vary strength by depth for spreading effect
                depth_factor = 1.0 - (j / 8.0)  # Stronger at bottom
                temperature_field[i, j] += heat_source_strength * depth_factor

        # Strong cooling at top (many small cooling zones)
        if j > n_grid - 12:
            # Similar pattern for cooling - non-uniform
            cool_pattern = (i % 7 < 3) or (i % 11 < 2) or (i % 19 < 3)
            if cool_pattern:
                # Vary strength by height for spreading effect
                height_factor = (j - (n_grid - 12)) / 12.0  # Stronger at top
                temperature_field[i, j] -= cooling_strength * height_factor

        # Ambient cooling (heat dissipation) - pull toward ambient temp
        temperature_field[i, j] *= diffusion

        # CRITICAL: Clamp temperature to reasonable bounds to prevent runaway
        temperature_field[i, j] = ti.max(-0.5, ti.min(1.0, temperature_field[i, j]))

@ti.kernel
def apply_buoyancy():
    """Apply buoyancy force based on temperature (hot rises, cool sinks)"""
    for i, j in velocity_field:
        # Buoyancy relative to ambient: positive temp rises, negative temp sinks
        temp_diff = temperature_field[i, j] - ambient_temp
        velocity_field[i, j].y += temp_diff * buoyancy * dt

        # Clamp velocity magnitude to prevent runaway speeds
        vel_mag = ti.sqrt(velocity_field[i, j].x**2 + velocity_field[i, j].y**2)
        if vel_mag > 0.5:  # Max velocity cap
            velocity_field[i, j] *= 0.5 / vel_mag

@ti.kernel
def advect_velocity():
    """Advect velocity field (self-advection)"""
    for i, j in velocity_field:
        pos_x = (i + 0.5) * cell_size
        pos_y = (j + 0.5) * cell_size

        # Backtrace
        vel_sample = velocity_field[i, j]
        prev_x = pos_x - vel_sample.x * dt
        prev_y = pos_y - vel_sample.y * dt

        # Clamp to domain
        prev_x = ti.max(0.0, ti.min(1.0, prev_x))
        prev_y = ti.max(0.0, ti.min(1.0, prev_y))

        new_velocity[i, j] = sample_bilinear(velocity_field, prev_x, prev_y)
        new_velocity[i, j] *= viscosity

@ti.kernel
def advect_temperature():
    """Advect temperature field"""
    for i, j in temperature_field:
        pos_x = (i + 0.5) * cell_size
        pos_y = (j + 0.5) * cell_size

        vel_sample = velocity_field[i, j]
        prev_x = pos_x - vel_sample.x * dt
        prev_y = pos_y - vel_sample.y * dt

        prev_x = ti.max(0.0, ti.min(1.0, prev_x))
        prev_y = ti.max(0.0, ti.min(1.0, prev_y))

        new_temperature[i, j] = sample_bilinear(temperature_field, prev_x, prev_y)

@ti.kernel
def copy_velocity():
    for i, j in velocity_field:
        velocity_field[i, j] = new_velocity[i, j]

@ti.kernel
def copy_temperature():
    for i, j in temperature_field:
        temperature_field[i, j] = new_temperature[i, j]

@ti.kernel
def enforce_boundaries():
    """Enforce boundary conditions"""
    for i, j in velocity_field:
        # No-slip boundaries
        if i == 0 or i == n_grid - 1:
            velocity_field[i, j].x = 0
        if j == 0 or j == n_grid - 1:
            velocity_field[i, j].y = 0

        # Clamp velocity magnitude to prevent extreme speeds
        vel_mag = ti.sqrt(velocity_field[i, j].x**2 + velocity_field[i, j].y**2)
        max_vel = 0.5
        if vel_mag > max_vel:
            velocity_field[i, j] *= max_vel / vel_mag

@ti.kernel
def add_turbulence():
    """Add random turbulence for mixing"""
    for i, j in velocity_field:
        # Reduced turbulence to allow clearer convection patterns
        if ti.random() < 0.005:
            velocity_field[i, j] += ti.Vector([
                (ti.random() - 0.5) * 0.2,
                (ti.random() - 0.5) * 0.2
            ])

def get_field_stats():
    """Get statistics about the simulation fields"""
    vel_field = velocity_field.to_numpy()
    temp_field = temperature_field.to_numpy()

    # Calculate velocity magnitudes
    vel_mag = (vel_field[:, :, 0]**2 + vel_field[:, :, 1]**2)**0.5

    stats = {
        'max_velocity': vel_mag.max(),
        'avg_velocity': vel_mag.mean(),
        'max_temp': temp_field.max(),
        'min_temp': temp_field.min(),
        'avg_temp': temp_field.mean(),
    }
    return stats

@ti.kernel
def update_particles():
    """Update particles with mass-based cooling and position-based heating"""
    for i in pos:
        y_pos = pos[i].y

        # Heat particles near the bottom (only when close to bottom)
        if y_pos < 0.15:
            # Reheat based on proximity to bottom
            heat_rate = (0.15 - y_pos) / 0.15  # Stronger near bottom
            particle_temp[i] += heat_rate * 0.02
            particle_temp[i] = ti.min(1.0, particle_temp[i])

        # Cool particles near the top (based on mass - heavier cools faster)
        if y_pos > 0.85:
            # Cooling rate depends on mass and proximity to top
            cool_rate = ((y_pos - 0.85) / 0.15) * mass[i] * 0.015
            particle_temp[i] -= cool_rate
            particle_temp[i] = ti.max(-0.5, particle_temp[i])

        # Buoyancy: hot rises, cold sinks (mass affects sinking speed)
        buoyancy_force = particle_temp[i] * 0.15  # Reduced from 0.3 - slower vertical
        gravity_force = -mass[i] * 0.025  # Reduced from 0.05 - slower sinking

        # Update velocity
        vel[i].y += (buoyancy_force + gravity_force) * dt

        # Damping to prevent extreme speeds
        vel[i] *= 0.98

        # Sample fluid velocity for some interaction
        fluid_vel = sample_bilinear(velocity_field, pos[i].x, pos[i].y)
        vel[i] += fluid_vel * 0.1 * dt  # Weak coupling to fluid

        # Cap velocity
        vel_mag = ti.sqrt(vel[i].x**2 + vel[i].y**2)
        max_vel = 0.15  # Reduced from 0.2
        if vel_mag > max_vel:
            vel[i] *= max_vel / vel_mag

        # Update position
        pos[i] += vel[i] * dt

        # Brownian motion - random molecular movement
        # Hotter particles have more thermal energy = more motion
        thermal_energy = ti.max(0.0, particle_temp[i] + 0.5)  # 0 to 1.5 range
        brownian_strength = 0.003 * thermal_energy

        # Random walk in both directions
        brownian_motion = ti.Vector([
            (ti.random() - 0.5) * brownian_strength,
            (ti.random() - 0.5) * brownian_strength
        ])
        pos[i] += brownian_motion

        # Wrap around boundaries
        if pos[i].x < 0: pos[i].x += 1.0
        if pos[i].x > 1: pos[i].x -= 1.0
        if pos[i].y < 0: pos[i].y += 1.0
        if pos[i].y > 1: pos[i].y -= 1.0

        # Update color based on particle temperature
        temp = particle_temp[i]

        if temp > 0.3:
            # Hot: red/orange
            colors[i] = ti.Vector([
                ti.min(1.0, 0.8 + temp * 0.2),
                ti.min(1.0, 0.3 + temp * 0.3),
                0.1
            ])
        elif temp > 0.1:
            # Warm: yellow
            colors[i] = ti.Vector([
                ti.min(1.0, 0.8 + temp * 2),
                ti.min(1.0, 0.8 + temp),
                0.3
            ])
        elif temp < -0.2:
            # Cold (sinking): dark blue
            colors[i] = ti.Vector([0.1, 0.3, 0.7])
        else:
            # Cool/Neutral: blue/cyan
            colors[i] = ti.Vector([0.3, 0.6, 0.9])

def step_simulation():
    """Single simulation step"""
    apply_heat_sources()
    apply_buoyancy()

    advect_velocity()
    copy_velocity()

    advect_temperature()
    copy_temperature()

    enforce_boundaries()
    add_turbulence()

    update_particles()

def main():
    print("Initializing Primordial Soup Simulation...")
    print(f"Particles: {n_particles}")
    print(f"Grid: {n_grid}x{n_grid}")

    # Initialize
    init_particles()
    init_fluid()

    # Create GUI
    gui = ti.GUI('Primordial Soup', res=(width, height), background_color=0x112233)

    print("Running simulation... (Close window to exit)")

    frame = 0
    while gui.running:
        # Run multiple substeps for stability
        for _ in range(2):
            step_simulation()

        # Render particles
        particle_positions = pos.to_numpy()
        particle_colors = colors.to_numpy()

        # Convert RGB colors to hex format for GUI
        particle_colors_hex = (particle_colors * 255).astype(int)
        particle_colors_hex = (particle_colors_hex[:, 0] << 16) | (particle_colors_hex[:, 1] << 8) | particle_colors_hex[:, 2]

        gui.circles(particle_positions, radius=2, color=particle_colors_hex)

        gui.show()
        frame += 1

        # Print debug stats every 50 frames
        if frame % 50 == 0:
            stats = get_field_stats()
            print(f"Frame {frame:4d} | "
                  f"Vel: max={stats['max_velocity']:.3f} avg={stats['avg_velocity']:.3f} | "
                  f"Temp: max={stats['max_temp']:.3f} min={stats['min_temp']:.3f} avg={stats['avg_temp']:.3f}")

if __name__ == '__main__':
    main()
