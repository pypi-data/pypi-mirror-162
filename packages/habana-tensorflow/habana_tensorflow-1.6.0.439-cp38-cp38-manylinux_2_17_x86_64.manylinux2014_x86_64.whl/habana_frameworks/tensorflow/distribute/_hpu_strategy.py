# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
###############################################################################
# Copyright (C) 2021-2022 Habana Labs, Ltd. an Intel Company
# All Rights Reserved.
#
# Unauthorized copying of this file or any element(s) within it, via any medium
# is strictly prohibited.
# This file contains Habana Labs, Ltd. proprietary and confidential information
# and is subject to the confidentiality and license agreements under which it
# was provided.
#
###############################################################################

import tensorflow
from tensorflow.python.distribute import collective_all_reduce_strategy

INSTALL_PRE_ALLREDUCE_BARRIER_ENV_VAR_NAME = "TF_HABANA_COLLECTIVE_REDUCE_SYNC"


def disable_collective_reduce_packing():
    """ Disables the automatic gradient tensor packing (grouping using concat/split) affecting CollectiveReduceV2.
    """
    from tensorflow.python.distribute import cross_device_utils

    def custom_batch_all_reduce(collective_replica_launcher, input_tensor_packs, options):
        """ Monkey-patched custom TensorFlow method, which does not call array_ops.concat/split.
            Original source: tensorflow/tensorflow/python/distribute/cross_device_utils.py
        """
        options = collective_replica_launcher._options.merge(options)
        outputs = []
        for pack in input_tensor_packs:
            for input_tensor in pack:
                outputs.append(collective_replica_launcher.all_reduce(
                    input_tensor, None, options))
        return outputs

    cross_device_utils.CollectiveReplicaLauncher.batch_all_reduce = custom_batch_all_reduce


_is_b50853_wa_installed = False


def _install_b50853_wa_now():
    from tensorflow.python.framework.c_api_util import ScopedTFGraph

    def _noop_func(_):
        pass

    ScopedTFGraph.__del__ = _noop_func


def install_b50853_wa_if_applicable():
    """ Installs a work-around to TensorFlow 2.5.0, 2.5.1, 2.6.0 issue b50853.
        See: https://github.com/tensorflow/tensorflow/issues/50853
    """
    if not tensorflow.executing_eagerly():
        return

    global _is_b50853_wa_installed
    if _is_b50853_wa_installed:
        return

    import atexit
    atexit.register(_install_b50853_wa_now)

    _is_b50853_wa_installed = True


_allcompare_installed = False


def install_allcompare():
    global _allcompare_installed
    if _allcompare_installed:
        return

    from habana_frameworks.tensorflow.internal.allcompare import (
        AllCompare, tf_distribute_broadcast_sample)
    from tensorflow.python.ops import collective_ops

    orig_all_reduce_v2 = collective_ops.all_reduce_v2

    def _proxy_all_reduce_v2(t, group_size, group_key, instance_key, merge_op="Add", *args, **kwargs):
        reduced_t = orig_all_reduce_v2(
            t, group_size, group_key, instance_key, merge_op, *args, **kwargs)

        allcompare = AllCompare.access_if_enabled()
        if allcompare is not None and merge_op in ["Add", "Mean"]:
            compared_tensor = reduced_t
            if merge_op == "Add":
                compared_tensor /= group_size
            compared_tensor_expected = t

            err_tensor, _ = allcompare.expect_similar(
                compared_tensor, compared_tensor_expected, name_prefix="AllCompare/CollectiveReduceV2")

            with tensorflow.control_dependencies([err_tensor]):
                reduced_t = tensorflow.identity(reduced_t)

        return reduced_t

    collective_ops.all_reduce_v2 = _proxy_all_reduce_v2
    _allcompare_installed = True

    allcompare = AllCompare.access_if_enabled()
    if allcompare is not None:
        allcompare.logger.warning(
            "Due to HPUStrategy usage, setting all-compare broadcasting method to tf.distribute (based on CollectiveBcastSend/Recv).")
        allcompare.broadcast_sample_fn = tf_distribute_broadcast_sample

        allcompare.logger.warning(
            "Due to HPUStrategy usage, disabling TensorFlow's gradient tensor packing for CollectiveReduceV2.")
        disable_collective_reduce_packing()


_pre_allreduce_barrier_installed = False
_pre_allreduce_barrier_global_instance_key = 0x7E000000


def install_pre_allreduce_barrier(num_replicas_in_sync: int):
    global _pre_allreduce_barrier_installed
    if _pre_allreduce_barrier_installed:
        return

    import tensorflow as tf
    from tensorflow.python.ops import collective_ops

    orig_all_reduce_v2 = collective_ops.all_reduce_v2

    def _proxy_all_reduce_v2(t, group_size, group_key, instance_key, merge_op="Add", *args, **kwargs):
        with tf.device("/device:CPU:0"):
            dummy_tensor = tf.constant([1.0], dtype=tf.float32)
            global _pre_allreduce_barrier_global_instance_key
            _pre_allreduce_barrier_global_instance_key += 1
            with tf.control_dependencies([t]):
                sync_op = collective_ops.all_gather(
                    dummy_tensor, group_size=num_replicas_in_sync, group_key=-1, instance_key=_pre_allreduce_barrier_global_instance_key, communication_hint="ring")

        with tf.control_dependencies([sync_op]):
            return orig_all_reduce_v2(
                t, group_size, group_key, instance_key, merge_op, *args, **kwargs)

    collective_ops.all_reduce_v2 = _proxy_all_reduce_v2
    _pre_allreduce_barrier_installed = True


