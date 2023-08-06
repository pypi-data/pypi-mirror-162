"""Send.lk SDK for Python."""
import datetime
import json
import os

from sendlk import _app

App = _app.App

def initialize(token: str = None, secret: str = None):
    """Initialize the SDK.

    Args:
        token (str): The token to use.
        secret (str): The secret to use.
    """
    if token is None:
        raise ValueError("Token is required.")

    if not isinstance(token, str):
        raise TypeError("Token must be a string.")
    
    if secret is None:
        raise ValueError("Secret is required.")
    
    if not isinstance(secret, str):
        raise TypeError("Secret must be a string.")
    
    App(token, secret)

