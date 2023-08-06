"""
Parser plug-in framework for extracting data and metadata from files.

Built-in parsers can be accessed directly, e.g. hyperthought.parsers.Ayasdi.

There is also a plug-in framework that can be used to add parsers.
See the add method for adding parsers and the get method for getting parsers
once added.

All parsers must subclass hyperthought.parsers.base.BaseParser.
"""

import importlib
import inspect
import os

from .base import BaseParser

# Make parser class available from the parsers package.
# Ex: ht.parsers.Ayasdi is to be preferred over ht.parsers.ayasdi.Ayasdi.
from ._ayasdi import Ayasdi
from ._centerstreet import CenterStreet
from ._craic import Craic
from ._genericjson import GenericJson
from ._midas import MidasStressStrain
from ._nsidat import NorthStarImageData
from ._fei_tiff import FeiTiff
# hyperspy removed for now.  Email sent to Andrew Sharits on 10/28/21 to see
# if it is still of interest.
# from ._hyperspy import GenericHyperSpy


PARSERS = {
    'Ayasdi': Ayasdi,
    'CenterStreet': CenterStreet,
    'Craic': Craic,
    'MidasStressStrain': MidasStressStrain,
    'NorthStarImageData': NorthStarImageData,
    'FeiTiff': FeiTiff,
    'GenericJson': GenericJson,
    # 'GenericHyperSpy': GenericHyperSpy,
}


class ParserNotFoundException(Exception):
    pass


def get(parser_name):
    """
    Get a parser given a parser name.

    This can be used to get built-in parsers as well as parsers added via the
    plugin framework.
    """
    if not isinstance(parser_name, str):
        raise TypeError('parser_name must be a string')

    if parser_name not in PARSERS:
        raise ParserNotFoundException(
            f"No parser named '{parser_name} could be found.")

    return PARSERS[parser_name]


def add(path):
    """
    Add a parser or parsers at a given file or directory path.

    If the path is for a Python file, the contents will be examined for
    subclasses of hyperthought.parsers.base.BaseParser.  If it is for a
    directory, the contents will be searched recursively for Python files.

    Parameters
    ----------
    path : str
        A path to a file or directory.

    Results
    -------
    Parser classes found in the file or directory will be added to get module
    for retrieval via the get method.
    """
    if not os.path.exists(path):
        raise ValueError(f"{path} is not a valid path")

    if os.path.isfile(path):
        file_name, file_extension = os.path.splitext(path)
        file_extension = file_extension.strip('.').lower()

        if file_extension != 'py':
            return

        spec = importlib.util.spec_from_file_location(file_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        class_members = inspect.getmembers(module, inspect.isclass)

        for class_name, class_ in class_members:
            if class_name in PARSERS:
                print(f"Unable to add {class_name} from {path} "
                      "due to name conflict")

            if issubclass(class_, BaseParser):
                PARSERS[class_name] = class_
    elif os.path.isdir(path):
        for de in os.scandir(path):
            add(de.path)
