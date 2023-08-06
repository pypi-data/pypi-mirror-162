from .base import BaseParser
from ..metadata import MetadataItem


class MidasStressStrain(BaseParser):
    """
    Read metadata from a tensile test.

    This is tailored to a format developed during the MIDAS program.

    Parameters
    ----------
    file_name : str
        The path to the file to be parsed.
    metadata_columns : list of dict or None
        Information on columns where keys, values, and units can be found.

    Required libraries
    ------------------
     -  numpy
     -  pandas

    Created on Fri Sep 28 04:53:19 2018
    @author: eddie

    Last modified by Jason Thiese on 6/1/2021.
    """
    VALID_EXTENSIONS = {'xlsx'}

    def __init__(self, file_path, metadata_columns=None):
        super().__init__(file_path=file_path)
        self._metadata_columns = metadata_columns

    def parse(self):
        # Use local imports to limit memory footprint and install requirements.
        from numpy import vectorize as np_vectorize
        from pandas import concat as pd_concat
        from pandas import read_excel as pd_read_excel

        # TODO:  Consider reworking the following to be function parameters.
        SHEET_NAME = 'Summary Sheet'

        if self._metadata_columns is None:
            self._metadata_columns = [
                # General metadata
                {
                    'key_column': 'B',
                    'value_column': 'D',
                    'unit_column': None,
                },
                # Dates
                {
                    'key_column': 'G',
                    'value_column': 'H',
                    'unit_column': None,
                },
                # Results
                {
                    'key_column': 'L',
                    'value_column': 'M',
                    'unit_column': 'N',
                },
            ]

        remove_colon = np_vectorize(
            lambda s: s[:-1] if s.endswith(':') else s
        )

        # Read metadata into a pandas.DataFrame.
        df_metadata = None

        for column_info in self._metadata_columns:
            # Determine parameters to read_excel.
            usecols = [
                column_info['key_column'],
                column_info['value_column']
            ]

            names = ['key', 'value']

            if column_info['unit_column'] is not None:
                usecols.append(column_info['unit_column'])
                names.append('unit')

            usecols = ','.join(usecols)

            # Read data using read_excel and process as needed.
            new_metadata = pd_read_excel(
                self._file_name,
                sheet_name=SHEET_NAME,
                usecols=usecols,
                index_col=None,
                header=None,
                names=names
            )

            new_metadata = new_metadata.dropna()
            new_metadata["key"] = new_metadata["key"].apply(remove_colon)

            # Add the new metadata to metadata.
            if df_metadata is None:
                df_metadata = new_metadata
            else:
                # TODO:  Consider updating a list rather than
                #        concatenating dataframes.
                df_metadata = pd_concat([df_metadata, new_metadata], sort=False)

        metadata = []

        for row in df_metadata:
            kwargs = dict(key=row['key'], value=row['value'])
            
            if row['unit']:
                kwargs['units'] = row['unit']

            metadata.append(MetadataItem(**kwargs))

        self.metadata = metadata
