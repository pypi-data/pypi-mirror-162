import collections
from enum import Enum
from functools import partial
import math
import os

import requests

from .base import GenericAPI, ERROR_THRESHOLD
from ..metadata import MetadataItem
from .. import utils


class FileTransferProgressHandler:
    """
    Invokes a callback when transfer size thresholds have been reached.

    Parameters
    ----------
    chunk_size : int or None
        The constant interval between size thresholds.
    total_size : int
        The total size of a file in bytes.
    callback : callable
        The callback to be invoked when a size threshold has been crossed.
    """
    MINIMUM_CHUNK_SIZE = 1

    def __init__(self, chunk_size, total_size, callback):
        if not isinstance(chunk_size, int) or chunk_size < 0:
            raise ValueError("chunk_size must be a non-negative integer")

        if chunk_size < self.MINIMUM_CHUNK_SIZE:
            chunk_size = self.MINIMUM_CHUNK_SIZE

        if not isinstance(total_size, int) or total_size < 0:
            raise ValueError("total_size must be a non-negative integer")

        if not callable(callback):
            raise ValueError("callback must be callable")

        # TODO:  Callback must accept an integer
        #        (number of chunks already added).

        self.chunk_size = chunk_size
        self.total_size = total_size
        self.callback = callback

        # Invoke callback when current size is >= threshold.
        self.current_size = 0
        self.callback_threshold = chunk_size

    def add(self, increment):
        """
        Update total size (number of bytes transferred) by increment.

        self.callback will be invoked if the addition of the new increment
        crosses a size threshold.

        Parameters
        ----------
        increment : int
            The number of bytes transferred since the last invocation.
        """
        if not increment:
            return

        self.current_size += increment

        if self.current_size >= self.total_size:
            # NOTE:  Do not use self.current_size as the numerator.
            #        It may be larger than self.total_size, for reasons
            self.callback(math.ceil(self.total_size / self.chunk_size))
            return

        if self.current_size >= self.callback_threshold:
            self.callback(math.floor(self.current_size / self.chunk_size))

            while self.callback_threshold <= self.current_size:
                self.callback_threshold = min(
                    self.callback_threshold + self.chunk_size,
                    self.total_size
                )


