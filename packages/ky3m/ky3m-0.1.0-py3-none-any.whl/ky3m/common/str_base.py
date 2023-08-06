def str_base(number: int, base: str) -> str:
    (d, m) = divmod(number, len(base))
    if d > 0:
        return str_base(d, base) + base[m]
    return base[m]
