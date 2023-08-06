from functools import partial

import requests

from .base import GenericAPI, ERROR_THRESHOLD


class WorkspacesAPI(GenericAPI):
    """
    Workspace API switchboard.

    Contains methods that correspond to endpoints for HyperThought™ workspaces.

    Parameters
    ----------
    auth : auth.Authorization
        Authorization object used to get headers and cookies needed to call
        HyperThought endpoints.
    """

    def __init__(self, auth):
        super().__init__(auth)

    def get_workspaces(self):
        """Get workspaces available to the current user."""
        base_url = self._auth.get_base_url()
        curried_request = partial(
            requests.get,
            url=f'{base_url}/api/workspace/',
        )
        r = self.attempt_api_call(curried_request=curried_request)

        if r.status_code < ERROR_THRESHOLD:
            return r.json()
        else:
            self._report_api_error(response=r)
