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
import logging
from enum import Enum
import tensorflow as tf

from habana_frameworks.tensorflow.multinode_helpers import comm_rank, comm_size

_log = logging.getLogger(__file__)


class SynapseLoggerConfig:
    CONFIG_ENV_VARIABLE_NAME = "HABANA_SYNAPSE_LOGGER"
    RANGE_ENV_VARIABLE_NAME = "HABANA_PROFILE_RANGE"

    def __init__(self):
        self._disable_autostart = False
        self._traceme = False
        self._hw_warn = False
        self._hw = False
        self._synapse = False
        self._required = False
        self._log_file_name = ""
        self._range = []
        self._init_from_env()
        self._init_range()

    #
    # Supported ranges formtats are: ["100-102", "100:102" "100,101,102", "100"]
    def _init_range(self):
        self._range = []
        range_str = os.environ.get(
            self.RANGE_ENV_VARIABLE_NAME, "").lower()
        if range_str:
            try:
                if "-" in range_str or ":" in range_str:
                    if "-" in range_str:
                        profiler_range = range_str.split("-")
                    if ":" in range_str:
                        profiler_range = range_str.split(":")
                    assert len(profiler_range) == 2
                    self.update_range(list(
                        range(int(profiler_range[0]), int(profiler_range[1])+1)))
                    return
                self.update_range([int(range_str)])
            except ValueError:
                _log.error(" ".join([
                    f"{self.RANGE_ENV_VARIABLE_NAME} value is malformed, range not set.",
                    "Supported formats are \"100-102\", \"100:102\", \"100\""
                ]))

    def _init_from_env(self):
        config_str = os.environ.get(
            self.CONFIG_ENV_VARIABLE_NAME, "false").lower()
        if config_str in ["false", "f", "n", "no", "off",  "0"]:
            return
        # legacy support
        if config_str in ["true", "t", "1", "on", "all", "range", "traceme"]:
            self._synapse = True
            self._hw = False
            self._traceme = (config_str == "traceme")
            self._disable_autostart = (config_str == "range")
            return

        config_list = config_str.split(",")
        if "synapse" in config_list:
            self._synapse = True
        if "hw" in config_list:
            self._hw = True
        if "tf" in config_list:
            self._traceme = True

    def update_range(self, new_range):
        self._range = new_range
        self._log_file_name = ""

    def check(self, tf_hook_enabled=False):
        config_ok = True
        if not self.required:
            _log.error(f"Synapse Logger was not enabled, please set {self.CONFIG_ENV_VARIABLE_NAME}!")
            config_ok = False
        if tf_hook_enabled and not self._range:
            _log.error(f"Setting {self.RANGE_ENV_VARIABLE_NAME} is required  for profiler hook (TF_HOOK_MODE) to work!")
            config_ok = False
        if not config_ok:
            _log.error(self.get_usage_msg())
        return config_ok


    @classmethod
    def get_usage_msg(cls):
        msg_lst = []
        msg_lst.append(f" * Configuring profiler requires following variables to be set:")
        msg_lst.append(f" * \t{cls.CONFIG_ENV_VARIABLE_NAME} - required for configuring the provider. Comma separated list")
        msg_lst.append(f" * \t{cls.RANGE_ENV_VARIABLE_NAME} - for establishing range of collection when using hook.")
        msg_lst.append(" * Available providers: fw hw")
        msg_lst.append(" * \tsynapse - enable synapse calls logging in Habana TensorFlow")
        msg_lst.append(" * \thw - enable hardware profilers")
        msg_lst.append(" * Supported range formats are  'X-Y' or 'X:Y', where X and Y are numbers of start and stop iteration respectively.")
        return "\n".join(msg_lst)


    @property
    def log_from_start(self):
        # Logs from start when autostart was not disabled and range was not set.
        return (not self._disable_autostart) and (not self._range)

    @property
    def hw_tracing_enabled(self):
        return self._hw

    @property
    def synapse_tracing_enabled(self):
        return self._synapse

    @property
    def tf_profiler_enabled(self):
        return self._traceme

    @property
    def required(self):
        return self._synapse or self._hw

    @property
    def steps_to_log(self):
        return list(self._range)

    @property
    def synapse_log_file_name(self):
        if not self._log_file_name:
            log_file_name = [""] if comm_size() == 1 else [
                "rank_{}".format(comm_rank())]
            if self._range:
                if len(self._range) == 1:
                    log_file_name.append("step_{}".format(self._range[0]))
                if len(self._range) > 1:
                    log_file_name.append(
                        "steps_from_{}_to_{}".format(self._range[0], self._range[-1]))
            log_file_name.extend(["synapse_log"])
            self._log_file_name = "_".join(log_file_name)
        return self._log_file_name


