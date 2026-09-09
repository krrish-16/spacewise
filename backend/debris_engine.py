"""SpaceWise debris and collision simulation engine."""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass
class Debris:
    debris_id: str
    position: List[float]
    velocity: List[float]


SATELLITE_POSITION = [0.0, 0.0, 0.0]

# Demo trajectory: starts at 10 km and moves toward the satellite.
DEBRIS = Debris(
    debris_id="DEBRIS-4092",
    position=[10.0, 0.0, 0.0],
    velocity=[-0.02, 0.0, 0.0],
)

IMMINENT_THRESHOLD_KM = 2.0
WARNING_THRESHOLD_KM = 5.0


def euclidean_distance_3d(a: List[float], b: List[float]) -> float:
    """Return 3D Euclidean distance in km."""
    if len(a) != 3 or len(b) != 3:
        raise ValueError("Coordinates must contain exactly [x, y, z].")

    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def estimate_time_to_impact_sec(distance_km: float, velocity: List[float]) -> int:
    """Simple straight-line demo estimate, not real orbital mechanics."""
    speed_km_s = math.sqrt(sum(v * v for v in velocity))
    if speed_km_s <= 0:
        return 999999

    return max(0, round(distance_km / speed_km_s))


def advance_debris(seconds: int = 20) -> Dict:
    """Move debris along its mock trajectory."""
    for i in range(3):
        DEBRIS.position[i] += DEBRIS.velocity[i] * seconds

    # Prevent the demo object from passing through the spacecraft.
    distance = euclidean_distance_3d(DEBRIS.position, SATELLITE_POSITION)
    if distance < 0.5:
        DEBRIS.position = [0.5, 0.0, 0.0]

    return check_debris()


def reset_debris() -> Dict:
    """Reset the demo debris to 10 km."""
    DEBRIS.position = [10.0, 0.0, 0.0]
    return check_debris()


def trigger_approach() -> Dict:
    """Move debris rapidly toward the spacecraft for a demo button."""
    distance = euclidean_distance_3d(DEBRIS.position, SATELLITE_POSITION)

    if distance > 7.0:
        seconds = 100
    elif distance > 4.0:
        seconds = 80
    elif distance > 2.0:
        seconds = 50
    else:
        seconds = 10

    return advance_debris(seconds)


def check_debris() -> Dict:
    """Return the collision_data object matching the team contract."""
    distance = euclidean_distance_3d(DEBRIS.position, SATELLITE_POSITION)
    time_to_impact = estimate_time_to_impact_sec(distance, DEBRIS.velocity)

    return {
        "imminent": distance < IMMINENT_THRESHOLD_KM,
        "distance_km": round(distance, 2),
        "time_to_impact_sec": time_to_impact,
        "debris_id": DEBRIS.debris_id,
        "warning": distance < WARNING_THRESHOLD_KM,
        "satellite_position": SATELLITE_POSITION,
        "debris_position": [round(x, 3) for x in DEBRIS.position],
    }
