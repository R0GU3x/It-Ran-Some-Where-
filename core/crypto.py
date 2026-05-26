import base64

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization


def generate_key_pair(key_size: int = 2048):
    """
    Generate an RSA private/public key pair.

    Returns:
        (private_key, public_key)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size
    )

    public_key = private_key.public_key()

    return private_key, public_key


def encryption(public_key, data: bytes) -> bytes:
    """
    Encrypt bytes using the public key and return a Base64 string.

    Args:
        public_key: RSA public key object
        data: plaintext bytes

    Returns:
        Base64-encoded ciphertext string
    """
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # return base64.b64encode(ciphertext).decode("utf-8")
    return base64.b64encode(ciphertext)


# def decryption(private_key, cipher_b64: str) -> bytes:
def decryption(private_key, cipher_b64: str) -> bytes:
    """
    Decrypt a Base64 ciphertext string using the private key.

    Args:
        private_key: RSA private key object
        cipher_b64: Base64-encoded ciphertext

    Returns:
        Plaintext bytes
    """
    ciphertext = base64.b64decode(cipher_b64)

    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return plaintext
    # return plaintext.decode('utf-8')


# Optional helper functions for key serialization

def private_key_to_pem(private_key) -> bytes:
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )


def public_key_to_pem(public_key) -> bytes:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


def load_private_key(pem_data: bytes):
    return serialization.load_pem_private_key(
        pem_data,
        password=None
    )


def load_public_key(pem_data: bytes):
    return serialization.load_pem_public_key(
        pem_data
    )


if __name__ == "__main__":
    private_key, public_key = generate_key_pair()

    data = b"Hello, world!"

    encrypted = encryption(public_key, data)
    print("Encrypted:", encrypted)

    decrypted = decryption(private_key, encrypted)
    print("Decrypted:", decrypted)