class SynapseLoggerHelpers:
    # Indicates that py_synapse_logger object has been created
    _syn_logger_init_done = False
    # Indicates that synapse logger setup is done
    _syn_logger_setup_done = False
    _syn_logger = None
    _syn_logger_config = None

    @staticmethod
    def synapse_logger_config():
        if not SynapseLoggerHelpers._syn_logger_config:
            SynapseLoggerHelpers._syn_logger_config = SynapseLoggerConfig()
        return SynapseLoggerHelpers._syn_logger_config

    @staticmethod
    def synapse_logger():
        config = SynapseLoggerHelpers.synapse_logger_config()
        if not SynapseLoggerHelpers._syn_logger_init_done and config.required:
            import habana_frameworks.tensorflow as htf
            import habana_frameworks.tensorflow.py_synapse_logger as syn_log
            SynapseLoggerHelpers._syn_logger = syn_log
            SynapseLoggerHelpers._syn_logger_init_done = True
        return SynapseLoggerHelpers._syn_logger

    @staticmethod
    def _setup_synapse_logger(log_name_prefix=""):
        if SynapseLoggerHelpers._syn_logger_setup_done:
            # nothing to do here
            return

        if log_name_prefix != "":
            _log.warning(
                "Providing log name prefix for _setup_synapse_logger is DEPRECATED")

        syn_log = SynapseLoggerHelpers.synapse_logger()
        config = SynapseLoggerConfig()
        if not syn_log:
            logger_required = config.required
            assert not logger_required, "SynapseLoggerHelpers.synapse_logger() returns None when logger is enabled"
            return
        syn_log.command("disable")
        syn_log.command("stop_data_capture")
        if config.synapse_tracing_enabled:
            syn_log.command("file_name={}".format(
                config.synapse_log_file_name))
            syn_log.command("category_mask=0x3")
            if config.tf_profiler_enabled:
                syn_log.command("enable_tf_profiler")
            if config.log_from_start:
                syn_log.command("restart")
        SynapseLoggerHelpers._syn_logger_setup_done = True


class SynapseLoggerHook(tf.estimator.SessionRunHook):

    def __init__(self, steps_to_log=None, profile_hw=False):
        tf.estimator.SessionRunHook.__init__(self)
        self._step_cnt = 0
        self._profile_hw = profile_hw
        config = SynapseLoggerHelpers.synapse_logger_config()

        # Legacy suport
        if steps_to_log:
            # Updating range in config will also update file name
            config.update_range(steps_to_log)

        config.check(tf_hook_enabled=True)

        self._steps_to_log = config.steps_to_log
        self._syn_logger_running = False

    def before_run(self):
        if not self._syn_logger_running:
            if self._step_cnt in self._steps_to_log:
                synapse_logger_start(
                    self._steps_to_log, profile_hw=self._profile_hw)
                self._syn_logger_running = True
        if self._syn_logger_running:
            synapse_logger_log(
                f'"name":"call:step", "ph":"B", "cname":"vsync_highlight_color", "func":"void step(int it)", "args":{{"it":{self._step_cnt}}}'
            )

    def after_run(self):
        self._step_cnt += 1

        if self._syn_logger_running:
            synapse_logger_log(f'"name":"call:step", "ph":"E"')
            if self._step_cnt not in self._steps_to_log:
                synapse_logger_stop(profile_hw=self._profile_hw)
                self._syn_logger_running = False


def synapse_logger_init():
    SynapseLoggerHelpers._setup_synapse_logger()


def synapse_logger_start(step_range=None, profile_hw=False):
    syn_log = SynapseLoggerHelpers.synapse_logger()
    config = SynapseLoggerHelpers.synapse_logger_config()
    if syn_log:
        if config.synapse_tracing_enabled:
            if step_range:
                config.update_range(step_range)
                syn_log.command("file_name={}".format(
                    config.synapse_log_file_name))
            syn_log.command("category_mask=0x3")
            syn_log.command("restart")
        if config.hw_tracing_enabled or profile_hw:
            if comm_size() == 1 or comm_rank() == 0:
                syn_log.start_hw_profile()
        # TODO: add tensorflow profiler to the hook
    else:
        logging.warning(
            "Synapse logger has not been enabled. Unable to start logging.")


def synapse_logger_stop(profile_hw=False):
    syn_log = SynapseLoggerHelpers.synapse_logger()
    config = SynapseLoggerHelpers.synapse_logger_config()
    if syn_log:
        if config.hw_tracing_enabled or profile_hw:
            if comm_size() == 1 or comm_rank() == 0:
                syn_log.stop_hw_profile()
        if config.synapse_tracing_enabled:
            syn_log.command("disable")
    else:
        logging.warning(
            "Synapse logger has not been enabled. Unable to start logging.")


def synapse_logger_log(log_msg):
    syn_log = SynapseLoggerHelpers.synapse_logger()
    config = SynapseLoggerHelpers.synapse_logger_config()
    if syn_log and config.synapse_tracing_enabled:
        syn_log.put_log(log_msg, 1)


def synapse_logger_is_configured():
    config = SynapseLoggerHelpers.synapse_logger_config()
    return config.check()


def synapse_logger_create_tf_hook():
    return SynapseLoggerHook()
