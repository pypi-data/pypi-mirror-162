class Header:
    """Header class of MalixMail.

        :param token: Token of the account.
        :type: str

        **header**
            - if ``token`` is ``None`` ::

                {
                    "Content-Type": "application/ld+json",
                    "accept": "application/ld+json"
                }

            - if ``token`` is provided ::

                {
                    "Content-Type": "application/ld+json",
                    "accept": "application/ld+json",
                    "Authorization": "bearer"+token
                }

        """
    def __init__(self, token: str = None):
        header = {
            "Content-Type": "application/ld+json",
            "accept": "application/ld+json"
        }
        if token:
            header["Authorization"] = "bearer "+token
        self.header = header