def comm_init(num_replicas_in_sync: int):
    import tensorflow as tf
    from tensorflow.python.ops import collective_ops

    from ..library_loader import habana_ops

    with tf.device("/device:HPU:0"):
        x = habana_ops.ops.CollectiveCommHandshakeProducer()
    with tf.device("/device:CPU:0"):
        x = collective_ops.all_gather(
            x, group_size=num_replicas_in_sync, group_key=-1, instance_key=1, communication_hint="ring")
    with tf.device("/device:HPU:0"):
        x = habana_ops.ops.CollectiveCommHandshakeConsumer(i=x)

    return x


class HPUStrategy(collective_all_reduce_strategy.CollectiveAllReduceStrategy):
    def __init__(self, cluster_resolver=None, communication_options=None, config: tensorflow.compat.v1.ConfigProto = None, server: tensorflow.distribute.Server = None):
        if cluster_resolver is None:
            cluster_resolver = tensorflow.distribute.cluster_resolver.TFConfigClusterResolver()

        # Note that 'communication' parameter has been intentionally omitted.
        self.__class__ = collective_all_reduce_strategy.CollectiveAllReduceStrategy
        if communication_options is None:
            from tensorflow.python.distribute import collective_util
            communication_options = collective_util.Options()
        super(collective_all_reduce_strategy.CollectiveAllReduceStrategy, self).__init__(
            HabanaCollectiveAllReduceExtended(
                self, cluster_resolver=cluster_resolver, communication_options=communication_options)
        )

        from tensorflow.python.distribute import distribute_lib
        distribute_lib.distribution_strategy_gauge.get_cell(
            "V2").set("MultiWorkerMirroredStrategy")
        # pylint: disable=protected-access
        distribute_lib.distribution_strategy_replica_gauge.get_cell(
            "num_workers").set(self.extended._num_workers)
        distribute_lib.distribution_strategy_replica_gauge.get_cell(
            "num_replicas_per_worker").set(self.extended._num_devices_per_worker)

        # In TF 1.15 the following update_config_proto() invocation is a necessary hack to the strategy's config_proto to prevent a hang.
        #   See: https://github.com/tensorflow/tensorflow/issues/31499
        # In TF 2.2 it is no longer needed.
        # Apparently it is still required in TF 2.5 for broadcasts.
        if config is None:
            config = tensorflow.compat.v1.ConfigProto()
            config.allow_soft_placement = False
        self._config = self.update_config_proto(config)

        if not tensorflow.executing_eagerly():
            if server is None:
                # Create and start the gRPC server for this worker.
                server = tensorflow.distribute.Server(
                    cluster_resolver.cluster_spec(),
                    job_name=cluster_resolver.task_type,
                    task_index=cluster_resolver.task_id,
                    config=self._config)
            self._target = server.target
            self.extended._std_server_started = True

        comm_init_op = comm_init(self.num_replicas_in_sync)

        if not tensorflow.executing_eagerly():
            with tensorflow.compat.v1.Session(self._target) as session:
                session.run(comm_init_op)

        install_b50853_wa_if_applicable()
        install_allcompare()

        from habana_frameworks.tensorflow.util import condition_env_var
        if condition_env_var(INSTALL_PRE_ALLREDUCE_BARRIER_ENV_VAR_NAME, False):
            install_pre_allreduce_barrier(self.num_replicas_in_sync)


class HabanaCollectiveAllReduceExtended(collective_all_reduce_strategy.CollectiveAllReduceExtended):
    def __init__(self, container_strategy, cluster_resolver, communication_options):
        super(HabanaCollectiveAllReduceExtended, self).__init__(
            container_strategy=container_strategy,
            cluster_resolver=cluster_resolver,
            communication_options=communication_options)
        self.experimental_enable_get_next_as_optional = False

    def _initialize_strategy(self, cluster_resolver):
        if cluster_resolver.cluster_spec().as_dict():
            self._initialize_multi_worker(cluster_resolver)
        else:
            self._initialize_local(cluster_resolver)

    def _initialize_local_devices(self, cluster_resolver, worker_device):
        local_devices = (
            f"{worker_device}/device:HPU:0",)
        return local_devices, "HPU"

    def _initialize_local(self, cluster_resolver, devices=None):
        # Pass devices=None, so _initialize_local_devices will be used to pick up HPU device.
        super(HabanaCollectiveAllReduceExtended, self)._initialize_local(
            cluster_resolver, devices=None)
