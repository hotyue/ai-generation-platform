def is_strength_upgrade(
    before_total_success_tasks: int,
    after_total_success_tasks: int,
) -> bool:
    """
    v1.0.30
    判定是否发生一次强度晋级（total_stars +1）
    """
    if before_total_success_tasks < 0 or after_total_success_tasks < 0:
        return False

    before_total_stars = before_total_success_tasks // 10
    after_total_stars = after_total_success_tasks // 10

    return after_total_stars == before_total_stars + 1