class FilesAPI(GenericAPI):
    """
    Files API switchboard.

    Contains methods that (roughly) correspond to endpoints for the
    HyperThought files app.  The methods simplify some tasks, such as
    uploading and downloading files.

    Parameters
    ----------
    auth : auth.Authorization
        Authorization object used to get headers and cookies needed to call
        HyperThought endpoints.
    """
    VERSION = 'v1'

    class FileType(Enum):
        """
        Enum describing types of file documents to be returned from methods.

        See the get_from_location method for an example.
        """
        FILES_ONLY = 'file'
        FOLDERS_ONLY = 'folder'
        FILES_AND_FOLDERS = 'all'

    def __init__(self, auth):
        super().__init__(auth)
        self._backend = None
        self._files_base_url = f"{self._base_url}/api/files/"

        if self.VERSION:
            self._files_base_url += f"{self.VERSION}/"

    def get_document(self, id):
        """
        Get a database document for a file, given its id.

        Parameters
        ----------
        id : str
            The database id for a file or folder.

        Returns
        -------
        A dict-like database document for the file with the given id.
        """
        url = f"{self._files_base_url}{id}"
        curried_request = partial(
            requests.get,
            url=url,
            params={'id': id},
        )
        r = self.attempt_api_call(curried_request=curried_request)

        if r.status_code < ERROR_THRESHOLD:
            return r.json()
        else:
            self._report_api_error(response=r)

    def get_from_location(self, space_id, path=None, file_type=None,
                          start=0, length=25):
        """
        Get HyperThought files/folders from a specific location.

        Parameters
        ----------
        space_id : str
            The id of a workspace.
        path : str or None
            The id path to the location of interest.  If none, will default to
            id root path (e.g., ',').
            Ex: an id path for '/path/to/folder' would have the form
                ',uuid,uuid,uuid,'
        file_type : FileType or None
            An enum value for the type of files to get.  A None value will
            default to FileType.FILES_AND_FOLDERS.
        start : int
            Start index for results pagination (0-based).
        length : int
            Pagination page length.

        Returns
        -------
        A list of documents (dicts) from the database corresponding to
        files/folders at the specified path in the specified space.
        """
        # Validate parameters.
        space_id = self._validate_space_id(space_id=space_id)
        path = self._validate_path(path)
        file_type = self._validate_file_type(file_type)

        url = f"{self._files_base_url}workspace/{space_id}/"
        params = {
            'path': path,
            'start': start,
            'pageLength': length,
        }

        if file_type is None:
            params['type'] = self.FileType.FILES_AND_FOLDERS.value
        else:
            params['type'] = file_type.value

        curried_request = partial(
            requests.get,
            url,
            params=params,
        )
        r = self.attempt_api_call(curried_request=curried_request)

        if r.status_code >= ERROR_THRESHOLD:
            self._report_api_error(response=r)

        output = r.json()

        # TODO:  Make sure this is necessary.
        if output is None:
            output = []

        # TODO:  Make sure this is necessary.
        if not isinstance(output, list):
            output = [output]

        return output

    def get_all_from_location(self, space_id, path=None, file_type=None):
        """
        Get all files/folders in a given file system location.

        Parameters
        ----------
        space_id : str
            The id of the workspace where the files of interest are stored.
        path : str
            The parent folder path of interest.  This will be a comma-separated
            list of ids up to and including the parent folder id.
            Ex:  ",uuid,uuid,uuid,"
        file_type : hyperthought.api.files.FilesAPI.FileType or None
            An enum instance specifying the type of files to get, i.e. files,
            folders, or both.  Will get both if None.

        Returns
        -------
        A list of dicts containing information on files and/or folders in a
        given file system location.
        """
        # Validate inputs.

        if not isinstance(space_id, str):
            raise ValueError(
                "The space_id parameter to get_all_from_location must be a "
                "string."
            )

        if path is not None and not isinstance(path, str):
            raise ValueError(
                "The path parameter to get_all_from_location must be a string "
                "or None."
            )

        # Set pagination parameters.
        start = 0
        length = 25

        # Create list to collect output.
        files = []

        while True:
            new_files = self.get_from_location(
                space_id=space_id,
                path=path,
                file_type=file_type,
                start=start,
                length=length,
            )

            if not new_files:
                break

            files.extend(new_files)
            start += length

        return files

    def get_id(self, name, space_id, path=None):
        """
        Get an id for a file/folder with a given name at a given location.

        Parameters
        ----------
        name : str
            The name of the file system entry.
        space_id : str
            The id of a workspace.
        path : str or None
            The id path to the location of interest.  If none, will default to
            id root path (e.g., ',').
            Ex: an id path for '/path/to/folder' would have the form
                ',uuid,uuid,uuid,'

        Returns
        -------
        An id, if the specified file/folder exists, else None.
        """
        # Validate parameters.
        name = self._validate_name(name)
        space_id = self._validate_space_id(space_id=space_id)
        path = self._validate_path(path)

        url = f"{self._files_base_url}workspace/{space_id}/"
        params = {
            'path': path,
            'start': 0,
            'pageLength': 25,
        }

        while True:
            curried_request = partial(
                requests.get,
                url=url,
                params=params,
            )
            r = self.attempt_api_call(curried_request=curried_request)

            if r.status_code >= ERROR_THRESHOLD:
                # NOTE:  This method will throw an exception.
                self._report_api_error(response=r)

            documents = r.json()

            if not isinstance(documents, list):
                raise Exception(f"results from {url} are not a list")

            if not documents:
                return None

            for document in documents:
                if document['name'] == name:
                    # Return the first match found.
                    # Ideally, there should be only one.
                    return document['pk']

            params['start'] += params['pageLength']

    def get_id_at_path(self, path, space_id):
        """
        Get a file id given a human readable path.

        Parameters
        ----------
        space_id : str
            The id of a workspace.
        path : str
            A human-readable path, e.g. 'path/to/file.txt'

        Returns
        -------
        The id for the file corresponding to the given path if one exists,
        otherwise None.  Only the terminal id (for the last file or folder)
        will be returned.  Use get_id_path to get a full id path.
        """
        space_id = self._validate_space_id(space_id=space_id)

        if not isinstance(path, str):
            raise ValueError("path must be a string")

        sep = utils.PATH_SEP
        id_sep = utils.ID_PATH_SEP
        tokens = path.strip(sep).split(sep)
        id_path = id_sep
        id_ = None

        for token in tokens:
            id_ = self.get_id(
                name=token,
                space_id=space_id,
                path=id_path,
            )

            if id_ is None:
                break

            id_path += id_ + id_sep

        return id_

    def get_id_path(self, path, space_id):
        """
        Get an id path given a human readable path.

        The path will include the terminal id, whether or not the last element
        in the path is a  file.  If this is not desired, don't include the file
        in the input path.

        Parameters
        ----------
        space_id : str
            The id of a workspace.
        path : str
            A human-readable path, e.g. 'path/to/file.txt'

        Returns
        -------
        The id path corresponding to the human-readable path,
        e.g. ',uuid,uuid,uuid,' for '/path/to/folder'.
        """
        sep = utils.PATH_SEP
        id_sep = utils.ID_PATH_SEP

        if path == sep:
            return id_sep

        space_id = self._validate_space_id(space_id=space_id)

        if not isinstance(path, str):
            raise ValueError("path must be a string")

        tokens = path.strip(sep).split(sep)
        id_path = id_sep

        for token in tokens:
            id_ = self.get_id(
                name=token,
                space_id=space_id,
                path=id_path,
            )

            if id_ is None:
                raise FileNotFoundError(f"File not found: {token}")

            id_path += id_ + id_sep

        return id_path

    def get_object_link(self, space_id=None, id_=None, path=None):
        """
        Get an object link string to store a link as a metadata value.

        Parameters
        ----------
        id_ : str or None
            The id for the file of interest.
        space_id : str or None
            The id of a workspace.
        path : str
            A human-readable path to the file of interest,
            e.g. 'path/to/file.txt'

        If id_ is not provided, the other parameters must be.

        Returns
        -------
        An object link string.
        """
        if id_ is not None and not isinstance(id_, str):
            raise ValueError(f"string expected for id_, found {type(path)}")

        if id_ is None:
            if space_id is None:
                raise ValueError("space_id must be provided if id_ is not")

            if path is None:
                raise ValueError("path must be provided if id_ is not")

        get_link = lambda id_: f"/files/filesystementry/{id_}"

        if id_ is None:
            id_ = self.get_id_at_path(space_id=space_id, path=path)

            if not id_:
                raise FileNotFoundError(
                    f"No file found at path {path} "
                    f"in workspace with id {space_id}"
                )

        return get_link(id_)

    def create_folder(self, name, space_id, path=None, metadata=None,):
        """
        Create a folder in HyperThought.

        Parameters
        ----------
        name : str
            The name of the folder to create.
        space_id : str
            The id of a workspace.
        path : str or None
            The id path to the location of interest.  If none, will default to
            id root path (e.g., ',').
            Ex: an id path for '/path/to/folder' would have the form
                ',uuid,uuid,uuid,'
        metadata : list of metadata.MetadataItem or None
            A list of MetadataItem objects.  See metadata.MetadataItem.

        Returns
        -------
        The id of the new folder.
        """
        name = self._validate_name(name)
        space_id = self._validate_space_id(space_id=space_id)
        path = self._validate_path(path)
        metadata = self._validate_metadata(metadata)

        # At the time of last modification (9/7/21), there was no v1 version
        # of the create-folder endpoint.
        url = '{}/api/files/create-folder/'.format(self._auth.get_base_url())

        # Reformat metadata as needed to pass via API.
        if metadata:
            metadata = [item.to_api_format() for item in metadata]

        curried_request = partial(
            requests.post,
            url=url,
            json={
                'space_id': space_id,
                'path': path,
                'name': name,
                'metadata': metadata,
            },
        )
        r = self.attempt_api_call(curried_request=curried_request)

        if r.status_code >= ERROR_THRESHOLD:
            self._report_api_error(response=r)

        folder_id = r.json()['document']['content']['pk']
        return folder_id

    def move(self, source_space_id, destination_space_id, file_ids,
             source_parent_folder_id=None, destination_parent_folder_id=None):
        """
        Move files from one file system location to another.

        Parameters
        ----------
        source_space_id : str
            The id of the workspace from which the files are being moved.
        destination_space_id : str
            The id of the workspace to which the files are being moved.
        file_ids = list of str
            ids of files in the source location that will be moved to the
            destination location.
        source_parent_folder_id : str or None
            The id of the parent folder in the source location.
            If None, the root folder will be assumed.
        destination_parent_folder_id : str or None
            The id of the parent folder in the destination location.
            If None, the root folder will be assumed.

        Returns
        -------
        Data on the enqueueing operation, including the number of items
        processed and queue status for each item.
        """
        if not isinstance(source_space_id, str):
            raise ValueError("source_space_id must be a string")

        if not isinstance(destination_space_id, str):
            raise ValueError("destination_space_id must be a string")

        if not isinstance(file_ids, collections.abc.Sequence):
            raise ValueError("file_ids must be a sequence (e.g., list)")

        for file_id in file_ids:
            if not isinstance(file_id, str):
                raise ValueError("all file ids must be strings")

        if (
            source_parent_folder_id is not None
            and
            not isinstance(source_parent_folder_id, str)
        ):
            raise ValueError(
                "source_parent_folder_id must be a string if provided")

        if (
            destination_parent_folder_id is not None
            and
            not isinstance(destination_parent_folder_id, str)
        ):
            raise ValueError(
                "destination_parent_folder_id must be a string if provided")

        url = f"{self._files_base_url}move/"
        curried_request = partial(
            requests.post,
            url=url,
            json={
                'sourceSpaceId': source_space_id,
                'sourceParentFolderId': source_parent_folder_id,
                'destinationSpaceId': destination_space_id,
                'destinationParentFolderId': destination_parent_folder_id,
                'fileIds': file_ids,
            },
        )
        r = self.attempt_api_call(curried_request=curried_request)

        if r.status_code < ERROR_THRESHOLD:
            return r.json()
        else:
            self._report_api_error(response=r)

    def upload(self, local_path, space_id, path=None, metadata=None,
               progress_callback=None, n_chunks=100,):
        """
        Upload a file to HyperThought.

        Parameters
        ----------
        local_path : str
            The path to a file on the local system.
        space_id : str
            The id of a workspace.
        path : str or None
            The id path to the location of interest.  If none, will default to
            id root path (e.g., ',').
            Ex: an id path for '/path/to/folder' would have the form
                ',uuid,uuid,uuid,'
        metadata : list of metadata.MetadataItem or None
            A list of MetadataItem objects.  See metadata.MetadataItem.
        progress_callback : callable (int -> None) or None
            A callback for handling upload progress.  Will be called each time
            a given number of bytes (chunk) is uploaded.
        n_chunks : int
            The number of chunks to be handled by progress_callback.
            Will be ignored if progress_callback is None.

        Returns
        -------
        A tuple containing the file id and the name of the file.  (The name is
        returned in case it is changed by HyperThought™ to ensure uniqueness.)
        """
        # Validate parameters.
        local_path = self._validate_local_path(local_path)
        space_id = self._validate_space_id(space_id=space_id)
        path = self._validate_path(path)

        if metadata is None:
            metadata = []

        metadata = self._validate_metadata(metadata)

        # TODO:  Move this into a validation function.
        if progress_callback is not None and not callable(progress_callback):
            raise ValueError("progress_callback must be a callable or None")

        if not isinstance(n_chunks, int):
            raise ValueError("n_chunks must be an int")

        # Get file name and size using the local path.
        active_local_path = utils.get_active_path(local_path)
        name = active_local_path.split(os.path.sep)[-1]
        size = os.path.getsize(active_local_path)

        # Get an upload url.
        url, file_id = self._get_upload_url(
            space_id=space_id,
            name=name,
            size=size,
            path=path,
            metadata=metadata,
        )

        # Use the url to upload the file.
        self._upload_using_url(
            url,
            active_local_path,
            progress_callback,
            n_chunks,
        )

        # Move the file from the temporary to the permanent file collection.
        file_name = self._temp_to_perm(file_id)

        # Return the file id.
        return (file_id, file_name,)

    def download(self, file_id, directory, progress_callback=None,
                 n_chunks=100):
        """
        Download a file from HyperThought to the local file system.

        Parameters
        ----------
        file_id : str
            The HyperThought id for a file to be downloaded.
        directory : str
            A local directory path to which the file will be downloaded.
        progress_callback : callable (int -> None) or None
            A callback for handling upload progress.  Will be called each time
            a given number of bytes (chunk) is uploaded.
        n_chunks : int
            The number of chunks to be handled by progress_callback.
            Will be ignored if progress_callback is None.
        """
        # Validate parameters.
        self._validate_id(file_id)
        self._validate_local_path(directory)

        # Make sure the path is a directory.
        active_directory_path = utils.get_active_path(directory)

        if not os.path.isdir(active_directory_path):
            print(f"{directory} is not a directory")
            raise ValueError(f"{directory} is not a directory")

        # Get the file name.
        file_info = self.get_document(id=file_id)
        file_size = file_info['size']
        file_name = file_info['name']
        file_path = os.path.join(active_directory_path, file_name)

        # Get a download url.
        url = self._get_download_url(file_id)

        # Use the url to download the file.
        # NOTE:  Download attempts will not be curried and passed to
        #        self.attempt_api_call, since it is not clear that multiple
        #        attempts can be made with a presigned url.
        self._download_using_url(
            download_url=url,
            local_path=file_path,
            file_size=file_size,
            progress_callback=progress_callback,
            n_chunks=n_chunks,
        )

    def delete(self, ids):
        """
        Delete a file or folder.

        Parameters
        ----------
        ids : str
            Ids of files/folders to be deleted.
        """
        # Validate parameters.
        for id_ in ids:
            self._validate_id(id_)

        curried_request = partial(
            requests.delete,
            url='{}/api/files/'.format(self._base_url),
            json={'ids': ids},
        )
        r = self.attempt_api_call(curried_request=curried_request)

        if r.status_code >= ERROR_THRESHOLD:
            # NOTE:  This method will throw an exception.
            self._report_api_error(response=r)

    def update_metadata(self, file_id, new_metadata):
        """
        Update metadata for a file.

        Parameters
        ----------
        file_id : str
            The id (uuid) for the file of interest.
        new_metadata : list of MetadataItem or None
            New metadata for the file.
            This will replace any existing metadata.
            Merging will need to be done client-side.
        """
        if new_metadata is None:
            new_metadata = []

        # NOTE:  This method throws exceptions.
        new_metadata = self._validate_metadata(new_metadata)
        new_metadata = [item.to_api_format() for item in new_metadata]
        curried_request = partial(
            requests.patch,
            url=f"{self._base_url}/api/files/",
            json={
                'file_id': file_id,
                'updates': {
                    'metadata': new_metadata,
                }
            },
        )
        r = self.attempt_api_call(curried_request=curried_request)

        if r.status_code >= ERROR_THRESHOLD:
            # NOTE:  This method throws exceptions.
            self._report_api_error(r)

    def get_backend(self):
        """
        Get the files backend.

        Returns
        -------
        A string describing the file backend, e.g. 's3' or 'default'.
        """
        if self._backend is not None:
            return self._backend

        curried_request = partial(
            requests.get,
            url=f'{self._base_url}/api/files/backend/',
        )
        r = self.attempt_api_call(curried_request=curried_request)

        if r.status_code >= ERROR_THRESHOLD:
            self._report_api_error(response=r)

        self._backend = r.json()['backend']
        # TODO:  Replace assertion with proper error handling.
        assert self._backend in ('s3', 'default',), (
            f"Unexpected backend: {self._backend}. "
            f"Expected 's3' or 'default'."
        )
        return self._backend

    def is_folder(self, document):
        """Determine whether a document represents a folder in the
        HyperThought file system."""
        if not isinstance(document, collections.Mapping):
            return False

        if 'content' in document:
            if 'ftype' in document['content']:
                return document['content']['ftype'] == utils.FOLDER_TYPE

        if 'ftype' in document:
            return document['ftype'] == utils.FOLDER_TYPE

        return False

    def _get_upload_url(self, name, size, space_id, path=None, metadata=None):
        """
        Get presigned url to upload a file.

        Called from self.upload_file.

        Parameters
        ----------
        name : str
            The name of the file.
        size : int
            The size of the file in bytes.
        space_id : str
            The id for a group or project.  Irrelevant for user spaces.
        path : str or None
            The path to the directory that will contain the file.
            If None, will default to root path.
        metadata : list of metadata.MetadataItem or None
            A list of MetadataItem objects.  See metadata.MetadataItem.

        Returns
        -------
        A tuple containing the presigned url of interest as well as the file id
        for the file to be uploaded.
        """
        if path is None:
            path = utils.ID_PATH_SEP

        if metadata:
            metadata = [item.to_api_format() for item in metadata]
        else:
            metadata = []

        curried_request = partial(
            requests.post,
            url=f"{self._files_base_url}generate-upload-url/",
            json={
                'workspaceId': space_id,
                'path': path,
                'name': name,
                'size': size,
                'metadata': metadata,
            },
        )
        r = self.attempt_api_call(curried_request=curried_request)

        if r.status_code >= ERROR_THRESHOLD:
            # NOTE:  This method will throw an exception.
            self._report_api_error(response=r)

        url = r.json()['url']
        file_id = r.json()['fileId']

        # urls for locally stored files (default as opposed to s3 backend)
        # will be stripped of their protocol and hyperthought domain.
        # This is done to make presigned urls work with the DataTables
        # jQuery plugin in the HyperThought UI.
        if not url.startswith('http'):
            if not url.startswith('/'):
                url = f"/{url}"
            url = f"{self._base_url}{url}"

        return url, file_id

    def _upload_using_url(self, upload_url, local_path,
                          progress_callback, n_chunks):
        """
        Use a url to upload a file.

        Called from self.upload.

        Parameters
        ----------
        upload_url : str
            The url to which the file should be uploaded.
        local_path : str
            The local path to the file to be uploaded.
        progress_callback : callable(int -> None) or None
            A callable to provide progress on upload status.
        n_chunks : int
            The number of chunks to be handled by progress_callback.
            Will be ignored if progress_callback is None.
        """
        upload_url = self._validate_url(upload_url)
        local_path = self._validate_local_path(local_path)

        file_size = os.path.getsize(local_path)
        file_handle = open(local_path, 'rb')

        if progress_callback is not None:
            chunk_size = math.ceil(file_size / n_chunks)
            progress_handler = FileTransferProgressHandler(
                chunk_size=chunk_size,
                total_size=file_size,
                callback=progress_callback,
            )
            original_read = file_handle.read

            def new_read(size):
                progress_handler.add(size)
                return original_read(size)

            file_handle.read = new_read

        # NOTE:  This request will not be curried and passed to
        #        self.attempt_api_call, since it is not clear that multiple
        #        attempts could be made with a presigned url.
        kwargs = {
            'url': upload_url,
            'data': file_handle,
            'verify': False,
            'stream': True,
            'headers': {},
        }

        if self.get_backend() == 'default':
            kwargs['headers'].update(self._auth.get_headers())
            # Content-Disposition (with file name) is required by Django 2.2.
            sep = utils.PATH_SEP
            file_name = local_path.strip(sep).split(sep)[-1]
            kwargs['headers']['Content-Disposition'] = (
                f"inline;filename={file_name}")
            kwargs['cookies'] = self._auth.get_cookies()
        else:
            # TODO:  Why can't this be removed?
            kwargs['headers'].update({
                'Content-Type': 'application/octet-stream'
            })

        r = requests.put(**kwargs)

        if r.status_code >= ERROR_THRESHOLD:
            self._report_api_error(response=r)

        file_handle.close()

    def _temp_to_perm(self, file_id):
        """
        Move a file from the temporary (invisible) to the permanent (visible)
        file collection after the file has been completely uploaded.

        Parameters
        ----------
        file_id : str
            The HyperThought id for the file.

        Returns
        -------
        The name of the file in HyperThought.  (This will not be the same
        as the local name if a file with that name already exists in HT.)
        """
        curried_request = partial(
            requests.patch,
            url=f"{self._files_base_url}{file_id}/temp-to-perm/",
        )
        r = self.attempt_api_call(curried_request=curried_request)

        if r.status_code >= ERROR_THRESHOLD:
            self._report_api_error(response=r)

        # temp-to-perm no longer returns information on the file.
        # In order to get the file name, we must invoke another service.
        file_info = self.get_document(id=file_id)
        return file_info['name']

    def _get_download_url(self, file_id):
        """
        Get a url that can be used to download a file.

        Parameters
        ----------
        id : str
            The HyperThought id for a file of interest.

        Returns
        -------
        A url that can be used to download the file.
        """
        file_id = self._validate_id(file_id)
        curried_request = partial(
            requests.get,
            url=f"{self._base_url}/api/files/generate-download-url/",
            params={
                'id': file_id,
            },
        )
        r = self.attempt_api_call(curried_request=curried_request)

        if r.status_code >= ERROR_THRESHOLD:
            self._report_api_error(response=r)

        return r.json()['url']

    def _download_using_url(self, download_url, local_path, file_size,
                            progress_callback, n_chunks):
        """
        Use a generated url to download a file.

        Parameters
        ----------
        download_url : str
            The generated url for downloading the file of interest.
            See self._get_download_url.
        local_path : str
            The local system path where the downloaded file will be saved.
        progress_callback : callable (int -> None) or None
            A callback for handling upload progress.  Will be called each time
            a given number of bytes (chunk) is uploaded.
        n_chunks : int
            The number of chunks to be handled by progress_callback.
            Will be ignored if progress_callback is None.
        """
        kwargs = {
            'url': download_url,
            'stream': True,
            'verify': False,
        }

        if self.get_backend() == 'default':
            kwargs['headers'] = self._auth.get_headers()
            kwargs['cookies'] = self._auth.get_cookies()

        progress_handler = None

        if progress_callback is not None:
            progress_chunk_size = math.ceil(file_size / n_chunks)
            progress_handler = FileTransferProgressHandler(
                chunk_size=progress_chunk_size,
                total_size=file_size,
                callback=progress_callback,
            )

        DOWNLOAD_CHUNK_SIZE = 8192

        with requests.get(**kwargs) as r:
            r.raise_for_status()

            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                    if chunk:   # filter out keep-alive new chunks
                        f.write(chunk)

                        if progress_handler:
                            progress_handler.add(DOWNLOAD_CHUNK_SIZE)

    def _validate_id(self, id_):
        assert isinstance(id_, str), (
            f"expected string as id, found {type(id_)}")
        return id_

    def _validate_space(self, space=None):
        if space is None:
            space = 'user'

        # TODO:  Call error-handling function instead of raising an
        #        AssertionError.
        #        Same goes for all assertions in validation methods.
        assert space in ('group', 'project', 'user',), (
            f"Invalid space: {space}")

        return space

    def _validate_space_id(self, space=None, space_id=None):
        assert isinstance(space_id, str), (
            f"string expected, found {type(space_id)}")
        return space_id

    def _validate_path(self, path):
        if path is None:
            path = utils.ID_PATH_SEP

        assert isinstance(path, str)
        assert path.startswith(utils.ID_PATH_SEP)
        assert path.endswith(utils.ID_PATH_SEP)
        return path

    def _validate_name(self, name):
        assert isinstance(name, str)
        return name

    def _validate_size(self, size):
        assert isinstance(size, int) and size >= 0
        return size

    def _validate_metadata(self, metadata):
        # Validate metadata structure.
        if metadata is None:
            return None

        error_message = (
            "metadata must be a list of hyperthought.metadata.MetadataItem")

        if not isinstance(metadata, list):
            raise ValueError(error_message)

        for item in metadata:
            if not isinstance(item, MetadataItem):
                raise ValueError(error_message)

        return metadata

    def _validate_url(self, url):
        # TODO:  Use regex?
        assert isinstance(url, str)
        return url

    def _validate_local_path(self, local_path):
        assert isinstance(local_path, str)
        assert os.path.exists(local_path)
        return local_path

    def _validate_file_type(self, file_type):
        if file_type is None:
            file_type = self.FileType.FILES_AND_FOLDERS

        assert isinstance(file_type, self.FileType)

        return file_type
