import json

from .base import BaseParser
from . import utils as parser_utils
from ..metadata import MetadataItem


class Ayasdi(BaseParser):
    """
    Ayasdi parser.  Will parse any JSON content under a "meta" key and flatten
    it for use in HyperThought™.

    Example:
    Input JSON file:
        {
            "meta": {
                "a": {
                    "b": [1, 2]
                }
            }
        }
    The flattened metadata will be:
        {
            "a/b/_0": 1,
            "a/b/_1": 2
        }
    The flattened metadata will then be transformed to the API format.
        [
            {
                "keyName": "a/b/_0",
                "value": {
                    "type": "int",
                    "link": 1
                }
            },
            {
                "keyName": "a/b/_1",
                "value": {
                    "type": "int",
                    "link": 2
                }
            }
        ]
    """
    VALID_EXTENSIONS = {'json'}

    def parse(self):
        exception_message = (
            'An Ayasdi file must contain JSON with a "meta" key.')

        try:
            with open(self._file_path, 'r') as fh:
                data = json.load(fh)
        except Exception as e:
            # Add exception message to error and re-raise.
            raise Exception('{}  Error: {}'.format(exception_message, str(e)))

        if 'meta' not in data:
            raise Exception(exception_message)

        # Use the flatten module to remove nestedness.
        self.metadata = [
            MetadataItem(key=key, value=value)
            for key, value
            in parser_utils.flatten.flatten(data['meta']).items()
        ]
