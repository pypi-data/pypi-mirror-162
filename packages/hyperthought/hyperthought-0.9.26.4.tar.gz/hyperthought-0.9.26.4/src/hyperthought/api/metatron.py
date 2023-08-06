from functools import partial

import requests

from .base import GenericAPI, ERROR_THRESHOLD


class MetatronAPI(GenericAPI):
    """
    Metatron (parsers) API switchboard.

    Contains methods that correspond to endpoints for HyperThought™ parsers.

    Parameters
    ----------
    auth : auth.Authorization
        Authorization object used to get headers and cookies needed to call
        HyperThought endpoints.
    """

    def __init__(self, auth):
        super().__init__(auth)

    def get_parsers(self):
        """Get information on parsers available to the current user."""
        curried_request = partial(
            requests.get,
            url=f'{self._base_url}/api/metatron/parsers/',
        )
        r = self.attempt_api_call(curried_request=curried_request)

        if r.status_code < ERROR_THRESHOLD:
            return r.json()
        else:
            self._report_api_error(response=r)
