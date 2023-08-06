import datetime

from ..metadata import MetadataItem
from .base import BaseParser
from . import utils as parser_utils


class Craic(BaseParser):
    """
    Parse metadata from a CRAIC file.

    Called by craic_msp_csv_text.

    Parameters
    ----------
    file_path : str
        Path to the file to be parsed.
    tag_list_delim : str
        The delimiter used between key/value pairs.
    key_value_delim : str
        The delimiter used between keys and values.
    sep : str
        A separator used (at the end of lines) in CRAIC files with csv
        extensions.
    key_map : dict-like or None
        A map between keys as found in the source file and keys to be used
        in HyperThought.  If None, a default dict will be used.
    fields_with_units : set-like or None
        A set of fields whose values have units.
    conversion_map : dict-like or None
        A map of type conversions.  Keys are field names, values are callables.
    date_format : str
        A format string corresponding to the date used in the source file.
    date_prefix : str
        Text to be stripped from the beginning of a date value in the source
        file prior to parsing the value into a datetime.
    date_postfix : str
        Text to be stripped from the end of a date value in the source
        file prior to parsing the value into a datetime.
    date_key : str
        The metadata key to associate with the run date.
        (No such key is available in the source file.)

    Returns
    -------
    Metadata, in the form of key-value pairs.
    """
    VALID_EXTENSIONS = {'txt', 'csv'}

    def __init__(self, file_path, tag_list_delim=':', key_value_delim='=',
                 sep=',', key_map=None, fields_with_units=None,
                 conversion_map=None, date_format='%m/%d/%Y %H:%M:%S %p',
                 date_prefix='Date(', date_postfix=')', date_key='Date'):
        super().__init__(file_path=file_path)
        self._tag_list_delim = tag_list_delim
        self._key_value_delim = key_value_delim
        self._sep = sep
        self._date_format = date_format
        self._date_prefix = date_prefix
        self._date_postfix = date_postfix
        self._date_key = date_key

        # Set parameters to default values, as necessary.
        if key_map is None:
            self._key_map = {
                'SciModeIT': 'Integration Time',
                'NS': 'Samples',
                'Obj': 'Objective',
            }
        else:
            self._key_map = key_map

        if fields_with_units is None:
            self._fields_with_units = {'Integration Time'}
        else:
            self._fields_with_units = fields_with_units

        if conversion_map is None:
            self._conversion_map = {
                'Integration Time': float,
                'Samples': int,
            }
        else:
            self._conversion_map = conversion_map

    def parse(self):
        metadata = []

        with open(self._file_path) as file_handle:
            metadata.append(
                MetadataItem(
                    key='Sample Name',
                    value=file_handle.readline().strip().strip(self._sep),
                )
            )
            metadata.append(
                MetadataItem(
                    key='Measurement Type',
                    value=file_handle.readline().strip().strip(self._sep),
                )
            )

            tag_text = file_handle.readline().strip().strip(self._sep)

            # Get the index for the date.
            # By assumption, the date will be at the end of the tag text.
            # TODO:  Verify this assumption.
            date_index = tag_text.find(self._date_prefix)

            # Process the date if found.
            if date_index >= 0:
                date_text = tag_text[date_index:]
                # Remove prefix and postfix.
                date_text = date_text[len(self._date_prefix):-len(self._date_postfix)]
                # Add the result as a string using an appropriate format.
                date_ = datetime.datetime.strptime(date_text, self._date_format)
                metadata.append(
                    MetadataItem(
                        key=self._date_key,
                        value=date_,
                        type_='dateTime',
                    )
                )
                # Remove date from tag text.
                tag_text = tag_text[:date_index].strip(self._tag_list_delim)

            # Split tag text using the appropriate deliminator.
            # (This can be done safely once the date has been removed.)
            tag_list = tag_text.split(self._tag_list_delim)

            # Process the key value pairs in the tag list.
            for item in tag_list:
                key, value = item.split(self._key_value_delim)
                metadata.append(self._get_metadata_item(key, value))
            
            # Set metadata.
            self.metadata = metadata

    def _get_metadata_item(self, key, value):
        """Add key-value pair to output dictionary."""
        # Replace key if necessary.
        if key in self._key_map:
            key = self._key_map[key]

        # Get conversion callable based on the key.
        conversion = self._conversion_map.get(key)
        units = None

        # Split units and convert values as needed.
        if key in self._fields_with_units:
            value, units = parser_utils.separate_units(value)

        if conversion is not None:
            value = conversion(value)

        kwargs = {
            'key': key,
            'value': value,
        }

        if units is not None:
            kwargs['units'] = units

        return MetadataItem(**kwargs)
