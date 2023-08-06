"""
parsers/_base.py

Abstract base class for parsers.
"""

from abc import ABC
from abc import abstractmethod
import collections
import os

from ..metadata import MetadataItem


class _NotAvailable:
    pass


class _NotAvailableException(Exception):
    pass


class BaseParser(ABC):
    """
    Abstract base class for parser.

    The interface consists of an abstract method, parse, which will parse
    data (eventually) and metadata from a file, as well as data and metadata
    properties to retrieve the parsed content.

    Parameters
    ----------
    file_path : str
        Path to the file to be parsed.
    """

    VALID_EXTENSIONS = None

    @classmethod
    def is_valid_extension(cls, file_extension):
        """Determine whether a file extension will work with the parser."""
        # If no valid extensions have been specified, assume the parser will
        # work.
        if not cls.VALID_EXTENSIONS:
            return True

        # Otherwise, make sure the extension provided is in the spec.
        valid_extensions = {
            extension.lower()
            for extension in cls.VALID_EXTENSIONS
        }
        return file_extension.lower() in valid_extensions

    def __init__(self, file_path):
        if not os.path.exists(file_path):
            raise ValueError(f"{file_path} is not a valid path")

        if not os.path.isfile(file_path):
            raise ValueError(f"{file_path} is not a file")

        if self.VALID_EXTENSIONS is not None:
            self.VALID_EXTENSIONS = {
                ext.lower()
                for ext in self.VALID_EXTENSIONS
            }
            file_extension = os.path.splitext(file_path)[1].strip('.').lower()

            if file_extension not in self.VALID_EXTENSIONS:
                raise ValueError(
                    "file extension should be one of "
                    f"{', '.join(self.VALID_EXTENSIONS)}")

        self._file_path = file_path
        self._data = _NotAvailable()
        self._metadata = _NotAvailable()

    @property
    def file_path(self):
        return self._file_path

    @property
    def data(self):
        raise NotImplementedError("data parsing has not been implemented")

    @data.setter
    def data(self, value):
        raise NotImplementedError("data parsing has not been implemented")

    @property
    def metadata(self):
        if isinstance(self._metadata, _NotAvailable):
            raise _NotAvailableException("No metadata has been set.")

        return self._metadata

    @metadata.setter
    def metadata(self, value):
        if (
            not isinstance(value, collections.abc.Sequence)
            or
            isinstance(value, str)
        ):
            raise ValueError("metadata must be a sequence")

        for item in value:
            if not isinstance(item, MetadataItem):
                raise ValueError(
                    "Each item in a metadata sequence must be an instance "
                    "of MetadataItem")

        self._metadata = value

    @abstractmethod
    def parse(self):
        pass

    def get_api_formatted_metadata(self):
        """
        Get metadata in API format.

        Will throw error if no metadata has been set.
        """
        return [item.to_api_format() for item in self.metadata]
