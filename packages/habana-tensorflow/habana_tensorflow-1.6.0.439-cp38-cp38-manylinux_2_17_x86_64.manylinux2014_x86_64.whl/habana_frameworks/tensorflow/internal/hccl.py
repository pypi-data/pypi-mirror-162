###############################################################################
# Copyright (C) 2020-2022 Habana Labs, Ltd. an Intel Company
# All Rights Reserved.
#
# Unauthorized copying of this file or any element(s) within it, via any medium
# is strictly prohibited.
# This file contains Habana Labs, Ltd. proprietary and confidential information
# and is subject to the confidentiality and license agreements under which it
# was provided.
#
###############################################################################

import imp
import os

from ..lib_utils import libraries_location

# -----------------------------------------------------------------------------

_h = imp.load_source("hccl_python_wrapper", os.path.join(
    libraries_location, "hccl_python_wrapper.py"))

FloatVector = _h.FloatVector

# -----------------------------------------------------------------------------


def _check_status(status: int):
    if status != 0:
        raise Exception(f"HCCL error: {status}")


def _dtype_from_str(dtype_str):
    return {
        "fp": _h.hcclFloat32,
        "fp32": _h.hcclFloat32,
        "float": _h.hcclFloat32,
        "float32": _h.hcclFloat32,
        "bf": _h.hcclBfloat16,
        "bf16": _h.hcclBfloat16,
        "bfloat": _h.hcclBfloat16,
        "bfloat16": _h.hcclBfloat16,
    }[dtype_str]


def _reduction_op_from_str(reduction_op_str):
    return {
        "sum": _h.hcclSum,
        "prod": _h.hcclProd,
        "max": _h.hcclMax,
        "min": _h.hcclMin,
    }[reduction_op_str]

# -----------------------------------------------------------------------------


def dtype_size(dtype):
    return {
        "fp": 4,
        "fp32": 4,
        "float": 4,
        "float32": 4,
        "bf": 2,
        "bf16": 2,
        "bfloat": 2,
        "bfloat16": 2,
    }[dtype]

# -----------------------------------------------------------------------------


def get_unique_id():
    """ Generates an Id to be used in hcclCommInitRank. hcclGetUniqueId should be
        called once and the Id should be distributed to all ranks in the
        communicator before calling hcclCommInitRank.
    """
    uniqueId_ptr = _h.new_hcclUniqueId_ptr()
    try:
        _check_status(_h.hcclGetUniqueId(uniqueId_ptr))
        uniqueId = bytes(_h.unique_id_to_byte_vector(
            _h.hcclUniqueId_ptr_value(uniqueId_ptr)))
        return uniqueId
    finally:
        _h.delete_hcclUniqueId_ptr(uniqueId_ptr)


# -----------------------------------------------------------------------------

currently_set_device = None


class Device:
    instance = None

    def __init__(self, device_id: int):
        assert Device.instance is None, "There may be only one instance of Device class."
        Device.instance = self

        self.device_id = device_id
        self._collective_stream_handle = None
        self.set_device()

    def set_device(self):
        # Set device as current and and open it once.
        _check_status(_h.hcclxSetDevice(self.device_id))
        global currently_set_device
        currently_set_device = self

    def close(self):
        self._release_collective_stream()

        # Close the device.
        _check_status(_h.hcclxCloseDevice(self.device_id))
        global currently_set_device
        assert currently_set_device == self
        currently_set_device = None

        assert Device.instance is self, "Internal error"
        Device.instance = None

    @property
    def collective_stream_handle(self):
        if self._collective_stream_handle is None:
            self._acquire_collective_stream()
            assert self._collective_stream_handle is not None, "Expected to have a valid collective stream handle at this point."

        return self._collective_stream_handle

    def _acquire_collective_stream(self):
        assert self._collective_stream_handle is None, "Collective stream has been already acquired."
        collectiveStreamHandle_ptr = _h.new_intptr_ptr()
        try:
            _check_status(_h.hcclxAcquireCollectiveStream(
                self.device_id, _h.as_hccl_stream_handle_ptr(collectiveStreamHandle_ptr)))
            self._collective_stream_handle = _h.as_hccl_stream_handle(
                _h.intptr_ptr_value(collectiveStreamHandle_ptr))
        finally:
            _h.delete_intptr_ptr(collectiveStreamHandle_ptr)

    def _release_collective_stream(self):
        if self._collective_stream_handle is not None:
            _check_status(_h.hcclxReleaseCollectiveStream(
                self._collective_stream_handle))
            self._collective_stream_handle = None

    def __enter__(self):
        self.set_device()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def create_device(ordinal: int):
    deviceId_ptr = _h.new_int_ptr()
    try:
        _check_status(
            _h.hcclxCreateDevice(ordinal, deviceId_ptr))
        device_id = _h.int_ptr_value(deviceId_ptr)
        return Device(device_id)
    finally:
        _h.delete_int_ptr(deviceId_ptr)


