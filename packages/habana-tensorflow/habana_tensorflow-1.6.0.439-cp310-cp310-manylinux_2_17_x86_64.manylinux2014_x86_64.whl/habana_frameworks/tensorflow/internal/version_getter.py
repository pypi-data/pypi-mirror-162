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
import os
import subprocess
import sys
import logging

logger = logging.getLogger(__file__)

_version_keys = ("LIBRARY", "VERSION", "VERSION_HASH", "BUILD_DATE", "VERSION_TF", "BUILD_DIRTY")
_begin_token, _end_token = b"BEGIN_VERSION_STR>>>", b"<<<END_VERSION_STR"


def get_version_str(file_name):
    with open(file_name, "rb") as lib:
        library = lib.read()
    b = library.find(_begin_token)
    if b == -1:
        raise Exception(f"Failed to retrieve Version starting token from {file_name}.")
    e = library.find(_end_token, b)
    if e == -1:
        raise Exception(f"Failed to retrieve Version ending token from {file_name}.")
    e -= len(",")
    if e - b >= 256:
        raise Exception(f"Length of verson string is invalid in {file_name} ({e-b}).")
    b+= len(_begin_token) + len(",")
    vstr = library[b:e].decode("ascii")
    return b, e, vstr


def get_version_dict(lib_to_read_version_info):
    p = get_version_str(lib_to_read_version_info)
    if p is None:
        return None
    _, _, output = p
    output = output.split(",")

    return {key: number for key, number in zip(_version_keys, output)}


def concat_version_dict(version_dict):
    out = "_".join(version_dict[key] for key in _version_keys[:-1])

    if "BUILD_DIRTY" in version_dict:
        out += "_dirty"
    return out

