============
hyperthought
============


Modules that encapsulate HyperThought API calls and make
operations like authentication and file transfer (upload
or download) easier to accomplish.

Description
===========

Example usage:

Here is the code needed to upload a file to a HyperThought project.

.. code-block:: python

    from getpass import getpass
    import hyperthought as ht

    auth_info = getpass("Enter encoded auth info from your HyperThought profile page: ")
    auth = ht.auth.Authorization(auth_info)
    files_api = ht.api.files.FilesAPI(auth)

    # The space could also be 'group' or 'user'.
    space = 'project'
    # space_id could also be a group id or username, for group or user spaces, respectively.
    space_id = input("Enter destination project id (in url of project): ")

    # Create a folder.
    # Use default (root) path and don't specify any metadata for the folder.
    # (See method docstring for info on unused parameters.)
    folder_id = files_api.create_folder(
        name="Tests",
        space=space,
        space_id=space_id,
    )

    # Get a path for the file.
    # Paths consist of comma-separated parent folder ids.
    path = f",{folder_id},"

    local_file_path = input("Enter path to local file: ")
    files_api.upload(
        local_path=local_file_path,
        space=space,
        space_id=space_id,
        path=path,
    )
    # Look in the HyperThought UI to see the uploaded file.
