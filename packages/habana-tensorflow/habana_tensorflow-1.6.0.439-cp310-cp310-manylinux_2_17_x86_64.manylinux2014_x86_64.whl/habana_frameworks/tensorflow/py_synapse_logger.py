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

import tensorflow as tf
import numpy as np
import imp
import sys
import os
import habana_frameworks.tensorflow as htf
from habana_frameworks.tensorflow.lib_utils import libraries_location

def _initialize():
    command_backlog=[]
    # store commands issued while loading logger and execute asap
    def command(f:str):
        command_backlog.append(f)
    globals()["command"] = command
    os.environ["SYNAPSE_LOGGER_TF_VERSION"] = str(tf.__version__)

    htf.load_habana_module()
    import habana_frameworks.tensorflow.habana_device as hdv

    _soname = "_py_synapse_logger.so"
    py_synapse_logger_so_path = os.path.join(libraries_location, _soname)
    _py_synapse_logger = imp.load_dynamic("_py_synapse_logger", py_synapse_logger_so_path)
    _py_synapse_logger.initialize()
    for c in command_backlog:
       _py_synapse_logger.command(c)
    return _py_synapse_logger, hdv

_py_synapse_logger, hdv = _initialize()

dump_reference = _py_synapse_logger.dump_reference


def compare(ref, data):
    ref_view = ref.numpy().astype(np.float32).view(np.uint8)
    data_view = data._numpy().view(np.uint8)
    _py_synapse_logger.compare(ref_view, data_view, data.dtype.name)


def command(f: str):
    """
    Executes synapse logger command.

    Parameter f contains string in format <command_name><=value>, where value format and meaning
    depends on the actual command and in many cases may be ommited.
    """
    before = _py_synapse_logger.is_enabled()
    res = _py_synapse_logger.command(f)
    after = _py_synapse_logger.is_enabled()
    if not before and after:
        hdv.enable_synapse_logger()
    elif before and not after:
        hdv.enable_synapse_api()


def _command_help(style="raw"):
    styles = {"raw": (("\n  ", "\n"), ("", "    ", "\n")), "markdown": (("\n* `", "`!!\n"), ("", "   ", "\n"))}

    markers = styles[style]

    def _wrap(text, length=80, prefix="    "):
        r = ""
        line = prefix
        for word in text.split(" "):
            if word:
                line += word + " "
            havenl = word.endswith("\n")
            if len(line) > length or havenl:
                r += line
                if not havenl:
                    r += "\n"
                line = prefix
        if line != prefix:
            r += line
        return r

    r = command.__doc__ + "\n\n"
    r += "  Currently supported commands:\n"
    for cmddef in _py_synapse_logger.get_command_definitions():
        r += f"{markers[0][0]}{cmddef.name}{markers[0][1]}"
        r += markers[1][0] + _wrap(cmddef.help, prefix=markers[1][1]) + markers[1][2]

    return r


command.__doc__ = _command_help()

put_log = _py_synapse_logger.put_log
start_hw_profile = _py_synapse_logger.start_hw_profile
stop_hw_profile = _py_synapse_logger.stop_hw_profile
release_device = _py_synapse_logger.release_device

data_dump_category = _py_synapse_logger.data_dump_category
