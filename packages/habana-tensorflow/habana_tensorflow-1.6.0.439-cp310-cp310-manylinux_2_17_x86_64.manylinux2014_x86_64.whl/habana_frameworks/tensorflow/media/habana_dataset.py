###############################################################################
# Copyright (C) 2022 Habana Labs, Ltd. an Intel Company
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
from habana_frameworks.tensorflow.library_loader import media_ops
from tensorflow.python.ops import gen_dataset_ops
from tensorflow.python.eager import function
from tensorflow.python.data.ops import dataset_ops
import gc
import atexit


class HabanaDataset(dataset_ops.DatasetSource):

    def __init__(self, output_shapes, output_types, pipeline):
        self._output_signature = tuple(map(lambda x: tf.TensorSpec(shape=x[0], dtype=x[1]),
                                           zip(output_shapes, output_types)))
        self._proxy_initialized = False

        def glue_init():
            pipeline.iter_init()

        def glue_finalize():
            pipeline.del_iter()

        @function.defun
        @tf.autograph.experimental.do_not_convert
        def init_func():
            tf.py_function(glue_init, [], Tout=[])

        @function.defun_with_attributes(attributes={"experimental_ints_on_device": True})
        @tf.autograph.experimental.do_not_convert
        def next_func():
            return media_ops.HabanaDatasetNext(pipeline_id=self._pipeline_id, output_shapes=output_shapes, output_types=output_types)

        @function.defun
        @tf.autograph.experimental.do_not_convert
        def finalize_func():
            tf.py_function(glue_finalize, [], Tout=[])
            return tf.constant(0, tf.uint64)

        pipeline.build()
        if tf.compat.v1.executing_eagerly():
            self._proxy = media_ops.CreateMediaProxy()
            pipeline.set_proxy("TF_FW", int(self._proxy.numpy()))
        else:
            create_proxy = media_ops.CreateMediaProxy()
            with tf.compat.v1.Session() as sess:
                self._proxy = sess.run(create_proxy)
            pipeline.set_proxy("TF_FW", int(self._proxy))
        self._proxy_initialized = True
        from habana_frameworks.tensorflow.media.python_bindings import register_pipeline
        self._pipeline_id = register_pipeline(pipeline)
        self._init_func = init_func._get_concrete_function_internal()
        self._next_func = next_func._get_concrete_function_internal()
        self._finalize_func = finalize_func._get_concrete_function_internal()
        self._init_captured_args = self._init_func.captured_inputs
        self._next_captured_args = self._next_func.captured_inputs
        self._finalize_captured_args = self._finalize_func.captured_inputs
        with tf.device("/device:HPU:0"):
            variant_tensor = gen_dataset_ops.generator_dataset(
                self._init_captured_args,
                self._next_captured_args,
                self._finalize_captured_args,
                init_func=self._init_func,
                next_func=self._next_func,
                finalize_func=self._finalize_func,
                output_shapes=output_shapes,
                output_types=output_types)

        # there is a hang happening on application exit, that has something to do with how tf.py_function & Python GIL
        # are interacting together. Many similar issues were reported to TensorFlow.
        # I.e. in https://github.com/tensorflow/tensorflow/issues/21277
        # Simple WA is to enforce gc.collect() at the end of application
        def at_exit(pipeline):
            tf.keras.backend.clear_session()
            pipeline.del_iter()
            self._finalize_proxy()
            gc.collect()
        atexit.register(at_exit, pipeline)

        super(HabanaDataset, self).__init__(variant_tensor)

    def _finalize_proxy(self):
        if not self._proxy_initialized:
            return

        from habana_frameworks.tensorflow.media.python_bindings import finalize_media
        finalize_media()

        self._proxy_initialized = False

    @property
    def element_spec(self):
        return self._output_signature
