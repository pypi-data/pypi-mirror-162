class Error(Exception):
    """Base class of Error."""
    def __init__(self, *args):
        super().__init__(*args)


class InvalidCredentials(Error):
    """Raises when given credentials are invalid.

    - **code**: **401**
    """
    def __init__(self, *args):
        self.response = args[0]
        self.json = self.response.json()

        super().__init__(self.json)


class InvalidInput(Error):
    """Raises when either address or password is invalid.

    - **code**: **400**
    """
    def __init__(self, *args):
        super().__init__(*args)


class UnprocessableEntity(Error):
    """Raises when no valid inputs are given.

    - **code**: **422**
    """
    def __init__(self, *args):
        self.response = args[0]
        self.json = self.response.json()
        data = {
            'code': self.response.status_code,
            'message': self.json["hydra:description"]
        }
        super().__init__(data)


class ResourceNotFound(Error):
    """
    Raises when there is no account resource belongs the respective
    credentials.

    - **code** : **404**
    """
    def __init__(self, *args):
        self.response = args[0]
        self.json = self.response.json()
        data = {
            'code': self.response.status_code,
            'message': self.json["hydra:description"]
        }
        super().__init__(data)


class NotAuthorized(Exception):
    """Raises When the client isn't authorized.

    - **code**: **401**
    """
    def __init__(self, *args):
        self.response = args[0]
        super().__init__(self.response.json())


class AccessDenied(Exception):
    """Raises when the client doesn't have the rights to perform some specific operations.

    - **code**: **403**
    """
    def __init__(self, *args):
        self.response = args[0]
        self.json = self.response.json()
        data = {
            'code': self.response.status_code,
            'message': self.json["hydra:description"]
        }
        super().__init__(data)
