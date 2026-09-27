import secrets

# Excludes 0/O and 1/I to avoid confusion when read aloud or handwritten.
ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"


def generate_tracking_code(length: int = 8) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))