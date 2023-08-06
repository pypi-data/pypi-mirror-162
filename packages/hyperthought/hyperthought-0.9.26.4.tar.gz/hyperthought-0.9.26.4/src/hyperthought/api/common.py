from enum import Enum
from functools import partial

import requests

from .base import GenericAPI, ERROR_THRESHOLD


class CommonAPI(GenericAPI):
    """
    Common API switchboard.

    Contains methods corresponding to endpoints that are called from multiple
    HyperThought™ components.

    Parameters
    ----------
    auth : auth.Authorization
        Authorization object used to get headers and cookies needed to call
        HyperThought endpoints.
    """

    class BugSeverity(Enum):
        """Severity levels used when reporting bugs."""
        LOW = 0
        MEDIUM = 1
        HIGH = 2
        CRITICAL = 3

        def to_string(self):
            """Convert enum instance to a string."""
            return self.name.title()

        @classmethod
        def to_enum(cls, severity):
            """
            Get an enum instance from corresponding text.

            Parameters
            ----------
            severity : str
                A string representing a severity level.

            Returns
            -------
            An enum instance.
            """
            # TODO:  Handle error case:  when severity string does not
            #        correspond to an enum value.
            return cls[severity.upper()]

    def __init__(self, auth):
        super().__init__(auth)

    def report_bug(self, description, severity=None):
        """
        Report a bug in the HyperThought™ API or a related application.

        Parameters
        ----------
        description : str
            A description of the error encountered.
        severity : BugSeverity or None
            The severity of the error being reported.  Default: MEDIUM.

        Returns
        -------
        A dictionary representing the bug report.  Keys will include the
        following:
            id : int
                The database id associated with the bug report record.
            user : str
                The username of the reported.
            email : str
                The email address of the reporter.
            description : str
                The description of the error, same value as the parameter.
            severity : str
                The severity level of the error, parameter value converted to
                title-case string.
            location : str
                A url supplied to the endpoint to identify which component
                the error is associated with.  The value used here is simply
                the base url plus "/api".
        """
        # Validate inputs.
        # TODO:  improve error handling, document exceptions in docstring.
        assert isinstance(description, str)
        if severity is None:
            severity = self.BugSeverity.MEDIUM
        assert isinstance(severity, self.BugSeverity)

        # Report the bug.
        url = f"{self._base_url}/api/common/user_incident/"
        data = {
            'user': self._auth.get_username(),
            'email': self._auth.get_email(),
            # This is a hack.  The location field expects a URL.
            'location': f"{self._base_url}/api",
            'description': description,
            'severity': severity.to_string(),
        }
        curried_request = partial(
            requests.post,
            url=url,
            data=data,
        )
        r = self.attempt_api_call(curried_request=curried_request)

        if r.status_code < ERROR_THRESHOLD:
            return r.json()
        else:
            self._report_api_error(response=r)

    def get_units(self):
        """Get list of QUDT units."""
        url = f"{self._base_url}/api/common/units/"
        curried_request = partial(
            requests.get,
            url=url,
        )
        r = self.attempt_api_call(curried_request=curried_request)

        if r.status_code < ERROR_THRESHOLD:
            return r.json()
        else:
            self._report_api_error(response=r)

    def get_vocab(self):
        """Get AFRL vocabulary (materials properties, etc)."""
        url = f"{self._base_url}/api/common/afrl-vocab/"
        curried_request = partial(
            requests.get,
            url=url,
        )
        r = self.attempt_api_call(curried_request=curried_request)

        if r.status_code < ERROR_THRESHOLD:
            return r.json()
        else:
            self._report_api_error(response=r)
