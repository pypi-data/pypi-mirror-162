def generate_store_app_id(store_name):
    """
    Generate a store app id.
    """

    return f"{store_name}-store"


def generate_store_app_key(store_name: str, length: int = 32):
    """
    Generate a store app key.
    """

    from .passwords import generate_random_password

    random_key = generate_random_password(length)

    store_name_hash = hash(store_name)

    return f"{store_name_hash}/{random_key}"
