import json

from .base import BaseParser
from . import utils as parser_utils
from ..metadata import MetadataItem


class GenericJson(BaseParser):
    """
    Generic JSON parser.  Will parse any JSON content and flatten it for use
    in HyperThought™.

    Example:
    Input JSON file:
        {
            "a": {
                "b": [1, 2]
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
    VALID_EXTENSIONS = {'json', 'norms'}

    def parse(self):
        exception_message = (
            'Unable to open specified file. Is the content formatted as JSON?')

        try:
            with open(self._file_path, 'r') as fh:
                data = json.load(fh)
        except Exception as e:
            # Add exception message to error and re-raise.
            raise Exception('{}  Error: {}'.format(exception_message, str(e)))

        # Use the flatten module to remove nestedness.
        self.metadata = [
            MetadataItem(key=key, value=value)
            for key, value
            in parser_utils.flatten.flatten(data).items()
        ]
