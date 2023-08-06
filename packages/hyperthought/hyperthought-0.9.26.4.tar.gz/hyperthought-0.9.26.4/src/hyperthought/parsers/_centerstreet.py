"""
Parser for design of experiments and GCode data files generated from Center
Street Technologies AM experiments.
"""

import csv
import datetime
import os
import re
import xml.etree.ElementTree as ET

from .base import BaseParser
from ..metadata import MetadataItem

# Locates text between "(" and ")"
UNIT_PARENTHESIS = re.compile(r"(?<=\()(.*?)(?=\))")
# Identifies a Material Test Curve file
MAT_TEST_CURVE = re.compile('material\s?test\s?\d+\s?curve')
# Identifies a Material Test Summary File
MAT_SUMMARY = re.compile('material\s?test\s?summary')
# Captures Material Run Number
MAT_RUN = re.compile(r'(?<=material\stest)\s?(\d+)(?=\s?curve)')

class CenterStreet(BaseParser):
    """
    Parser intended to be applied to all CenterStreet documents.

    Currently parser will handle mpf and dpdx files.
    """

    VALID_EXTENSIONS = {'mpf', 'dxpx', 'csv'}

    def get_annotation(self, **kwargs):
        """
        Intended to create annotation string from required key:value pairs.

        Parameters
        ----------
        **kwargs: dict
            Simple set of keywords with values that are converted to a Simple
            dictionary.

        Returns
        -------
        s: str
            Formatted string containing all key value pairs from the input.
        """
        annotation_str = ''
        for key, value in kwargs.items():
            s = annotation_str.join(
                '<{key}:{value}>'.format(key=key, value=value)
            )
        return s

    def process_str(self, _input):

        '''
        Formats a given input by converting to string and eliminating
        new line characters and starting or trailing whitespaces.

        Parameters
        ----------
        _input (string): input to be formatted
        '''

        out_string = str(_input).replace('\n', ' ').strip()
        out_string = re.sub(r'\s+', ' ', out_string)

        return out_string

    def file_name_parser(self):
        '''
        Parser designed to parse out key data items from the file name of
        specific files.
        Returns list of metadata items constructed from parsed data.
        '''
        file_name = os.path.basename(self.file_path)
        metadata = []

        if bool(MAT_SUMMARY.search(file_name.lower())):
            fn_split = file_name.strip().split(' ')
            metadata.append(
                MetadataItem(
                    'Test Standard',
                    re.search('ASTM\s?[A-Z]\s?\d+\s?-\s?\d+', file_name).group()
                )
            )
        elif bool(MAT_TEST_CURVE.search(file_name.lower())):
            fn_split = file_name.strip().split(' ')
            run_date = datetime.datetime.strptime(fn_split[0], '%m%d%Y')
            metadata.append(
                MetadataItem(
                    'Test Run Date',
                    '{0}/{1}/{2}'.format(
                        run_date.month,
                        run_date.day,
                        run_date.year
                    )
                )
            )
            run_time = datetime.datetime.strptime(fn_split[1], '%H%M%S')
            metadata.append(
                MetadataItem(
                    'Test Run Time',
                    '{0}:{1}:{2} {3}'.format(
                        run_time.hour,
                        run_time.minute,
                        run_time.second,
                        fn_split[2][:2]
                    )
                )
            )
            metadata.append(
                MetadataItem(
                    'Run Number', MAT_RUN.search(file_name.lower()).group()
                )
            )

        return metadata

    def mat_summary_csv_parser(self):
        '''
        Parser designed to parse out key data items from a material test
        summary csv file.
        Returns list of metadata items constructed from parsed data.
        '''
        with open(self.file_path) as f:
            data = list(csv.reader(f, delimiter=','))

        metadata = []
        header_index = None

        for i in range(len(data)):
            # Find likely Tabular Row
            if len(data[i]) >= 2:
                # Capture header index
                if not header_index:
                    header_index = i
                    continue
                for j in range(len(data[i])):

                    if data[i][j] == '':
                        continue

                    data_item = {}

                    data_item['value'] = data[i][j]
                    data_item['annotation'] = self.get_annotation(
                        RUN_INDEX=str(i-header_index)
                    )
                    unit = UNIT_PARENTHESIS.findall(data[header_index][j])

                    if unit:
                        data_item['units'] = unit[-1]
                        data_item['key'] = re.sub(
                            "\(({})\)".format(unit[-1]),
                            '',
                            data[header_index][j]
                        )
                    else:
                        data_item['key'] = data[header_index][j]

                    metadata.append(MetadataItem(**data_item))

            # Seperate Data Item
            elif len(data[i]) == 1 and i+1 != len(data) and data[i][0].strip()\
                and data[i+1][0].strip():

                single_inst_data_item = {}
                unit = UNIT_PARENTHESIS.findall(data[i][0])

                if unit:
                    single_inst_data_item['units'] = unit[-1]
                    single_inst_data_item['key'] = re.sub(
                        '\(({})\)'.format(unit[-1]),
                        '',
                        data[i][0]
                    )
                else:
                    single_inst_data_item['key'] = data[i][0]

                single_inst_data_item['value'] = data[i+1][0]

                metadata.append(MetadataItem(**single_inst_data_item))

        return metadata

    def gcode_parser(self):
        '''
        Parser designed to parse out key data items from a GCode file.
        Returns list of metadata items constructed from parsed data.
        '''
        # Add GCode structure validation
        valid_lines = []
        start_line_index = -1
        end_line_index = -1

        # Items that have units that need to be apart of the value
        skip_units = [
            'Extruder 1 Material used',
            'Extruder 1 Material name',
            'Version of Fusion'
        ]

        metadata_items = []

        element = self.get_cdm_match('Gcode File Name')

        metadata_items.append(
            MetadataItem(
                key='Gcode File Name',
                value = os.path.splitext(self.file_path.split('/')[-1])[0],
                annotation=self.get_annotation(CDM_ID=element['id'], CDM_NAME=element['name'])
            )
        )

        with open(self.file_path) as f:
            lines = f.readlines()

        for index, line in enumerate(lines):
            if line[0] == ';' and start_line_index == -1:
                start_line_index = index
                valid_lines.append(line)
                continue
            if line[0] == ';' and end_line_index == -1:
                valid_lines.append(line)

            if line[0] != ';' and end_line_index == -1:
                end_line_index = index
                break

        for line in valid_lines:
            line_elements = line.split(":", 1)

            if len(line_elements) == 1:
                continue

            key = self.process_str(line_elements[0]).strip(';')
            value = self.process_str(line_elements[1])

            # Validate this is what we want to look up
            # Currently works but will need a better solution.
            unit_match = re.search('\d+(in)', value)

            if (unit_match and key not in skip_units):
                value = re.sub('in', '', value)
                unit = unit_match.group(1)
            else:
                unit = ''

            if key and value:
                cdm_element = self.get_cdm_match(key)
                metadata_items.append(
                    MetadataItem(
                        key=key,
                        value=value,
                        units=unit,
                        annotation=self.get_annotation(
                            CDM_ID=cdm_element['id'],
                            CDM_NAME=cdm_element['name']
                        )
                    )
                )

        return metadata_items

    def doe_parser(self):
        '''
        Parser designed to parse out key data items from a DOE file.
        Returns list of metadata items constructed from parsed data.
        '''
        tree = ET.parse(self.file_path)
        root = tree.getroot()

        headers = {}
        header_items = []
        metadata_items = []

        header_items.extend(
            [
                item
                for factor in root.findall('factorInfo')
                for item in factor
            ]
        )

        header_items.extend(
            [
                item
                for response in root.findall('responseInfo')
                for item in response
            ]
        )

        headers = {
            header.attrib['id'] : {
                'name': header.attrib['name'],
                'unit': header.attrib['unit']
            }
            for header in header_items
        }

        for index, item in enumerate(root.findall('run')):
            for child in item:
                key_ = headers[child.attrib['id']]['name']
                annotation_items = {
                    'RUN_INDEX': str(index)
                }
                metadata_items.append(
                    MetadataItem(
                        key=key_,
                        value=child.text,
                        units=headers[child.attrib['id']]['unit'],
                        annotation=self.get_annotation(**annotation_items)
                    )
                )

        return metadata_items

    def parse(self):
        '''
        Parser function that utilizes various parsers based on the input file
        extension type.
        '''

        self.metadata = self.file_name_parser()

        file_extension = os.path.splitext(self.file_path)[1].lstrip('.')

        if file_extension == 'mpf':
            self.metadata.extend(self.gcode_parser())
        elif file_extension == 'dxpx':
            self.metadata.extend(self.doe_parser())
        elif file_extension == 'csv':
            if MAT_SUMMARY.search(self.file_path.lower()):
                self.metadata.extend(self.mat_summary_csv_parser())
        else:
            pass