def open_device(device_id: int):
    _check_status(_h.hcclxOpenDevice(device_id))
    return Device(device_id)

# -----------------------------------------------------------------------------


class Comm:
    """ Represents HCCL communicator and manages its opaque handle.
    """

    def __init__(self, handle):
        self.handle = handle

    def count(self):
        """ Gets the number of ranks in the communicator clique.
        """
        count_ptr = _h.new_intptr_ptr()
        try:
            _check_status(_h.hcclCommCount(self.handle, count_ptr))
            return _h.intptr_ptr_value(count_ptr)
        finally:
            _h.delete_intptr_ptr(count_ptr)

    def device(self):
        """ Returns the Habana device number associated with the communicator.
        """
        device_ptr = _h.new_intptr_ptr()
        try:
            _check_status(_h.hcclCommSynDevice(
                self.handle, device_ptr))
            return _h.intptr_ptr_value(device_ptr)
        finally:
            _h.delete_intptr_ptr(device_ptr)

    def user_rank(self):
        """ Returns the user-ordered "rank" associated with the communicator.
        """
        userRank_ptr = _h.new_intptr_ptr()
        try:
            _check_status(_h.hcclCommUserRank(
                self.handle, userRank_ptr))
            return _h.intptr_ptr_value(userRank_ptr)
        finally:
            _h.delete_intptr_ptr(userRank_ptr)

    def destroy(self):
        """ Frees resources associated with communicator object,
            but waits for any operations that might still be running on the device.
        """
        Device.instance._release_collective_stream()
        _h.hcclCommDestroy(self.handle)
        del self.handle

    def abort(self):
        """ Frees resources associated with communicator object and
            aborts any operations that might still be running on the device.
        """
        _h.hcclCommAbort(self.handle)
        del self.handle

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.destroy()

# -----------------------------------------------------------------------------


def comm_init_rank(nranks: int, unique_id: bytes, rank: int):
    """ Creates a new communicator (multi thread/process version).
        rank must be between 0 and nranks-1 and unique within a communicator clique.
        Each rank is associated to a Habana device, which has to be set before calling hcclCommInitRank.
        hcclCommInitRank implicitly synchronizes with other ranks, so it must be
        called by different threads/processes or use hcclGroupStart/hcclGroupEnd.
    """
    commId_ptr = _h.new_intptr_ptr()
    try:
        uniqueId = _h.unique_id_from_byte_vector(
            _h.ByteVector(unique_id))
        _check_status(_h.hcclCommInitRank(
            _h.as_comm_handle_ptr(commId_ptr), nranks, uniqueId, rank))
        comm_handle = _h.as_comm_handle(
            _h.intptr_ptr_value(commId_ptr))
        return Comm(comm_handle)
    finally:
        _h.delete_intptr_ptr(commId_ptr)


# -----------------------------------------------------------------------------

locked_address_map = {}


