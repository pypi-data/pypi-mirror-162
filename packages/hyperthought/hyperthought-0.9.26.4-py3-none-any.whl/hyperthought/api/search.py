import collections
from functools import partial

import requests

from .base import GenericAPI, ERROR_THRESHOLD


class SearchAPI(GenericAPI):
    """
    Search API switchboard.

    Contains methods that correspond to HyperThought search endpoints.

    At the present time, there is only one search endpoint that is intended
    for API use.  Search features are in active development, however, so this
    will not be true for long.

    Parameters
    ----------
    auth : auth.Authorization
        Authorization object used to get headers and cookies needed to call
        HyperThought endpoints.
    """

    VALID_FACET_KEYS = {
        'CreatedOn',
        'ModifiedOn',
        'CreatedBy',
        'ModifiedBy',
        'FileType',
    }

    def __init__(self, auth):
        super().__init__(auth)

    def get_valid_facet_keys(self):
        """Get a set of facet keys that can be used with the search method."""
        return set(self.VALID_FACET_KEYS)

    def search(self, query, start=0, length=25, facets=None):
        """
        Get information on parsers available to the current user.

        Parameters
        ----------
        query : str
            The requested search query.
        start : int
            The starting location in the list of matching records to return.
            Uses 0-indexing.
        length : int
            How many records to return with each call.
        facets : list of str or None
            An optional list of facets used to filter the requested query.
            The strings take the form "{facet_key}:{value}".
            The "{facet_key}" part of the string must be in a list of valid
            facets.  See the get_valid_facet_keys method.

        Returns
        -------
        A dict containing search results.  Keys include 'results' (list of
        matching records), 'start' (same as start_record parameter),
        'end' (same as page_length parameter), and 'totalRecords' (total
        number of records matching the query in the database).
        """
        if facets is None:
            facets = []
        else:
            if not isinstance(facets, collections.abc.Sequence):
                raise ValueError("facets must be a sequence")

        for facet in facets:
            facet_key = facet.split(':')[0]

            if facet_key not in self.VALID_FACET_KEYS:
                raise ValueError(
                    f"Invalid facet: '{facet_key}'.  "
                    f"Must be one of {self.VALID_FACET_KEYS}."
                )

        curried_request = partial(
            requests.post,
            url=f'{self._base_url}/api/search/v1/api-search/',
            json={
                'query': query,
                'start': start,
                'length': length,
                'facets': facets,
            },
        )
        r = self.attempt_api_call(curried_request=curried_request)

        if r.status_code < ERROR_THRESHOLD:
            return r.json()
        else:
            self._report_api_error(response=r)
