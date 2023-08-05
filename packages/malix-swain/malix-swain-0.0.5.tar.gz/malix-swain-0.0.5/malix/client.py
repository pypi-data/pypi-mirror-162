from .utils import Methods, jwtoken


class Client:
    """Client class for MalixMail.

    :param address: Address of the account.
    :param password: Passowrd of the account.
    :type address: str
    :type password: str

    :returns Client: :class:`Client <malix.client.Client>` object.

    """

    def __init__(self, address: str, password: str):
        self.email = address
        self.password = password
        self.token = jwtoken.get_token(address=address, password=password).token
        self.id = jwtoken.get_token(address=address, password=password).id


    def get_account(self, Id: str):
        """Returns an :class:`Account <malix.utils.attributes.Account>` object for the given account id.

        :param Id: Id of the account.
        :type Id: str

        :returns: :class:`Account <malix.utils.attributes.Account>` object.

        :raises NotAuthorized: When the client isn't authorized.
        :raises ResourceNotFound: When there is no account resource associated with the given account id.

        :type NotAuthorized: :class:`NotAuthorized <malix.utils.exceptions.NotAuthorized>`
        :type ResourceNotFound: :class:`ResourceNotFound <malix.utils.exceptions.ResourceNotFound>`

        """
        return Methods.get_account(Id, self.token)


    def get_my_account(self):
        """Returns an :class:`Account <malix.utils.attributes.Account>` object for the client.

        :returns: :class:`Account <malix.utils.attributes.Account>` object.

        :raises NotAuthorized: When the client isn't authorized.
        :raises ResourceNotFound: When there is no account resource associated with the client's address.
        :raises AccessDenied: When the client doesn't have the rights to perform some specific operations.

        :type NotAuthorized: :class:`NotAuthorized <malix.utils.exceptions.NotAuthorized>`
        :type ResourceNotFound: :class:`ResourceNotFound <malix.utils.exceptions.ResourceNotFound>`
        :type AccessDenied: :class:`AccessDenied <malix.utils.exceptions.AccessDenied>`

        """
        return Methods.get_my_account(self.token)


    def delete_account(self, Id: str):
        """Deletes the account resource of the given account id.

        :param Id: Id of the account.
        :type Id: str

        :returns: **204** (*int*) - Successfully deleted.

        :raises NotAuthorized: When the client isn't authorized.
        :raises ResourceNotFound: When there is no account resource associated with the given account id.
        :raises AccessDenied: When the client doesn't have the rights to perform some specific operations.When you don't have the rights to perform the specific operations.

        :type NotAuthorized: :class:`NotAuthorized <malix.utils.exceptions.NotAuthorized>`
        :type ResourceNotFound: :class:`ResourceNotFound <malix.utils.exceptions.ResourceNotFound>`
        :type AccessDenied: :class:`AccessDenied <malix.utils.exceptions.AccessDenied>`

        """
        return Methods.delete_account(Id, self.token)


    def get_message_collection(self):
        """Returns collections of messages.

        :returns: dict - dictonary of inbox messages.

        :raises NotAuthorized: When the client isn't authorized.
        :type NotAuthorized: :class:`NotAuthorized <malix.utils.exceptions.NotAuthorized>`

        """
        return Methods.get_message_collection(self.token)


    def get_message(self, Id: str):
        """Returns a :class:`Message <malix.utils.attributes.Message>` object for the given message id.

        :param Id: Id of the account.
        :type Id: str

        :returns: :class:`Message <malix.utils.attributes.Message>` object.

        :raises NotAuthorized: When the client isn't authorized.
        :raises ResourceNotFound: When there is no message resource associated with the given message id.

        :type NotAuthorized: :class:`NotAuthorized <malix.utils.exceptions.NotAuthorized>`
        :type ResourceNotFound: :class:`ResourceNotFound <malix.utils.exceptions.ResourceNotFound>`

        """
        return Methods.get_message(Id, self.token)


    def delete_message(self, Id: str):
        """Deletes the message resource of the given message id.

        :param Id: Id of the message.
        :type Id: str

        :returns: **204** (*int*) - Successfully deleted.

        :raises NotAuthorized: When the client isn't authorized.
        :raises ResourceNotFound: When there is no message resource associated with the given message id.

        :type NotAuthorized: :class:`NotAuthorized <malix.utils.exceptions.NotAuthorized>`
        :type ResourceNotFound: :class:`ResourceNotFound <malix.utils.exceptions.ResourceNotFound>`

        """
        return Methods.delete_message(Id, self.token)


    def download_message(self, Id: str, Path: str = None):
        """Downloads the message.

        :param Id: Id of the message.
        :type Id: str

        :returns: **200** (*int*) - Successfully downloaded.

        :raises NotAuthorized: When the client isn't authorized.
        :raises ResourceNotFound: When there is no message resource associated with the given message id.

        :type NotAuthorized: :class:`NotAuthorized <malix.utils.exceptions.NotAuthorized>`
        :type ResourceNotFound: :class:`ResourceNotFound <malix.utils.exceptions.ResourceNotFound>`

        """
        if Path:
            return Methods.download_message(Id, self.token, Path)
        else:
            return Methods.download_message(Id, self.token)

    def update_message(self, Id: str):
        """Updates seen status of the given message id.

        :param Id: Id of the account.
        :type Id: str

        :returns: **response** (*dict*) - Response of the patch request.

        :raises NotAuthorized: When the client isn't authorized.
        :raises ResourceNotFound: When there is no account resource associated with the given account id.
        :raises InvalidInput: When no valid inputs are given.
        :raises UnprocessableEntity: When no valid inputs are given.

        :type NotAuthorized: :class:`NotAuthorized <malix.utils.exceptions.NotAuthorized>`
        :type ResourceNotFound: :class:`ResourceNotFound <malix.utils.exceptions.ResourceNotFound>`

        :type InvalidInput: :class:`InvalidInput <malix.utils.exceptions.InvalidInput>`
        :type UnprocessableEntity: :class:`UnprocessableEntity <malix.utils.exceptions.UnprocessableEntity>`

        """
        return Methods.update_message(Id, self.token)


