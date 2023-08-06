from codecs import open
from os import path


# Get the release version from the VERSION file
def get_version_from_file(version_file):
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here, version_file), 'r') as fp:
        return fp.read().strip(' \r\n\t')
