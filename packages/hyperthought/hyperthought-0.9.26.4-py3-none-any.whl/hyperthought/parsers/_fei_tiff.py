import datetime
import os
import re

from ..metadata import MetadataItem
from .base import BaseParser
from . import utils as parser_utils


def _get_fei_conversion_map(
        Date_format='%m/%d/%Y',
        Time_format='%H:%M:%S %p',
        TimeOfCreation_format='%d.%m.%Y %H:%M:%S',
    ):
    """Get a map of field value conversions.

    Parameters
    ----------
    Date_format : string
        The format for the Date field.
    Time_format : string
        The format for the Time field.
    TimeOfCreation_format : string
        The format for the TimeOfCreation field.

    NOTE: All formats will be used with datetime.datetime.strptime.

    Returns
    -------
    A dictionary: keys = field names, values = callables
    """
    def convert_Date(s):
        return datetime.datetime.strptime(s, Date_format).date()

    def convert_Time(s):
        return datetime.datetime.strptime(s, Time_format).time()

    def convert_TimeOfCreation(s):
        return datetime.datetime.strptime(s, TimeOfCreation_format)

    return {
        'Average': float,  # int?
        'BeamShiftX': float,  # int?
        'BeamShiftY': float,  # int?
        'BitShift': float,  # int?
        'Brightness': float,
        'BrightnessDB': float,
        'BuildNr': int,
        'ChPressure': float,
        'Contrast': float,
        'ContrastDB': float,
        'DatabarHeight': float,  # int?
        'Date': convert_Date,
        'DigitalBrightness': float,  # int?
        'DigitalContrast': float,  # int?
        'DigitalGamma': float,  # int?
        'DisplayHeight': float,
        'DisplayWidth': float,
        'Dwell': float,
        'Dwelltime': float,
        'EmissionCurrent': float,
        'EucWD': float,
        'FrameTime': float,
        'Grid': float,  # int?
        'HFW': float,
        'HV': float,  # int?
        'HorFieldsize': float,
        'Integrate': float,  # int?
        'InternalScan': bool,
        'LineIntegration': float,  # int?
        'LineTime': float,
        'MagCanvasRealWidth': float,
        'MagnificationMode': float,  # int?
        'MinimumDwellTime': float,
        'Mix': float,  # int?
        'Number': int,
        'PixelHeight': float,
        'PixelWidth': float,
        'PreTilt': float,  # int?
        'ResolutionX': int,
        'ResolutionY': int,
        'ScanInterlacing': float,  # int?
        'ScanRotation': float,  # int?
        'ScreenMagCanvasRealWidth': float,
        'ScreenMagnificationMode': float,  # int?
        'Setting': float,  # int?
        'SourceTiltX': float,
        'SourceTiltY': float,
        'SpecTilt': float,  # int?
        'Spot': float,  # int?
        # TODO: determine whether this value can be decomposed
        # 'Stage': '150 x 150',
        'StageR': float,
        'StageT': float,
        'StageTa': float,
        'StageTb': float,  # int?
        'StageX': float,
        'StageY': float,
        'StageZ': float,
        'StigmatorX': float,
        'StigmatorY': float,
        'TiltCorrectionAngle': float,
        'Time': convert_Time,
        'TimeOfCreation': convert_TimeOfCreation,
        'VFW': float,
        'VerFieldsize': float,
        'WD': float,
        'WorkingDistance': float,
        'ZoomFactor': float,
        'ZoomPanX': float,
        'ZoomPanY': float
     }


class FeiTiff(BaseParser):
    """
    Parse metadata from an FEI tiff file.
    
    The metadata will be located at the end of the file, after the image data.

    Parameters
    ----------
        file_path: str
            The path to the file of interest.
        n_metadata_bytes : int
            The number of bytes to read from the end of the file.
            (This should be >= the number of bytes needed to store metadata.)
        key_value_delim : str
            The character that separates keys and values.
        key_map : dict
            A map used to replace keys.
        fields_with_units : set
            Keys for fields that require separation of numeric values and
            unit strings.
        conversion_map : dict
            A map of conversions to be performed.
            The keys are the field names.
            The values are conversion callables.
    """

    VALID_EXTENSIONS = {'tif', 'tiff'}

    def __init__(self, file_path, n_metadata_bytes=16384, key_value_delim='=',
                 key_map=None, fields_with_units=None, conversion_map=None,):
        super().__init__(file_path=file_path)
        self._n_metadata_bytes = n_metadata_bytes
        self._key_value_delim = key_value_delim

        if key_map is None:
            self._key_map = {}
        else:
            self._key_map = key_map

        if fields_with_units is None:
            self._fields_with_units = set()
        else:
            self._fields_with_units = fields_with_units

        if conversion_map is None:
            self._conversion_map = _get_fei_conversion_map()
        else:
            self._conversion_map = conversion_map

    def parse(self):
        file_handle = open(self._file_path)

        # Read the last n_metadata_bytes into a variable (text).
        file_handle.seek(0, os.SEEK_END)
        file_size = file_handle.tell()
        file_handle.seek(file_size - self._n_metadata_bytes)
        text = file_handle.read(self._n_metadata_bytes)

        # Extract the relevant substring from text.
        # (The metadata is organized as key value pairs in sections.
        # Each section name is surrounded by square brackets.
        # Thus, to find the beginning of the metadata, it will suffice
        # to find the first occurrence of '['.)
        start_index = text.find('[')
        text = text[start_index:]

        # Split the remaining text into lines, then use a regular expression
        # to extract key-value pairs from lines that match the key-value pattern.
        lines = text.split('\n')
        pattern = re.compile('\S+' + self._key_value_delim + '\S+')
        metadata = []

        for line in lines:
            if re.match(pattern, line):
                key, value = [s.strip() for s in line.split(self._key_value_delim)]
                kwargs = dict(key=key)
                conversion = self._conversion_map.get(key)

                # Split units and convert values as needed.
                if key in self._fields_with_units:
                    value, units = parser_utils.separate_units(value)
                    kwargs['units'] = units

                if conversion is not None:
                    value = conversion(value)

                kwargs['value'] = value
                metadata.append(MetadataItem(**kwargs))

        self.metadata = metadata
