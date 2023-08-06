import os
from horovod.runner import run

def _get_pkg_version():
    with open('PKG-INFO') as f:
        for line in f:
            if line.startswith('Version: '):
                return line.split()[-1].strip()

def _get_version():
    version = os.getenv('release_version')
    if version:
        build_number = os.getenv('rel_id')
        if build_number:
            return version + '.' + build_number
        else:
            return version + '.dev0'
    elif os.path.exists('PKG-INFO'):
        try:
            return _get_pkg_version()
        except:
            return '0.0.0.dev0'
    else:
        return '0.0.0.dev0'

# habana-horovod version
__version__ = _get_version()
