def bump_difficulty(current: int, delta: int) -> int:
    """Bump difficulty up or down, keeping it within 1-5 bounds."""
    return max(1, min(5, current + delta))