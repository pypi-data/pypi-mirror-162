from .base import BaseParser
from . import utils as parser_utils
from ..metadata import MetadataItem


class GenericHyperSpy(BaseParser):
    """
    Parse metadata extracted via hyperspy.
    """

    def parse(self):
        """Parse metadata extracted via HyperSpy."""
        try:
            import hyperspy.api as hs
            s = hs.load(self._file_path)
        except ModuleNotFoundError:
            raise ModuleNotFoundError("HyperSpy has not been installed.")

        metadata_dict = s.original_metadata.as_dictionary()
        flattened_metadata_dict = parser_utils.flatten.flatten(metadata_dict)

        metadata = [
            MetadataItem(key=key, value=value)
            for key, value in flattened_metadata_dict.items()
        ]
        
        self.metadata = metadata
