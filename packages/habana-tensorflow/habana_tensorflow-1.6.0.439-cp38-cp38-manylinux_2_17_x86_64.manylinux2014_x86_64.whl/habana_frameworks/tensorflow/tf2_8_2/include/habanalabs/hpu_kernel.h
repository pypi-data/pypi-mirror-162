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

#include <memory>

#include <tensorflow/core/framework/op_kernel.h>
#include <tensorflow/core/framework/kernel_def_builder.h>

#include "hpu_kernel_context.h"

namespace habana {
inline namespace v1 {
class BaseFunctor;
class HpuKernelImpl;

/**
 * @brief Base class for HpuKernel, that implements Compute(). Do not inherit from it.
 */
class HpuBaseKernel : public tensorflow::OpKernel {
 public:
  //! C'tor
  explicit HpuBaseKernel(tensorflow::OpKernelConstruction* context);
  //! D'tor
  ~HpuBaseKernel() override;
  //! Final impl of tensorflow::OpKernel::Compute() method
  virtual void Compute(tensorflow::OpKernelContext* context) override final;
  //! Getter for child Functor @see HpuKernel
  virtual BaseFunctor& GetFunctor() = 0;
  //! Getter for Impl
  virtual HpuKernelImpl* Pimpl() { return pImpl_.get(); }

 private:
  std::unique_ptr<HpuKernelImpl> pImpl_;
};

/**
 * @brief Final class for all HpuKernels.
 *
 * In order to register new kernel, BaseFunctor needs to be implemented, i.e. HpuKernel<SomeFunctor>.
 */
template <class Functor>
class HpuKernel final : public HpuBaseKernel {
 public:
  static_assert(std::is_base_of<BaseFunctor, Functor>::value, "Functor must inherit from BaseFunctor");
  using HpuBaseKernel::HpuBaseKernel;
  //! Getter for Functor - core part of any HpuKernel
  BaseFunctor& GetFunctor() override { return functor_; }

 private:
  Functor functor_;
};

/**
 * @brief Base class for specialized functors, to be used with HpuKernel.
 */
class BaseFunctor {
 public:
  /**
   * @brief This function is responsible for defining outputs and TPC kernel on HpuKernelContext object.
   */
  virtual void DefineNode(HpuKernelContext* context) = 0;
};

}  // namespace v1
}  // namespace habana

namespace tensorflow {
namespace register_kernel {
inline namespace v1 {
/**
 * @brief KernelDefBuilder class that should be used to register HpuKernels.
 *
 * It resides in tensorflow::register_kernel namespace to be compatible
 * with macro REGISTER_KERNEL_BUILDER from tensorflow/core/framework/op_kernel.h.
 *
 * Example:
 *  REGISTER_KERNEL_BUILDER(ForHpuWithName("CustomOp").TypeConstraint<float>("T"),
 *                          habana::HpuKernel<CustomFunctor<float>>);
 *
 * It provides following functionalities:
 *  - KernelDefBuilder Device is set to HPU
 *  - automatic clustering
 */
class ForHpuWithName : public tensorflow::KernelDefBuilder {
 public:
  //! C'tor
  explicit ForHpuWithName(const char* op);
};
}  // namespace v1
}  // namespace register_kernel

#define TF_EXTRACT_KERNEL_NAME_ForHpuWithName(name_str) \
  name_str, ::tensorflow::register_kernel::ForHpuWithName(name_str)

}  // namespace tensorflow
