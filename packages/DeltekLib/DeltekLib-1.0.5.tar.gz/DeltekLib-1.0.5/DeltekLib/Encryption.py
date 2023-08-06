import hashlib
import secrets
import string
from typing import Optional


def generate_secret_key(
        length: int,
        special_characters: Optional[str] = "!@#$%^&*()_+-=[]{}|'"
) -> string:
    """
    Generates a secret key string based on the standard keys found on ordinary keyboards added by special characters
    of your choice

    Symmetric encryption is also called secret key encryption, and it uses just one key, called a shared secret,
    for both encrypting and decrypting.

    :param length: specifies the length of the key to be generated
    :param special_characters: series of special characters you can add along the standard keys used, if not specified,
    the default special characters will be used instead
    :return: Symmetric Encrypted String

    *Examples:*
    | Generate Secret Key | 15
    | Generate Secret Key | 15 | special_characters=!@#$%
    """

    length = int(length)
    lower_case = string.ascii_lowercase
    upper_case = string.ascii_uppercase
    numbers = string.digits
    combined_characters = lower_case + upper_case + numbers + special_characters
    secret = ''.join(secrets.choice(combined_characters) for i in range(length))
    return secret


def generate_hash(*strings) -> string:
    """
    Generates hash key based on strings passed along as parameters

    :param strings: list of strings to generate a hashed string from
    :return: Hashed String

    *Examples:*
    | Generate Hash | Richard | Sanchez
    | Generate Hash | Richard | Sanchez | Deltek | Automation
    """

    string_to_hash = "".join(strings)
    return hashlib.sha256(string_to_hash.encode()).hexdigest()
