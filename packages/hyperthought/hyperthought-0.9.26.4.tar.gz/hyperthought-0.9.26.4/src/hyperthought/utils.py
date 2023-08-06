import os
import platform


ID_PATH_SEP = ','
PATH_SEP = '/'
WINDOWS_LOCAL_PATH_PREFIX = '\\\\?\\'
WINDOWS_GLOBAL_PATH_PREFIX = "\\??\\"
FOLDER_TYPE = 'Folder'
VALID_SPACES = {'group', 'project', 'user'}


class InvalidMetadataFormatException(Exception):
    pass


def get_active_path(path):
    """Get a path that can be used to get size, read/write, etc."""
    path = path.replace('\\', os.path.sep).replace('/', os.path.sep)

    if (
        platform.system() != 'Windows'
        or
        path.startswith(WINDOWS_LOCAL_PATH_PREFIX)
        or
        path.startswith(WINDOWS_GLOBAL_PATH_PREFIX)
    ):
        return path

    return f'{WINDOWS_LOCAL_PATH_PREFIX}{path}'
