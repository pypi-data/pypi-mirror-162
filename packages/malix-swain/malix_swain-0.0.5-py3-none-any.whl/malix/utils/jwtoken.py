import requests
import json
from .attributes import Token
from .exceptions import InvalidCredentials

def get_token(address: str = None, password: str = None):
    """Returns a :class:`Token <malix.utils.attributes.Token>` object for the given credentials.

    :param address: Address of the account.
    :param password: Passowrd of the account.
    :type address: str
    :type password: str

    :returns: :class:`Token <malix.utils.attributes.Token>` object

    :raises InvalidCredentials: Raises when given credentials are invalid.
    :type InvalidCredentials: :class:`InvalidCredentials <malix.utils.exceptions.InvalidCredentials>`

    """
    headers = {
        "Content-Type": "application/ld+json",
        "accept": "application/ld+json"
    }
    info = {
        "address": address,
        "password": password
    }
    response = requests.post(
        url="https://api.mail.tm/token", headers=headers,
        json=info
    )
    if response.status_code == 200:
        return Token(response.json())
    elif response.status_code == 401:
        raise InvalidCredentials(response)
    else:
        return json.dumps(response.json(), indent=4)
