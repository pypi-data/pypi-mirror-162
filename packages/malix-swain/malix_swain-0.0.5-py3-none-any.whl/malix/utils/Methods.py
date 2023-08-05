import requests
import json
import os, platform
from .headers import Header
from .attributes import *
from .exceptions import *


def get_sources(Id: str, token: str):
    """Returns the available sources for the respective Id."""
    pass


def get_message_collection(token: str):
    """Retrives the collection resource."""
    headers = Header(token)
    response = requests.get(url="https://api.mail.tm/messages", headers=headers.header)

    if response.status_code == 401:
        raise NotAuthorized(response)
    else:
        return response.json()


def get_message(Id: str, token: str):
    """Retrives the available messages for the respective source."""
    headers = Header(token)
    response = requests.get(url="https://api.mail.tm/messages/"+Id, headers=headers.header)

    if response.status_code == 200:
        return Message(response.json())
    elif response.status_code == 401:
        raise NotAuthorized(response)
    elif response.status_code == 404:
        raise ResourceNotFound(response)
    else:
        return json.dumps(response.json(), indent=4)


def delete_message(Id: str, token: str):
    """Deletes the message resource."""
    headers = Header(token)
    response = requests.delete(url="https://api.mail.tm/messages/"+Id, headers=headers.header)

    if response.status_code == 204:
        return response.status_code
    elif response.status_code == 401:
        raise NotAuthorized(response)
    elif response.status_code == 404:
        raise ResourceNotFound(response)
    else:
        return json.dumps(response.json(), indent=4)


def update_message(Id: str, token: str):
    """Updates message resource."""
    headers = Header(token)
    info = {
        "seen": True
    }
    response = requests.patch(url="https://api.mail.tm/messages/"+Id, headers=headers.header, json=info)
    return response.json()


def download_message(Id: str, token: str, path: str = None):
    """Downloads the message."""
    html = get_message(Id, token).html[0]
    if path:
        pass
    elif platform.system() == "Windows":
        path = "C:/Users/"+os.getlogin()+"/Downloads/"
    elif platform.system() == "Linux":
        path = "/home/"+os.getlogin()+"/Downloads/"
    elif platform.system() == "Darwin":
        path = "/Users/"+os.getlogin()+"/Downloads/"
    
    with open(path+Id+".html", "w") as f:
        f.write(html)
    return 200


def get_domain_collection(domains_only: bool = False):
    """Retrives collection of domains."""
    headers = Header()
    response = requests.get(url="https://api.mail.tm/domains", headers=headers.header)
    data = response.json()["hydra:member"]
    if domains_only:
        domains = [i['domain'] for i in data]
        return domains
    else:
        return response.json()


def get_domain(Id: str):
    """Retrives resource of a specific domain id."""
    headers = Header()
    response = requests.get(url="https://api.mail.tm/domains/"+Id, headers=headers.header)

    if response.status_code == 200:
        return Domain(response.json())
    elif response.status_code == 404:
        raise ResourceNotFound(response)
    else:
        return json.dumps(response.json(), indent=4)


def make_account(address: str = None, password: str = None):
    """Creates a resource for an account."""
    headers = Header()
    info = {
        "address": address,
        "password": password
    }
    response = requests.post(url="https://api.mail.tm/accounts", headers=headers.header, json=info)

    if response.status_code == 201:
        return Account(response.json())
    elif response.status_code == 400:
        raise InvalidInput(response)
    elif response.status_code == 422:
        raise UnprocessableEntity(response)
    else:
        return json.dumps(response.json(), indent=4)


def get_account(Id: str, token: str):
    """Retrives the resource of an account."""
    headers = Header(token)
    URL = "https://api.mail.tm/accounts/"+Id
    response = requests.get(url=URL, headers=headers.header)

    if response.status_code == 200:
        return Account(response.json())
    elif response.status_code == 401:
        raise NotAuthorized(response)
    elif response.status_code == 404:
        raise ResourceNotFound(response)
    else:
        return json.dumps(response.json(), indent=4)


def delete_account(Id, token: str):
    """Deletes the account resource."""
    headers = Header(token)
    URL = "https://api.mail.tm/accounts/"+Id
    response = requests.delete(url=URL, headers=headers.header)

    if response.status_code == 204:
        return response.status_code
    elif response.status_code == 401:
        raise NotAuthorized(response)
    elif response.status_code == 404:
        raise ResourceNotFound(response)
    elif response.status_code == 403:
        raise AccessDenied(response)
    else:
        return json.dumps(response.json(), indent=4)


def get_my_account(token: str):
    """Retrives the resource for an logged in account."""
    headers = Header(token)
    URL = "https://api.mail.tm/me"
    response = requests.get(url=URL, headers=headers.header)

    if response.status_code == 200:
        return Account(response.json())
    elif response.status_code == 401:
        raise NotAuthorized(response)
    elif response.status_code == 404:
        raise ResourceNotFound(response)
    else:
        return json.dumps(response.json(), indent=4)
