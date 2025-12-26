from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class HonorLevelSnapshot:
    total_success_tasks: int
    level_star: int
    level_moon: int
    level_sun: int
    level_diamond: int
    level_crown: int


def calculate_honor_levels(
    total_success_tasks: int,
) -> HonorLevelSnapshot:
    """
    v1.0.30
    基于 total_success_tasks 计算五段荣誉等级（5 进制派生）
    """

    if total_success_tasks < 0:
        raise ValueError("total_success_tasks must be >= 0")

    total_stars = total_success_tasks // 10

    level_star = total_stars % 5
    level_moon = (total_stars // 5) % 5
    level_sun = (total_stars // 25) % 5
    level_diamond = (total_stars // 125) % 5
    level_crown = (total_stars // 625) % 5

    return HonorLevelSnapshot(
        total_success_tasks=total_success_tasks,
        level_star=level_star,
        level_moon=level_moon,
        level_sun=level_sun,
        level_diamond=level_diamond,
        level_crown=level_crown,
    )
