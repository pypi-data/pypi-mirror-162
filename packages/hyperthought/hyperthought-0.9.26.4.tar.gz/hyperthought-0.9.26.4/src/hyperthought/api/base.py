"""
base.py

Base/generic functionality related to API calls.
"""

from datetime import datetime
import json
import os
import tempfile
from time import sleep

import requests


# Any status codes >= the following will result in errors being reported.
ERROR_THRESHOLD = 300


class APIError(Exception):
    pass


class GenericAPI:
    """
    Base class for app-specific API classes.

    Parameters
    ----------
    auth : auth.Authorization
        Authorization manager for access to HyperThought™ over OIDC.
    """

    def __init__(self, auth):
        self._auth = auth
        self._base_url = auth.get_base_url().rstrip('/')

    @property
    def auth(self):
        return self._auth

    def _report_api_error(self, response):
        """
        Report an error from an API call.

        The content of the failed request will be written to file.
        An Exception will also be thrown with detailed information about the
        request.

        response : requests.models.Response
            A response object corresponding to an API request.
            The status code will likely indicate an error, but the caller will
            be responsible for checking it.
        """
        # Go to directory that contains the api submodule.
        # TODO:  Revisit.  Make sure this is sensible if there is no parent
        #        directory.
        error_directory = os.path.join(
            # <parent_directory>/<submodule>/api/workflow/base.py
            tempfile.gettempdir(),
            'error_output',
        )

        # Make sure the error directory exists.
        if not os.path.exists(error_directory):
            os.makedirs(error_directory)

        now = datetime.now()
        error_file = '{}/error_{}{:02}{:02}_{:02}{:02}{:02}.html'.format(
            error_directory, now.year, now.month, now.day, now.hour,
            now.minute, now.second)

        with open(error_file, 'wb') as f:
            f.write(response.content)

        url = response.url
        headers = dict(response.headers)
        cookies = dict(response.cookies.get_dict())

        msg = (
            "\n\nAPI ERROR"
            "\nurl: {} "
            "\nheaders:\n{}\n"
            "\ncookies:\n{}\n"
            "\nerror file: {}\n\n"
        ).format(
            url,
            json.dumps(headers, indent=2),
            json.dumps(cookies, indent=2),
            error_file
        )
        raise APIError(msg)

    def attempt_api_call(self, curried_request, attempts=10, sleep_time=1):
        """
        Convenience function to attempt an API call.

        This method will deal with ConnectionErrors by sleeping and retrying
        the call.

        Parameters
        ----------
        curried_request : function
            A curried API request (e.g. requests.get, requests.post, etc.)
        attempts : int
            The number of times to try the call before giving up.
            Additional attempts will be made only if the last attempt resulted
            in a ConnectionError.
        sleep_time : numeric
            Sleep time in seconds.

        Returns
        -------
        The response object associated with the call.

        Exceptions
        ----------
        All exceptions will be re-raised, with the exception of
        ConnectionError, which will be tried a given number of times.
        """
        while attempts > 0:
            try:
                r = curried_request(
                    headers=self.auth.get_headers(),
                    cookies=self.auth.get_cookies(),
                    verify=self.auth.verify,
                )

                if r.status_code >= 300:
                    raise APIError(
                        f"status code: {r.status_code}\n"
                        f"content: {r.content.decode()}"
                    )
                else:
                    return r
            except (requests.ConnectionError, APIError) as e:
                attempts -= 1

                if attempts == 0:
                    raise e

                sleep(sleep_time)
            except Exception as e:
                raise e
