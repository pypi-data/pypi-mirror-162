def generate_random_password(length: int = 16) -> str:
    """
    Generates a random password.
    """

    import string
    import random

    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def generate_django_secret_key(length: int = 32) -> str:
    """
    Generates a random django secret key.
    """

    import string
    import random

    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