class DevicePtr:
    """ Represents a locked (pinned) HPU buffer address.
        That address have a raw hardware pointer that can be used in the underlying Synapse calls.
    """

    def __init__(self, addr: int):
        self.addr = addr
        global locked_address_map
        if addr in locked_address_map:
            self._ptr = locked_address_map[addr][0]
            locked_address_map[addr][1] += 1
        else:
            self._ptr = _h.hcclxLockDeviceAddress2(addr)
            if _h.void_ptr_to_int64(self._ptr) == 0:
                raise Exception(
                    f"HCCL error: Locking device address {addr} failed.")
            locked_address_map[addr] = [self._ptr, 1]

    def hw_ptr(self):
        return self._ptr

    def unlock(self):
        if self._ptr is not None:
            global locked_address_map
            if self.addr in locked_address_map:
                locked_address_map[self.addr][1] -= 1
                if locked_address_map[self.addr][1] == 0:
                    _h.hcclxUnlockDeviceAddress(
                        locked_address_map[self.addr][0])
                    del locked_address_map[self.addr]
            self._ptr = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unlock()


class DeviceBuffer:
    """ Represents a HPU memory buffer, i.e. starting address and allocation size.
    """

    def __init__(self, addr: int, size: int, free_on_exit: bool):
        self.addr = addr
        self.size = size
        self.free_on_exit = free_on_exit

    def subbuffer(self, start_offset: int, end_offset: int = None, size_offset: int = None):
        assert (end_offset is None) ^ (size_offset is None), \
            "end_offset or size_offset has to be specified, but not both"

        new_addr = self.addr + start_offset
        if end_offset is not None:
            new_size = self.size - start_offset + end_offset
        if size_offset is not None:
            new_size = self.size + size_offset

        return DeviceBuffer(new_addr, new_size, free_on_exit=False)

    def lock_addr(self, offset: int = 0):
        return DevicePtr(self.addr + offset)

    def free(self):
        """ Frees the underlying memory allocation as long as the buffer was allocated using malloc() function, thus has an exlusive ownership to it.
        """
        assert self.free_on_exit, "Unable to free a buffer which does not have ownership to the underlying allocation."
        _check_status(_h.hcclxFree(_h.int64_to_void_ptr(self.addr)))

    def _hw_ptr(self, offset=0):
        return _h.int64_to_void_ptr(self.addr + offset)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.free_on_exit:
            self.free()

    def upload_data(self, data, dtype):
        if not isinstance(data, _h.FloatVector):
            data = _h.FloatVector(data)
        assert self.size >= len(data) * dtype_size(dtype), \
            "Allocated buffer is too small to contain all the data."

        dtype = _dtype_from_str(dtype)
        if dtype != _h.hcclFloat32:
            data = _h.convert_float_to_data(data, dtype)

        _h.upload_data(self._hw_ptr(), data)

    def download_data(self, dtype):
        elem_size = dtype_size(dtype)
        assert self.size % elem_size == 0, "Allocated buffer is not aligned to the size of requested dtype."

        dtype = _dtype_from_str(dtype)
        if dtype != _h.hcclFloat32:
            data = _h.ByteVector(self.size)
        else:
            data = _h.FloatVector(self.size // elem_size)

        _h.download_data(data, self._hw_ptr())

        if dtype != _h.hcclFloat32:
            data = _h.convert_data_to_float(data, dtype)

        return data


def malloc(size: int):
    """ Allocates a memory buffer on HPU and returns an instance of DeviceBuffer class.
    """
    addr = _h.hcclxMalloc2(size)
    if addr == 0:
        raise Exception(
            f"HCCL error: Device memory allocation failed for size={size}")
    return DeviceBuffer(addr, size, True)


# -----------------------------------------------------------------------------


def reduce(send_buffer: DeviceBuffer, receive_buffer: DeviceBuffer, count: int, dtype: str, reduction_op: str, root: int, comm: Comm, stream_handle: int):
    """ Reduces data arrays of length count in send_buffer into receive_buffer using reduction_op operation.
    """
    dtype = _dtype_from_str(dtype)
    reduction_op = _reduction_op_from_str(reduction_op)

    input_addresses = _h.VoidPtrVector([send_buffer._hw_ptr()])
    _check_status(_h.hcclxPrepareStream2(
        stream_handle, input_addresses))
    del input_addresses

    with send_buffer.lock_addr() as send_ptr, receive_buffer.lock_addr() as receive_ptr:
        _check_status(_h.hcclReduce(send_ptr.hw_ptr(), receive_ptr.hw_ptr(
        ), count, dtype, reduction_op, root, comm.handle, stream_handle))

    output_addresses = _h.VoidPtrVector([receive_buffer._hw_ptr()])
    _check_status(_h.hcclxSubmitEvents2(
        stream_handle, output_addresses))
    del output_addresses

# -----------------------------------------------------------------------------


def allreduce(send_buffer: DeviceBuffer, receive_buffer: DeviceBuffer, count: int, dtype: str, reduction_op: str, comm: Comm, stream_handle: int):
    """ Reduces data arrays of length count in send_buffer using reduction_op operation,
        and leaves identical copies of result on each receive_buffer.
    """
    dtype = _dtype_from_str(dtype)
    reduction_op = _reduction_op_from_str(reduction_op)

    input_addresses = _h.VoidPtrVector([send_buffer._hw_ptr()])
    _check_status(_h.hcclxPrepareStream2(
        stream_handle, input_addresses))
    del input_addresses

    with send_buffer.lock_addr() as send_ptr, receive_buffer.lock_addr() as receive_ptr:
        _check_status(_h.hcclAllReduce(send_ptr.hw_ptr(), receive_ptr.hw_ptr(
        ), count, dtype, reduction_op, comm.handle, stream_handle))

    output_addresses = _h.VoidPtrVector([receive_buffer._hw_ptr()])
    _check_status(_h.hcclxSubmitEvents2(
        stream_handle, output_addresses))
    del output_addresses

# -----------------------------------------------------------------------------


def reduce_scatter(send_buffer: DeviceBuffer, receive_buffer: DeviceBuffer, receive_count: int, dtype: str, reduction_op: str, comm: Comm, stream_handle: int):
    """ Reduces data in send_buffer using reduction_op operation and leaves reduced result
        scattered over the devices so that receive_buffer on rank i will contain the i-th
        block of the result.
        Assumes send_count is equal to nranks*receive_count, which means that send_buffer
        should have a size of at least nranks*receive_buffer elements.
    """
    dtype = _dtype_from_str(dtype)
    reduction_op = _reduction_op_from_str(reduction_op)

    input_addresses = _h.VoidPtrVector([send_buffer._hw_ptr()])
    _check_status(_h.hcclxPrepareStream2(
        stream_handle, input_addresses))
    del input_addresses

    with send_buffer.lock_addr() as send_ptr, receive_buffer.lock_addr() as receive_ptr:
        _check_status(_h.hcclReduceScatter(send_ptr.hw_ptr(), receive_ptr.hw_ptr(
        ), receive_count, dtype, reduction_op, comm.handle, stream_handle))

    output_addresses = _h.VoidPtrVector([receive_buffer._hw_ptr()])
    _check_status(_h.hcclxSubmitEvents2(
        stream_handle, output_addresses))
    del output_addresses

# -----------------------------------------------------------------------------


def allgather(send_buffer: DeviceBuffer, receive_buffer: DeviceBuffer, send_count: int, dtype: str, comm: Comm, stream_handle: int):
    """ Each device gathers send_count values from other HPUs into receive_buffer,
        receiving data from rank i at offset i*send_count.
        Assumes recv_count is equal to nranks*send_count, which means that receive_buffer
        should have a size of at least nranks*send_count elements.
    """
    dtype = _dtype_from_str(dtype)

    input_addresses = _h.VoidPtrVector([send_buffer._hw_ptr()])
    _check_status(_h.hcclxPrepareStream2(
        stream_handle, input_addresses))
    del input_addresses

    with send_buffer.lock_addr() as send_ptr, receive_buffer.lock_addr() as receive_ptr:
        _check_status(_h.hcclAllGather(send_ptr.hw_ptr(
        ), receive_ptr.hw_ptr(), send_count, dtype, comm.handle, stream_handle))

    output_addresses = _h.VoidPtrVector([receive_buffer._hw_ptr()])
    _check_status(_h.hcclxSubmitEvents2(
        stream_handle, output_addresses))
    del output_addresses

# -----------------------------------------------------------------------------


def bcast(buffer: DeviceBuffer, count: int, dtype: str, root: int, comm: Comm, stream_handle: int):
    """ Copies count values from root to all other devices.
        root is the rank where data resides before the operation is started.
    """
    inout_addresses = _h.VoidPtrVector([buffer._hw_ptr()])
    _check_status(_h.hcclxPrepareStream2(
        stream_handle, inout_addresses))

    dtype = _dtype_from_str(dtype)
    with buffer.lock_addr() as buffer_ptr:
        _check_status(_h.hcclBcast(buffer_ptr.hw_ptr(),
                                   count, dtype, root, comm.handle, stream_handle))

    _check_status(_h.hcclxSubmitEvents2(
        stream_handle, inout_addresses))
    del inout_addresses


def broadcast(send_buffer: DeviceBuffer, receive_buffer: DeviceBuffer, count: int, dtype: str, root: int, comm: Comm, stream_handle: int):
    """ Copies count values from root to all other devices.
        root is the rank where data resides before the operation is started.
    """
    dtype = _dtype_from_str(dtype)

    input_addresses = _h.VoidPtrVector([send_buffer._hw_ptr()])
    _check_status(_h.hcclxPrepareStream2(
        stream_handle, input_addresses))
    del input_addresses

    with send_buffer.lock_addr() as send_ptr, receive_buffer.lock_addr() as receive_ptr:
        _check_status(_h.hcclBroadcast(send_ptr.hw_ptr(
        ), receive_ptr.hw_ptr(), count, dtype, root, comm.handle, stream_handle))

    output_addresses = _h.VoidPtrVector([receive_buffer._hw_ptr()])
    _check_status(_h.hcclxSubmitEvents2(
        stream_handle, output_addresses))
    del output_addresses

# -----------------------------------------------------------------------------


is_in_grouped_mode = False
recv_output_addresses_to_submit = []

# -----------------------------------------------------------------------------


def send(send_buffer: DeviceBuffer, count: int, dtype: str, peer: int, comm: Comm, stream_handle: int):
    """ Sends data from send_buffer to rank peer.
        Rank peer needs to call recv() with the same dtype and the same count from this rank.
        It is a blocking call for unless operation is a part of group within group_start() and group_end() section.
    """
    dtype = _dtype_from_str(dtype)

    inout_addresses = _h.VoidPtrVector([send_buffer._hw_ptr()])
    _check_status(_h.hcclxPrepareStream2(
        stream_handle, inout_addresses))

    with send_buffer.lock_addr() as send_ptr:
        _check_status(_h.hcclSend(send_ptr.hw_ptr(),
                                  count, dtype, peer, comm.handle, stream_handle))


def recv(receive_buffer: DeviceBuffer, count: int, dtype: str, peer: int, comm: Comm, stream_handle: int):
    """ Recieves data from rank peer to receive_buffer.
        Rank peer needs to call send() with the same dtype and the same count as this rank.
        It is a blocking call unless operation is a part of group within group_start() and group_end() section.
    """
    dtype = _dtype_from_str(dtype)

    with receive_buffer.lock_addr() as receive_ptr:
        _check_status(_h.hcclRecv(receive_ptr.hw_ptr(),
                                  count, dtype, peer, comm.handle, stream_handle))

    output_addresses = _h.VoidPtrVector([receive_buffer._hw_ptr()])

    global is_in_grouped_mode
    if is_in_grouped_mode:
        global recv_output_addresses_to_submit
        recv_output_addresses_to_submit.append(
            (stream_handle, output_addresses))
    else:
        _check_status(_h.hcclxSubmitEvents2(
            stream_handle, output_addresses))
        del output_addresses


def group_start():
    """ Start a group call.
        All subsequent calls to HCCL may not block due to inter-CPU synchronization.
    """
    _check_status(_h.hcclGroupStart())
    global is_in_grouped_mode
    is_in_grouped_mode = True


def group_end():
    """ End a group call.
        Will issue all collective operations issued since hcclGroupStart before returning.
        The function will not block until their completion.
    """
    _check_status(_h.hcclGroupEnd())

    global is_in_grouped_mode
    if is_in_grouped_mode:
        global recv_output_addresses_to_submit
        for stream_handle, output_addresses in recv_output_addresses_to_submit:
            _check_status(_h.hcclxSubmitEvents2(
                stream_handle, output_addresses))
        recv_output_addresses_to_submit.clear()
        is_in_grouped_mode = False

# -----------------------------------------------------------------------------
