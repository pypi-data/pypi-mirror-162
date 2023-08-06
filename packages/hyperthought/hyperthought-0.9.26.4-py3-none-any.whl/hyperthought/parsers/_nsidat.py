from .base import BaseParser
from ..metadata import MetadataItem


class NorthStarImageData(BaseParser):
    """
    Parse a NorthStar Imaging CT reconstruction header file.

    The header file contains the number of voxels in the whole reconstruction,
    the voxel size in each dimension, the creation date, the name(s) of file(s)
    containing the reconstruction, and the number of slices in each file.

    Parameters
    ----------
    file_path : str
        A path to a NorthStar header file.
    """

    VALID_EXTENSIONS = {'nsihdr'}

    def parse(self):
        # Import third party libraries here to avoid memory overhead and
        # installation requirements.
        with open(self._file_path, 'r') as fh:
            lines = fh.readlines()

        metadata = []
        extent_mins = []
        extent_maxes = []
        data_file_names = []
        data_file_slices = []
        n_files = 0

        for i, line in enumerate(lines):
            if line.lstrip().startswith("<Voxels>"):
                voxels = [
                    int(val)
                    for val in line[len("<Voxels>"):].strip().split()
                ]
            elif line.lstrip().startswith("<Min>"):
                extent_mins = [
                    float(val)
                    for val in line[len("<Min>"):].strip().split()
                ]
            elif line.lstrip().startswith("<Max>"):
                extent_maxes= [
                    float(val)
                    for val in line[len("<Max>"):].strip().split()
                ]
            elif (
                line.lstrip().startswith("<Name>")
                and
                lines[i+1].lstrip().startswith("<NbSlices>")
            ):
                data_file_names.append(line.split(">").strip())
                n_files += 1  #increment file count
                #look at the next line for the slice count
                data_file_slices.append(lines[i+1].split()[1])
            elif line.lstrip().startswith("<Project Name>"):
                metadata.append(
                    MetadataItem(
                        key='Project Name',
                        value=line.split(">").strip()
                    )
                )
            elif line.lstrip().startswith("<Creation Date>"):
                metadata.append(
                    MetadataItem(
                        key='Creation Date',
                        value=line.split(">").strip()
                    )
                )

        metadata.insert(0, MetadataItem(key='Nfiles', value=n_files))

        #compute voxel size
        assert len(extent_mins) == 3, "extent mins ('<Min>' line) not found"
        assert len(extent_maxes) == 3, "extent maxes ('<Max>' line) not found"

        for key, index in zip(('dx', 'dy', 'dz'), range(3)):
            metadata.append(
                MetadataItem(
                    key=key,
                    value=extent_maxes[index] - extent_mins[index],
                    units='mm?',  # appears to be in mm
                )
            )

        for key, index in zip(["Nx", "Ny", "Nz"], range(3)):
            metadata.append(
                MetadataItem(
                    key=key,
                    value=voxels[index],
                )
            )

        metadata.append(
            MetadataItem(
                key='data_files',
                value=', '.join(data_file_names),
            )
        )
        metadata.append(
            MetadataItem(
                key='data_file_slices',
                value=', '.join(data_file_slices),
            )
        )

        self.metadata = metadata