/*******************************************************************************
 * Copyright (C) 2021 Habana Labs, Ltd. an Intel Company
 * All Rights Reserved.
 *
 * Unauthorized copying of this file or any element(s) within it, via any medium
 * is strictly prohibited.
 * This file contains Habana Labs, Ltd. proprietary and confidential information
 * and is subject to the confidentiality and license agreements under which it
 * was provided.
 *
 *******************************************************************************
 */
#pragma once

#include <tensorflow/core/framework/op_kernel.h>
#include <tensorflow/core/framework/tensor_shape.h>
#include <tensorflow/core/framework/types.pb.h>
#include <tensorflow/core/platform/status.h>

#include <string>
#include <vector>

namespace habana {
inline namespace v1 {
//! helper structure to represent metadata of tensorflow::Tensor
struct TensorInfo {
  tensorflow::DataType dtype;
  tensorflow::TensorShape shape;
};

//! helper structure to represent TPC kernel details
struct NodeDesc {
  //! Unique Identifier of TPC kernel
  std::string guid;
  //! pointer to the parameters data bound to the TPC kernel type
  void* user_params;
  //! size of parameters data bound to the TPC kernel type
  unsigned params_size;
  //! custom \b unique name of node - useful for debugging purposes. It can be left blank.
  std::string name;
};

/**
 * @brief Context containing all the necessary information to define TPC bound to HpuKernel.
 *
 * Within HpuKernelContext, user is responsible to define output information as well as define TPC kernel to be
 * invoked. If there is any error, while working with HpuKernelContext, SetStatus() method with error should be called,
 * and function should return.
 */
class HpuKernelContext {
 public:
  virtual ~HpuKernelContext() = default;

  /**
   * @brief Returns success status, if input for a given index exists.
   *
   * If successful, input_info is updated with information about input tensorflow::Tensor
   * connected to the HpuKernel at given index.
   */
  virtual tensorflow::Status InputInfo(int idx, TensorInfo& input_info) const = 0;

  /**
   * @brief Returns success status, if output for a given index exists.
   *
   * If successful, output_info is updated with information about output tensorflow::Tensor
   * connected to the HpuKernel at given index.
   * In order for this function to work, outputs must be populated with DefineOutputInfo().
   */
  virtual tensorflow::Status OutputInfo(int idx, TensorInfo& output_info) const = 0;

  /**
   * @brief Returns number of inputs of HpuKernel
   */
  virtual int NumInputs() const = 0;

  /**
   * @brief Returns number of outputs of HpuKernel
   */
  virtual int NumOutputs() const = 0;

  /**
   * @brief Returns valid pointer, if there is HostMemory tensorflow::Tensor at a given input index.
   *
   * In case of invalid index for HostMemory input, nullptr is returned.
   */
  virtual const tensorflow::Tensor* HostMemoryInput(int idx) const = 0;

  /**
   * @brief Returns NodeDef for a given OpKernel associated with HpuKernelContext
   */
  virtual const tensorflow::NodeDef& NodeDef() const = 0;

  /**
   * @brief Returns selected attribute of the Kernel.
   *
   * Function borrowed from OpKernelConstruction class.
   * If the T type does match the type found under attr_name, error status is returned.
   *
   * @param attr_name name of attribute in Op in TF Graph
   * @param value pointer to object to be filled with data.
   * @return status of the operation
   */
  template <class T>
  tensorflow::Status GetAttr(tensorflow::StringPiece attr_name, T* value) const {
    return GetNodeAttr(NodeDef(), attr_name, value);
  }

  /**
   * @brief Defines single output info within HpuKernelContext.
   *
   * Multiple calls with same index will result in error status returned
   *
   * @param idx output index. Should be less than NumOutputs()
   * @param info tensorflow::Tensor info for given output
   * @return status of the operation
   */
  virtual tensorflow::Status DefineOutputInfo(int idx, const TensorInfo& info) = 0;

  /**
   * @brief Defines single TPC kernel within HpuKernelContext.
   *
   * Multiple calls to this function will result in error status returned
   *
   * @param node_desc definition of TPC kernel
   * @param input_indices ordered indices of input TensorInfos
   *                      from HpuKernelContext that should be connected to TPC kernel
   * @param output_indices indices of output TensorInfos from HpuKernelContext
   *                       that should be connected to TPC kernel
   *                       Example: Op with 3 outputs (0, 1, 2), TPC with 3 outputs needed in different order (1, 0, 2)
   *                                This implies output_indices={1, 0, 2} (indices of OutputInfos in HpuKernelContex)
   *
   * In order to connect outputs to TPC kernel, DefineOutputInfo() must be called before for each output.
   *
   * @return status of the operation
   */
  virtual tensorflow::Status DefineNode(const NodeDesc& node_desc, const std::vector<int>& input_indices,
                                        const std::vector<int>& output_indices) = 0;

  /**
   * @brief Defines single TPC kernel within HpuKernelContext with in-place outputs definition.
   *
   * Multiple calls to this function will result in error status returned
   *
   * @param node_desc definition of TPC kernel
   * @param input_indices ordered indices of input TensorInfos
   *                      from HpuKernelContext that should be connected to TPC kernel
   * @param output_infos ordered list of output infos that should be connected to TPC kernel
   *                     Received output infos will automatically be added (in order) to HpuKernelContext.
   *
   * DefineOutputInfo() cannot be called before. If it was, this function will return error.
   *
   * @return status of the operation
   */
  virtual tensorflow::Status DefineNode(const NodeDesc& node_desc, const std::vector<int>& input_indices,
                                        const std::vector<TensorInfo>& output_infos) = 0;

  /**
   * @brief SetStatus() should be called, if HpuKernelContext encounters an error.
   *
   * Any method returning tensorflow::Status is not updating Status on HpuKernelContext.
   * It is caller's responsibility to do it.
   */
  virtual void SetStatus(const tensorflow::Status& status) = 0;

  //! Getter for current status of HpuKernelContext.
  virtual const tensorflow::Status& Status() const = 0;

  //! Helper routine for the OP_REQUIRES macros
  virtual void CtxFailure(const tensorflow::Status& s) = 0;
  //! Helper routine for the OP_REQUIRES macros
  virtual void CtxFailureWithWarning(const tensorflow::Status& s) = 0;
  //! Helper routine for the OP_REQUIRES macros
  virtual void CtxFailure(const char* file, int line, const tensorflow::Status& s) = 0;
  //! Helper routine for the OP_REQUIRES macros
  virtual void CtxFailureWithWarning(const char* file, int line, const tensorflow::Status& s) = 0;

  //! Getter for pointer to tensorflow::OpKernelContext. Use rarely.
  virtual const tensorflow::OpKernelContext* OpKernelContext() const = 0;
};

}  // namespace v1
}  // namespace habana

/**
 * @brief Helper function to make HpuKernelContext with TF macros.
 *
 * HpuKernels do not support ComputeAsync. Implementing empty CheckNotInComputeAsync
 * allows user to use macros defined in tensorflow/core/framework/op_requires.h:
 * OP_REQUIRES(...) and OP_REQUIRES_OK(...)
 *
 */
inline void CheckNotInComputeAsync(habana::HpuKernelContext*, const char*) {}
