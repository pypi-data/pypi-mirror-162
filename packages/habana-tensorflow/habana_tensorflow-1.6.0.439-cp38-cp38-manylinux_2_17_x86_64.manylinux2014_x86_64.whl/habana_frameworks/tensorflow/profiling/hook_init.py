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
import inspect
from functools import wraps, partial
from copy import copy
import importlib
import sys
import logging
from keras.callbacks import Callback

_log = logging.getLogger(__file__)


def profiling_hook_init(profiling_config=None):
    """
    Injects Habana TF hooks that can be used e.g. to get HW trace for specific batch
    """

    profiling_config = _parse_profiling_env_flags(profiling_config)
    if profiling_config is False:
        return
    if profiling_config is None:
        raise Exception("failed to determine profiling config")
    hook_installer, factory, args = profiling_config

    tf_hook = factory(*args)
    if tf_hook is None:
        raise Exception("Failed to create hook")
    hook_installer(tf_hook)


def _parse_profiling_env_flags(mode=None):
    args = tuple()
    if mode is None:
        mode = os.environ.get("TF_HOOK_MODE", False)
    _log.info(f"hook config: {mode}")
    if mode is False:
        return False
    elif mode in ("v1", "keras", "ctl", "all"):
        factory = "habana_frameworks.tensorflow.synapse_logger_helpers.synapse_logger_create_tf_hook"
    else:
        mode, factory, args = mode.split(",")
        args = args.split(":")
    factory = factory.split(".")
    factory_module, factory_fn = ".".join(factory[:-1]), factory[-1]
    _log.info(f"loading hook factory {factory_fn} from module {factory_module}")
    factory_module = importlib.import_module(factory_module)
    factory = getattr(factory_module, factory_fn)

    installer_fn = f"install_hook_{mode}"
    installer = globals().get(installer_fn, None)
    if installer is None:
        _log.warning(f"Could not find hook installer {installer_fn}, continuing..")
        return None
    return installer, factory, args


def _append_param(func, arg, update):
    """
    Monkey-pathing helper that replaces a system library call with a
    wrapper that does some additional action.
    """

    params = inspect.signature(func).parameters
    arg_index = next(x[0] for x in zip(range(len(params)), params.items()) if x[1][0] == arg)

    def local_list(l):
        return [] if not l else copy(l)

    @wraps(func)
    def wrapper(*args, **kwargs):
        if len(args) > arg_index:
            args = args[:arg_index] + (update(local_list(args[arg_index])),) + args[arg_index + 1 :]
            func(*args, **kwargs)
        else:
            kwargs[arg] = update(local_list(kwargs.get(arg, params[arg].default)))
            func(*args, **kwargs)

    return wrapper


def install_hook_all(tf_hook):
    install_hook_v1(tf_hook)
    install_hook_keras(tf_hook)
    install_hook_ctl(tf_hook)


def install_hook_v1(tf_hook):
    # Wrapping TF 1.x
    # Estimator API also uses MonitoredSession inside so it supports it as well:
    import tensorflow as tf

    _log.info("TF_HOOK: v1 enabled")
    default_session_run = tf.compat.v1.train.MonitoredSession.run

    def hooked_session_run(self, *args, **kwargs):
        tf_hook.before_run()
        default_outputs = default_session_run(self, *args, **kwargs)
        tf_hook.after_run()
        return default_outputs

    tf.compat.v1.train.MonitoredSession.run = hooked_session_run


def install_hook_keras(tf_hook):
    # Wrapping Keras (model.fit, model.fit_generator, both training and training_v1):
    _log.info("TF_HOOK: keras enabled")
    from keras.engine import training, training_v1

    class KerasHookAdapter(Callback):
        def on_train_batch_begin(self, batch, logs=None):
            _log.info("TF_HOOK: before run")
            tf_hook.before_run()

        def on_train_batch_end(self, batch, logs=None):
            _log.info("TF_HOOK: after run")
            tf_hook.after_run()

        on_batch_begin = on_train_batch_begin
        on_batch_end = on_train_batch_end

    callback = tf_hook if isinstance(tf_hook, Callback) else KerasHookAdapter()

    def add_callback(param):
        param.append(callback)
        return param

    training.Model.fit = _append_param(training.Model.fit, "callbacks", add_callback)
    training.Model.fit_generator = _append_param(training.Model.fit_generator, "callbacks", add_callback)

    training_v1.Model.fit = _append_param(training_v1.Model.fit, "callbacks", add_callback)
    training_v1.Model.fit_generator = _append_param(training_v1.Model.fit_generator, "callbacks", add_callback)


def install_hook_ctl(tf_hook):
    """
    Installs a training hook or callback into a custom training loop (CTL)
    topology.

    Installer scans modules that are already loaded into runtime in search of
    two patch points: controller.Controller and get_profiler_callback. The
    latter one is replaced to produce custom Callback instance instead of
    typicall CTL profiler callback. Keep in mind that get_profiler_callback is
    only issued for runs with enabled profiling. This is commonly done with
    --profile_steps training command argument, but inspect your topology for
    details.
    """
    _log.info("TF_HOOK: ctl enabled")

    class CtlHookAdapter(Callback):
        def on_batch_begin(self, batch, logs=None):
            _log.info("TF_HOOK: before run")
            tf_hook.before_run()

        def on_batch_end(self, batch, logs=None):
            _log.info("TF_HOOK: after run")
            tf_hook.after_run()

    callback = tf_hook if isinstance(tf_hook, Callback) else CtlHookAdapter()

    model_garden_modules = list()
    model_garden_root = os.environ["MODEL_GARDEN_ROOT"]
    for name, module in sys.modules.items():
        spec = getattr(module, "__spec__", None)
        if spec is not None and spec.origin is not None and spec.origin.startswith(model_garden_root):
            model_garden_modules.append(module)

    controller_module = list(module for module in model_garden_modules if getattr(module, "Controller", False))

    keras_utils = list(
        module
        for module in model_garden_modules
        if module.__name__.endswith("keras_utils") and getattr(module, "get_profiler_callback", False)
    )
    if len(controller_module) != 1 or len(keras_utils) != 1:
        _log.warning("expexting exactly one controller module and one keras_utuils module to patch")
        return None
    controller_module, keras_utils = controller_module[0], keras_utils[0]
    _log.info(f"Patching {controller_module} and {keras_utils}")

    controller_type = controller_module.Controller

    class ControllerWrapper:
        """Used to early close training from callback object. Keras
        model has stop_training bool but ctl topology controller has no similar
        feature. Controller train function is however comparing global step
        against train_steps. Callback may use this bypass access to
        controller.train_steps to force early stop of the training."""

        def __init__(self):
            self.controller = None

        def create_controller(self, factory, *args, **kwargs):
            assert self.controller is None
            self.controller = factory(*args, **kwargs)
            _log.info(f"created wrapped controller {self.controller}")
            opt_set_controller = getattr(callback, "set_controller", None)
            if opt_set_controller is not None:
                opt_set_controller(self.controller)
            return self.controller

    controller_wrapper = ControllerWrapper()

    setattr(controller_module, "Controller", partial(controller_wrapper.create_controller, controller_type))

    def get_profiler_callback(model_dir, profile_steps, enable_tensorboard, steps_per_epoch):
        _log.info(
            f"get_profiler_callback model_dir={model_dir}, profile_steps={profile_steps}, enable_tensorboard={enable_tensorboard}, steps_per_epoch={steps_per_epoch}"
        )
        return callback

    setattr(keras_utils, "get_profiler_callback", get_profiler_callback)
