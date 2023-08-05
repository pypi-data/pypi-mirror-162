"""
File manager.

Responsible for retrieving all files requested by the user
"""

import os.path
import pickle
import sys
from os import listdir
from os.path import join


def getFiles(input_directory, nFiles=None):
    """Returns the files of the input directory"""
    # If it's not a dry run, all the files are returned
    if not nFiles:
        try:
            for f in listdir(input_directory):
                yield join(input_directory, f)
        except NotADirectoryError:
            sys.exit("The input attribute of your configuration file does not designate a directory. Maybe you are trying to process a copc ? Try adding the --copc flag.")
    # If it's a dry run, only the biggest nFiles of the directory are returned
    else:
        try:
            # Get all the files
            files = [join(input_directory, f) for f in listdir(input_directory)]
            # Create tuples (filepath, filesize)
            filesSize = [(join(input_directory, f), os.path.getsize(join(input_directory, f))) for f in files]
            # Sort files in descending order
            filesSize.sort(key=lambda tup: tup[1], reverse=True)
            # Get the first nFiles
            for i in range(nFiles):
                yield filesSize[i][0]
        except NotADirectoryError:
            sys.exit("The input attribute of your configuration file does not designate a directory. Maybe you are trying to process a copc ? Try adding the --copc flag.")


def getSerializedPipelines(temp_directory):
    """Returns the pipelines that have been serialized"""
    for tmp in listdir(temp_directory):
        # Open the serialized pipeline
        with open(join(temp_directory, tmp), 'rb') as p:
            # Deserialize it
            pipeline = pickle.load(p)
        yield pipeline
