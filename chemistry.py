"""Chemical properties and monomer types for abiogenesis simulation."""

from enum import IntEnum


class ChemicalProperty(IntEnum):
    """Chemical properties that affect monomer behavior."""

    NONE = 0  # No special behavior
    ATTACH = 1  # Attach adjacent monomers (Blue)
    SUBTRACT = 2  # Remove type from polymer (Black)
    ATTRACT = 3  # Move toward type (HotPink)
    REPEL = 4  # Move away from type (Olive)
    SPLIT = 5  # Split polymer at this point (Brown)
    COMBINE = 6  # Combine to same chain (Purple)
    COPY = 7  # Copy to type (Red)
    INCREASE_PH = 8  # Increase pH (Orange)
    DECREASE_PH = 9  # Decrease pH (Yellow)


# Color mapping for chemical properties (RGB normalized 0-1)
PROPERTY_COLORS = {
    ChemicalProperty.NONE: (0.5, 0.5, 0.8),  # Default blue
    ChemicalProperty.ATTACH: (0.0, 0.0, 1.0),  # Blue
    ChemicalProperty.SUBTRACT: (0.0, 0.0, 0.0),  # Black
    ChemicalProperty.ATTRACT: (1.0, 0.41, 0.71),  # HotPink
    ChemicalProperty.REPEL: (0.5, 0.5, 0.0),  # Olive
    ChemicalProperty.SPLIT: (0.65, 0.16, 0.16),  # Brown
    ChemicalProperty.COMBINE: (0.5, 0.0, 0.5),  # Purple
    ChemicalProperty.COPY: (1.0, 0.0, 0.0),  # Red
    ChemicalProperty.INCREASE_PH: (1.0, 0.65, 0.0),  # Orange
    ChemicalProperty.DECREASE_PH: (1.0, 1.0, 0.0),  # Yellow
}


class ParticleType(IntEnum):
    """Types of particles in the simulation."""

    MONOMER = 0  # Free-floating chemical unit
    VESICLE = 1  # Protocell containing monomers
    ABSORBED = 2  # Marked for deletion


# Number of different monomer types (0-9)
NUM_MONOMER_TYPES = 10
