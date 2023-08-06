"""
Module for handling keys.

"""

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from .echo import echo


def generate_private_public_keys(key_size: int = 2048) -> tuple:
    """
    Generates a private and public key pair.
    """

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


def write_private_key_to_file(private_key: rsa.RSAPrivateKey, file_path: str) -> None:
    """
    Writes the private key to a file.
    """

    try:
        with open(file_path, "wb+") as key_file:
            key_file.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
            return True
    except Exception as _:
        return False


def write_public_key_to_file(public_key: rsa.RSAPublicKey, file_path: str) -> None:
    """
    Writes the public key to a file.
    """

    try:

        with open(file_path, "wb+") as key_file:
            key_file.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
            return True
    except Exception as _:
        return False


def write_all_the_keys(accolade_base_store_path: str):
    """
    Writes all the keys to files.
    """

    try:
        echo("Generating 🔑️ for security...")

        jwt_private_key, jwt_public_key = generate_private_public_keys()

        echo("😀️ Writing JWT 🔑️ to file...")

        write_private_key_to_file(jwt_private_key, f"{accolade_base_store_path}/keys/jwt/private.pem")
        write_public_key_to_file(jwt_public_key, f"{accolade_base_store_path}/keys/jwt/public.pem")

        echo("JWT 🔑️ Done!")

        echo("Generating Microservices Commnication 🔑️ for security...")

        communication_private_key, communication_public_key = generate_private_public_keys()

        echo("😀️ Writing Microservices Commnication 🔑️ to file...")

        write_private_key_to_file(communication_private_key, f"{accolade_base_store_path}/keys/communication/private.pem")
        write_public_key_to_file(communication_public_key, f"{accolade_base_store_path}/keys/communication/public.pem")

        echo("Microservices Commnication 🔑️ Done!")

        echo("Generating Guest 🔑️ for security...")

        guest_private_key, guest_public_key = generate_private_public_keys()

        echo("😀️ Writing Guest 🔑️ to file...")

        write_private_key_to_file(guest_private_key, f"{accolade_base_store_path}/keys/guest/private.pem")
        write_public_key_to_file(guest_public_key, f"{accolade_base_store_path}/keys/guest/public.pem")

        echo("Guest 🔑️ Done!")

        return True
    
    except Exception as _:
        return False