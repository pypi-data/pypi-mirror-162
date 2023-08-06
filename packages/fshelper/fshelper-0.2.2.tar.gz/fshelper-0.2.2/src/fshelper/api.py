import logging

from requests import Session

logger = logging.getLogger(__name__)


class Credential:
    """Facilitate creating a Basic authentication credential for the FreshService API.

    https://api.freshservice.com/#authentication
    """

    def __init__(self, username=None, password=None):
        """Constructor for a Credential object.

        https://api.freshservice.com/#authentication

        :param username: FreshService API key or FreshService Username
        :param password: Dummy password when using an API key. 'X' is used in the documentation
        """
        self.username = username
        self.password = password


class RequestService:
    """Wrapper for the requests package to create an authenticated session with the FreshService API

    Use this class with a context manager or new_session() with a try, except, finally block with
    'RequestService.session.close() in the finally block.
    """

    def __init__(self, credential: Credential, domain: str):
        """Constructor for a RequestService object

        :param credential: Credential object
        :param domain: FreshService domain (the part before '.freshservice.com')
        """
        self.credential = credential
        self.domain = domain
        self.session = None

    def __enter__(self):
        self.new_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if any((exc_type, exc_val)):
            logger.exception(
                "Error encountered with requests session. %s - %s",
                exc_type,
                exc_val,
            )
        logger.info("Quitting requests session")
        self.session.close()

    def new_session(self):
        self.session = Session()
        self.session.auth = (self.credential.username, self.credential.password)
