# -*- coding: utf-8 -*-
import os
import sys
#  
# Do your custom imports here
import h5py  # If you want to export data as HDF5 file for example
#


def parse_data_ref(data_path, data_ref):
    """Fetch the required data

    :param data_path:
    :param data_ref: dataset reference as string
    :return:
    """
    #
    # Parse your data reference
    #
    # As an example, you could interpret the 'dataset reference' as a directory name, and concatenates it
    # with the base data directory path
    dataset_path = os.path.join(data_path, data_ref)
    if not os.path.isdir(dataset_path):
        raise IOError("Simulation snapshot data directory not found.")

    return dataset_path


def run(data_path, data_ref, argument_1="A", argument_2=256, argument_3=False, test=False):
    """My custom data processing service description

    :param data_path: path to data directory (string)
    :param data_ref: dataset reference (string)
    :param argument_1:
    :param argument_2:
    :param argument_3:
    :param test: Activate service test mode
    """
    path = parse_data_ref(data_path, data_ref)

    if test:
        #
        # Run your service in test mode
        #
        return

    #
    # Python code for the service in normal mode goes here !
    #

    # The data processing service must write its output data in a local (already created) "out/" directory.
    output_dir = "out"

    # Example => write data in a HDF5 file
    with h5py.File(os.path.join(output_dir, "results.h5"), 'w') as h5f:
        # Write result in a HDF5 dataset
        h5f.create_dataset("my_array", ...)


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])

__all__ = ["run"]
