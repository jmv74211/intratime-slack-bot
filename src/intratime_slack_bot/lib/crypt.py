import base64
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

from intratime_slack_bot.config import settings

# ----------------------------------------------------------------------------------------------------------------------


def generate_cipher_key(password=settings.CIPHER_KEY):
    """
    Function to generate the key hash needed to encrypt the password

    Parameters
    ----------
    password: str
        Password. It must be 16 || 32 characters long

    Returns
    ------
    key: bytes
        Key hash
    """

    salt = b"\xf6A\x99\x8b\xf4\x92C\x14y\xf2\xd0\xdb\x94d\xbf\t"

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )

    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

    return key

# ----------------------------------------------------------------------------------------------------------------------


def encrypt(text, password=settings.CIPHER_KEY):
    """
    Function to encrypt a text, like a password

    Parameters
    ----------
    text: str
        Text to cipher
    password: str
        Password. It must be 16 || 32 characters long

    Returns
    -------
    ciphered_text: str
        Ciphered text
    """
    cipher = Fernet(generate_cipher_key(password))
    ciphered_text = cipher.encrypt(text.encode()).decode()

    return ciphered_text

# ----------------------------------------------------------------------------------------------------------------------


def decrypt(encrypted_text, password=settings.CIPHER_KEY):
    """
    Function to decrypt a ciphered text

    Parameters
    ----------
    encrypted_text: str
        Text to decipher
    password: str
        Password. It must be 16 || 32 characters long

    Returns
    -------
    deciphered_text: str
        Deciphered text
    """
    cipher = Fernet(generate_cipher_key(password))
    deciphered_text = cipher.decrypt(encrypted_text.encode()).decode()

    return deciphered_text
