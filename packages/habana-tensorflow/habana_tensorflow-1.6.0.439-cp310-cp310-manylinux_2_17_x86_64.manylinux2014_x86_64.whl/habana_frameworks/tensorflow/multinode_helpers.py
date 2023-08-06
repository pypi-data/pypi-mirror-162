###############################################################################
# Copyright (C) 2021 Habana Labs, Ltd. an Intel Company
# All Rights Reserved.
#
# Unauthorized copying of this file or any element(s) within it, via any medium
# is strictly prohibited.
# This file contains Habana Labs, Ltd. proprietary and confidential information
# and is subject to the confidentiality and license agreements under which it
# was provided.
###############################################################################

import os
import json
import logging

import tensorflow as tf

from tensorflow.python.platform import tf_logging as logging
from .util import condition_env_var


SUPPORTED_HLS_TYPE = [
    "HLS1",
    "HLS1-H",
    "HLS2"
]

HLS1_MODULE_CNT = {
    "HLS1": 8,
    "HLS1-H": 4,
    "HLS2": 8
}


HCL_CONFIG_PATH_VAR = "HCL_CONFIG_PATH"
HLS_MODULE_ID_VAR = "HLS_MODULE_ID"
HABANA_VISIBLE_MODULES_VAR = "HABANA_VISIBLE_MODULES"
HABANA_VISIBLE_DEVICES_VAR = "HABANA_VISIBLE_DEVICES"


def run_once(f):
    def decorator(*args, **kwargs):
        if decorator.once_flag:
            f(*args, **kwargs)
            decorator.once_flag = False
    decorator.once_flag = True
    return decorator


@run_once
def _setup_env_for_multinode(required=False):
    if comm_size() > 1:
        _set_ID()
        _select_hls_module()
        rank_prefix = "rank_{}_".format(comm_rank())
        _set_env_prefix("TF_RANK_PREFIX", rank_prefix, False)
        _set_env_prefix("HBN_TF_GRAPH_PREFIX", rank_prefix, False)
        _set_env_prefix("TF_DUMP_GRAPH_PREFIX", rank_prefix, True)
        _hvd_rank_prefix = rank_prefix


def _select_hls_module():
    """
    This function is setting "HLS_MODULE_ID" variable for tf-bridge internals.
    "HLS_MODULE_ID" determines which Gaudi from HLS should be used by this process.
    If this variable is not set, tf-bridge will allocate first free device.
    """
    local_rank = comm_local_rank(True)
    if local_rank is None:
        # In case local rank is not available in env Module ID should be established by other means.
        logging.warning(
            "No specific Module ID is requested. First free device will be used!")
        return

    if HLS_MODULE_ID_VAR in os.environ.keys():
        # If HLS_MODULE_ID_VAR is already set. Do NOT override it!
        logging.warning(
            "HLS_MODULE_ID selected from user override. Value is %s", os.environ[HLS_MODULE_ID_VAR])
        return

    if HABANA_VISIBLE_DEVICES_VAR in os.environ.keys() and HABANA_VISIBLE_MODULES_VAR not in os.environ.keys():
        # This is W/A for k8s automated environment. [SW-88466]
        # As "HABANA_VISIBLE_MODULES" is not available there, fallback is to acquire first free device.
        return

    if HABANA_VISIBLE_MODULES_VAR in os.environ.keys():
        visible_modules = os.environ[HABANA_VISIBLE_MODULES_VAR].split(",")
        assert local_rank < len(
            visible_modules), f"There is not enough devices available for training. Please verify if {HABANA_VISIBLE_MODULES_VAR} is set correctly."
        os.environ[HLS_MODULE_ID_VAR] = visible_modules[local_rank]
        return

    # In all other cases strict mapping of local_rank -> module_id allows easier NUMA or MPI binding.
    os.environ[HLS_MODULE_ID_VAR] = str(local_rank)


def _set_ID():
    local_rank = comm_local_rank(True)
    if local_rank is None:
        # If we are unable to establish local_rank, we are unable to set ID
        return
    if "ID" in os.environ.keys():
        # ID has been already set. Do NOT override it!
        return
    os.environ["ID"] = str(local_rank)


def comm_size(check_available=False):
    return get_int_from_env("OMPI_COMM_WORLD_SIZE", 1, check_available)


def comm_rank(check_available=False):
    return get_int_from_env("OMPI_COMM_WORLD_RANK", 0, check_available)


def comm_local_size(check_available=False):
    return get_int_from_env("OMPI_COMM_WORLD_LOCAL_SIZE", 1, check_available)


def comm_local_rank(check_available=False):
    return get_int_from_env("OMPI_COMM_WORLD_LOCAL_RANK", 0, check_available)


def get_int_from_env(env_var, default_value, check_available=False):
    if check_available and env_var not in os.environ.keys():
        return None
    return int(os.environ.get(env_var, default_value))


def _set_env_prefix(env_name, prefix, leave_empty):
    old_prefix = os.environ.get(env_name, "")
    if leave_empty and not old_prefix:
        return
    new_prefix = f"{old_prefix}{prefix}"
    os.environ[env_name] = new_prefix


def _try_get_hcl_config(required):
    try:
        return get_hcl_config()
    except (AssertionError, json.JSONDecodeError):
        if (required):
            raise
        return None


def get_hcl_config():
    hcl_config_path = os.environ.get(HCL_CONFIG_PATH_VAR)
    assert hcl_config_path != None, "{} is not set, but required by Horovod".format(
        HCL_CONFIG_PATH_VAR)
    assert os.path.isfile(hcl_config_path), "{} points to not accessible file: {}".format(
        HCL_CONFIG_PATH_VAR, hcl_config_path)

    with open(hcl_config_path, "r") as hcl_config_file:
        try:
            return json.load(hcl_config_file)
        except json.JSONDecodeError:
            logging.error("{} indicated by {} is not valid json file".format(
                hcl_config_path, HCL_CONFIG_PATH_VAR))
            raise
