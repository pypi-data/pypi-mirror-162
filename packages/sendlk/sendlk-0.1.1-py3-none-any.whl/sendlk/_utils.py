from cryptography.fernet import Fernet
from sendlk import _app
from sendlk.exceptions import SendLKException
import random
from time import time

App = _app.App.get_instance()

def encrypt_token(length: int = 4, expire: int = 3) -> tuple:
    """
    Get the token to use.
    Arguments:
        length {int} -- length for the code.
        expire {int} -- The code expire time in minutes.
    Returns:
        str -- The token.
    """
    
    if not length or not isinstance(length, int):
        length = 4

    if not expire or not isinstance(expire, int) or expire < 1:
        expire = 3

    if length < 1:
        raise SendLKException(message="Length must be greater than 0.")

    digits = "0123456789"

    # Code Generator
    code = "".join(
        digits[random.randint(0, len(digits) - 1)] for _ in range(length)
    )

    # Time stamp
    milliseconds = int(time() * 1000)

    payload_string = f"{milliseconds}:{code}:{expire}"

    # Encrypt
    cipher_suite = Fernet(App.secret.encode())
    payload = cipher_suite.encrypt(payload_string.encode()).decode()

    return (payload, code)

def decrypt_token(token: str, verify_code: str) -> str:
    """
    Decrypt the token.
    Arguments:
        token {str} -- The token to decrypt.
        verify_code {str} -- The code to verify.
    Returns:
        str -- The decrypted code.
    """
    if not token or not isinstance(token, str):
        raise SendLKException(message="Invalid token.")
    if not verify_code or not isinstance(verify_code, str):
        raise SendLKException(message="Invalid code.")
    try:
        cipher_suite = Fernet(App.secret.encode())
        payload = cipher_suite.decrypt(token.encode()).decode()
        if not payload:
            raise SendLKException(message="Invalid token.")
        token_time, code, expire = payload.split(":")
        current_time = int(time() * 1000)
        if int(token_time) + int(expire) * 60000 < current_time:
            raise SendLKException(message="Token expired.")
        if code != verify_code:
            raise SendLKException(message="Invalid code.")
        return code
    except SendLKException as e:
        raise e
    except Exception as e:
        raise SendLKException(message=f"Error decrypting token: {e}") from e