def get_token(address: str, password: str):
    """Returns a :class:`Token <malix.utils.attributes.Token>` object for the given credentials.

    :param address: Address of the account.
    :param password: Passowrd of the account.
    :type address: str
    :type password: str

    :returns: :class:`Token <malix.utils.attributes.Token>` object

    :raises InvalidCredentials: Raises when given credentials are invalid.
    :type InvalidCredentials: :class:`InvalidCredentials <malix.utils.exceptions.InvalidCredentials>`

    """
    return jwtoken.get_token().token


def make_account(address: str, password: str):
    """Creates an account resourse using the given credentials.

    :param address: Address of the account.
    :param password: Passowrd of the account.
    :type address: str
    :type password: str

    :returns: :class:`Account <malix.utils.attributes.Account>` object.

    :raises InvalidInput: When no valid inputs are given.
    :raises UnprocessableEntity: When no valid inputs are given.

    :type InvalidInput: :class:`InvalidInput <malix.utils.exceptions.InvalidInput>`
    :type UnprocessableEntity: :class:`UnprocessableEntity <malix.utils.exceptions.UnprocessableEntity>`

    """
    respone = Methods.make_account(address, password)
    return respone


def get_domain_collection(domains_only: bool = False):
    """Returns collection of available domains.

    :param domains_only: Set true if you want to get only the domains containing in a list.
    :type domains_only: bool

    :returns:
        - if ``domains_only: bool = False`` : dictionary of available domains with other responses.
        - if ``domains_only: bool = True`` : list of available domains.

    """
    return Methods.get_domain_collection(domains_only=domains_only)


def get_domain(Id: str):
    """Returns :class:`Domain <malix.utils.attributes.Domain>` object of the given Id.

    :param Id: Id of the domain.
    :type Id: str

    :returns: :class:`Domain <malix.utils.attributes.Domain>` object.

    :raises ResourceNotFound: When there is no domain resource associated with the given domain id.
    :type ResourceNotFound: :class:`ResourceNotFound <malix.utils.exceptions.ResourceNotFound>`

    """
    return Methods.get_domain(Id)
