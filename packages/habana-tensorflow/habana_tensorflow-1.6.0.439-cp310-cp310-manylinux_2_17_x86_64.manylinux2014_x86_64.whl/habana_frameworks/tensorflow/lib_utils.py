###############################################################################
# Copyright (C) 2021 Habana Labs, Ltd. an Intel Company
# All Rights Reserved.
#
# Unauthorized copying of this file or any element(s) within it, via any medium
# is strictly prohibited.
# This file contains Habana Labs, Ltd. proprietary and confidential information
# and is subject to the confidentiality and license agreements under which it
# was provided.
#
###############################################################################
'''
Utility module to determine TF version without importing the module
It relies on 'pip3 freeze', that browses all the packages available
'''
import re
import subprocess
import os
import logging
import tensorflow as tf

_log = logging.getLogger(__file__)


def _is_habana_tensorflow_installed():
    '''
    helper function to browse packages installed with pip and determine if habana-tensorflow is installed
    '''
    pip3_freeze_out = str(subprocess.check_output(['pip3', 'freeze']))
    return re.search('habana-tensorflow', pip3_freeze_out) is not None


def _is_script_in_pip_packages():
    '''
    Unelegant way of checking if this file is in installed package by browsing path to file.
    It's to prevent mixing pip installation with scripts from repo.
    '''
    return 'site-packages' in os.path.abspath(__file__) or 'dist-packages' in os.path.abspath(__file__)


_tf_version_folder = "tf" + tf.__version__.replace(".", "_")
_module_lib_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               _tf_version_folder,
                               "lib",
                               "habanalabs")
_mandatory_lib = "habana_device.so." + tf.__version__


def _check_modules_directory(directory):
    if not os.path.isdir(directory):
        return False

    if not os.path.isfile(os.path.join(directory, _mandatory_lib)):
        return False

    return True

# in regular case, libs should be packed inside the module
# this function should be called only for non-module case


def _find_lib_in_ld_libs():
    _log.info('Searching LD_LIBRARY_PATH for libraries')
    if "LD_LIBRARY_PATH" in os.environ:
        for directory in os.environ.get("LD_LIBRARY_PATH").split(":"):
            if _check_modules_directory(directory):
                _log.info(f'Found {_mandatory_lib} in {directory}')
                return directory
    return None


def _get_modules_directory():
    _log.info("Trying to find libs in module directory..")

    if _is_script_in_pip_packages():
        if not _check_modules_directory(_module_lib_dir):
            raise Exception(
                f'habana-tensorflow is broken. Library {_mandatory_lib} for TensorFlow {tf.__version__} not found. Try reinstalling..')
        _log.info(f"Found libs in module dir {_module_lib_dir}")
        return _module_lib_dir
    if _is_habana_tensorflow_installed():
        raise Exception(
            'habana-tensorflow module has been found in packages installed via PIP and this module is used from local path.'
            f' The module used here is from {os.path.dirname(__file__)}.'
            ' Remove package from pip or do not use local module.')

    _log.info(f"Libs not found in module dir. Trying LD_LIBRARY_PATH..")
    ld_lib_found_path = _find_lib_in_ld_libs()
    if ld_lib_found_path:
        _log.info(f"Using libs from LD_LIBRARY_PATH - {ld_lib_found_path}")
        return ld_lib_found_path
    else:
        raise Exception(
            f"Failed to find {_mandatory_lib} for TensorFlow {tf.__version__} in LD_LIBRARY_PATH. Module is not properly initialized..")


def get_includes_location():
    '''
    This function returns location of API headers.
    '''
    if libraries_location == _module_lib_dir:
        return os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            _tf_version_folder,
                            "include")
    else:
        # local includes
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))),
                            'include')


libraries_location = _get_modules_directory()
if libraries_location:
    habana_module_path = os.path.join(libraries_location, _mandatory_lib)
else:
    habana_module_path = None
