/*
 * Copyright 2021 NVIDIA CORPORATION & AFFILIATES.  All rights reserved.
 *
 * NOTICE TO LICENSEE:
 *
 * This source code and/or documentation ("Licensed Deliverables") are
 * subject to NVIDIA intellectual property rights under U.S. and
 * international Copyright laws.
 *
 * These Licensed Deliverables contained herein is PROPRIETARY and
 * CONFIDENTIAL to NVIDIA and is being provided under the terms and
 * conditions of a form of NVIDIA software license agreement by and
 * between NVIDIA and Licensee ("License Agreement") or electronically
 * accepted by Licensee.  Notwithstanding any terms or conditions to
 * the contrary in the License Agreement, reproduction or disclosure
 * of the Licensed Deliverables to any third party without the express
 * written consent of NVIDIA is prohibited.
 *
 * NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
 * LICENSE AGREEMENT, NVIDIA MAKES NO REPRESENTATION ABOUT THE
 * SUITABILITY OF THESE LICENSED DELIVERABLES FOR ANY PURPOSE.  IT IS
 * PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF ANY KIND.
 * NVIDIA DISCLAIMS ALL WARRANTIES WITH REGARD TO THESE LICENSED
 * DELIVERABLES, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY,
 * NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
 * NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
 * LICENSE AGREEMENT, IN NO EVENT SHALL NVIDIA BE LIABLE FOR ANY
 * SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, OR ANY
 * DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
 * WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
 * ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
 * OF THESE LICENSED DELIVERABLES.
 *
 * U.S. Government End Users.  These Licensed Deliverables are a
 * "commercial item" as that term is defined at 48 C.F.R. 2.101 (OCT
 * 1995), consisting of "commercial computer software" and "commercial
 * computer software documentation" as such terms are used in 48
 * C.F.R. 12.212 (SEPT 1995) and is provided to the U.S. Government
 * only as a commercial end item.  Consistent with 48 C.F.R.12.212 and
 * 48 C.F.R. 227.7202-1 through 227.7202-4 (JUNE 1995), all
 * U.S. Government End Users acquire the Licensed Deliverables with
 * only those rights set forth herein.
 *
 * Any use of the Licensed Deliverables in individual and commercial
 * software must include, in the user documentation and internal
 * comments to the code, the above Disclaimer and U.S. Government End
 * Users Notice.
 * </blockquote>}
 */


/**
 * @file
 * @brief This file contains all public function declarations of the cuTensorNet
 * library.
 */
#pragma once

#define CUTENSORNET_MAJOR 1 //!< cuTensorNet major version.
#define CUTENSORNET_MINOR 1 //!< cuTensorNet minor version.
#define CUTENSORNET_PATCH 1 //!< cuTensorNet patch version.
#define CUTENSORNET_VERSION (CUTENSORNET_MAJOR * 10000 + CUTENSORNET_MINOR * 100 + CUTENSORNET_PATCH)

#include <cutensornet/types.h>

#if defined(__cplusplus)
#include <cstdint>
#include <cstdio>

extern "C" {
#else
#include <stdint.h>
#include <stdio.h>

#endif /* __cplusplus */

#if defined(__GNUC__)
    #define CUTENSORNET_DEPRECATED(new_func)     __attribute__((deprecated("please use " #new_func " instead")))
#else
    #define CUTENSORNET_DEPRECATED(new_func)
#endif

/**
 * \brief Initializes the cuTensorNet library
 *
 * \details The device associated with a particular cuTensorNet handle is assumed to remain
 * unchanged after the cutensornetCreate() call. In order for the cuTensorNet library to 
 * use a different device, the application must set the new device to be used by
 * calling cudaSetDevice() and then create another cuTensorNet handle, which will
 * be associated with the new device, by calling cutensornetCreate().
 *
 * \param[out] handle Pointer to ::cutensornetHandle_t
 *
 * \returns ::CUTENSORNET_STATUS_SUCCESS on success and an error code otherwise
 * \remarks blocking, no reentrant, and thread-safe
 */
cutensornetStatus_t cutensornetCreate(cutensornetHandle_t* handle);

/**
 * \brief Destroys the cuTensorNet library handle
 *
 * \details This function releases resources used by the cuTensorNet library handle. This function is the last call with a particular handle to the cuTensorNet library.
 * Calling any cuTensorNet function which uses ::cutensornetHandle_t after cutensornetDestroy() will return an error.
 *
 * \param[in,out] handle Opaque handle holding cuTensorNet's library context.
 */
cutensornetStatus_t cutensornetDestroy(cutensornetHandle_t handle);

/**
 * \mainpage cuTensorNet: A high-level CUDA library that is dedicated to operations on tensor networks (i.e., a collection of tensors) 
 */

/**
 * \brief Initializes a ::cutensornetNetworkDescriptor_t, describing the connectivity (i.e., network topology) between the tensors.
 *
 * Note that this function allocates data on the heap; hence, it is critical that cutensornetDestroyNetworkDescriptor() is called once \p descNet is no longer required.
 * 
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] numInputs Number of input tensors.
 * \param[in] numModesIn Array of size \p numInputs; ``numModesIn[i]`` denotes the number of modes available in the i-th tensor.
 * \param[in] extentsIn Array of size \p numInputs; ``extentsIn[i]`` has ``numModesIn[i]`` many entries with ``extentsIn[i][j]`` (``j`` < ``numModesIn[i]``) corresponding to the extent of the j-th mode of tensor ``i``.
 * \param[in] stridesIn Array of size \p numInputs; ``stridesIn[i]`` has ``numModesIn[i]`` many entries with ``stridesIn[i][j]`` (``j`` < ``numModesIn[i]``) corresponding to the linearized offset -- in physical memory -- between two logically-neighboring elements w.r.t the j-th mode of tensor ``i``.
 * \param[in] modesIn Array of size \p numInputs; ``modesIn[i]`` has ``numModesIn[i]`` many entries -- each entry corresponds to a mode. Each mode that does not appear in the input tensor is implicitly contracted.
 * \param[in] alignmentRequirementsIn Array of size \p numInputs; ``alignmentRequirementsIn[i]`` denotes the (minimal) alignment (in bytes) for the data pointer that corresponds to the i-th tensor (see ``rawDataIn[i]`` of cutensornetContraction()). It is recommended that each pointer is aligned to a 256-byte boundary.
 * \param[in] numModesOut number of modes of the output tensor. On entry, if this value is ``-1`` and the output modes are not provided, the network will infer the output modes. If this value is ``0``, the network is force reduced.
 * \param[in] extentsOut Array of size \p numModesOut; ``extentsOut[j]`` (``j`` < ``numModesOut``) corresponding to the extent of the j-th mode of the output tensor.
 * \param[in] stridesOut Array of size \p numModesOut; ``stridesOut[j]`` (``j`` < ``numModesOut``) corresponding to the linearized offset -- in physical memory -- between two logically-neighboring elements w.r.t the j-th mode of the output tensor.
 * \param[in] modesOut Array of size \p numModesOut; ``modesOut[j]`` denotes the j-th mode of the output tensor.
 * \param[in] alignmentRequirementsOut Denotes the (minimal) alignment (in bytes) for the data pointer that corresponds to the output tensor (see \p rawDataOut of cutensornetContraction()). It's recommended that each pointer is aligned to a 256-byte boundary.
 * output tensor.
 * \param[in] dataType Denotes the data type for all input an output tensors.
 * \param[in] computeType Denotes the compute type used throughout the computation.
 * \param[out] descNet Pointer to a ::cutensornetNetworkDescriptor_t.
 *
 * \note If \p stridesIn (\p stridesOut) is set to 0 (\p NULL), it means the input tensors (output tensor) are in the Fortran (column-major) layout.
 * \note \p numModesOut can be set to ``-1`` for cuTensorNet to infer the output modes based on the input modes, or to ``0`` to perform a full reduction.
 *
 * Supported data-type combinations are:
 *
 * \verbatim embed:rst:leading-asterisk
 * +-------------+--------------------------+-------------+
 * |  Data type  |       Compute type       | Tensor Core |
 * +=============+==========================+=============+
 * | CUDA_R_16F  | CUTENSORNET_COMPUTE_32F  |   Volta+    |
 * +-------------+--------------------------+-------------+
 * | CUDA_R_16BF | CUTENSORNET_COMPUTE_32F  |   Ampere+   |
 * +-------------+--------------------------+-------------+
 * | CUDA_R_32F  | CUTENSORNET_COMPUTE_32F  |   No        |
 * +-------------+--------------------------+-------------+
 * | CUDA_R_32F  | CUTENSORNET_COMPUTE_TF32 |   Ampere+   |
 * +-------------+--------------------------+-------------+
 * | CUDA_R_32F  | CUTENSORNET_COMPUTE_16BF |   Ampere+   |
 * +-------------+--------------------------+-------------+
 * | CUDA_R_32F  | CUTENSORNET_COMPUTE_16F  |   Volta+    |
 * +-------------+--------------------------+-------------+
 * | CUDA_R_64F  | CUTENSORNET_COMPUTE_64F  |   Ampere+   |
 * +-------------+--------------------------+-------------+
 * | CUDA_R_64F  | CUTENSORNET_COMPUTE_32F  |   No        |
 * +-------------+--------------------------+-------------+
 * | CUDA_C_32F  | CUTENSORNET_COMPUTE_32F  |   No        |
 * +-------------+--------------------------+-------------+
 * | CUDA_C_32F  | CUTENSORNET_COMPUTE_TF32 |   Ampere+   |
 * +-------------+--------------------------+-------------+
 * | CUDA_C_64F  | CUTENSORNET_COMPUTE_64F  |   Ampere+   |
 * +-------------+--------------------------+-------------+
 * | CUDA_C_64F  | CUTENSORNET_COMPUTE_32F  |   No        |
 * +-------------+--------------------------+-------------+
 * \endverbatim

 */
cutensornetStatus_t cutensornetCreateNetworkDescriptor(const cutensornetHandle_t handle,
                                                  int32_t numInputs,
                                                  const int32_t numModesIn[],
                                                  const int64_t* const extentsIn[],
                                                  const int64_t* const stridesIn[],
                                                  const int32_t* const modesIn[],
                                                  const uint32_t alignmentRequirementsIn[],
                                                  int32_t numModesOut,
                                                  const int64_t extentsOut[],
                                                  const int64_t stridesOut[],
                                                  const int32_t modesOut[],
                                                  uint32_t alignmentRequirementsOut,
                                                  cudaDataType_t dataType,
                                                  cutensornetComputeType_t computeType,
                                                  cutensornetNetworkDescriptor_t* descNet);

/**
 * \brief Frees all the memory associated with the network descriptor.
 *
 * \param[in,out] desc Opaque handle to a tensor network descriptor.
 */
cutensornetStatus_t cutensornetDestroyNetworkDescriptor(cutensornetNetworkDescriptor_t desc);

/**
 * \brief Gets the number of output modes, data size, modes, extents, and strides of the output tensor.
 *
 * If all information regarding the output tensor is needed by the user, this function should be called twice
 * (the first time to retrieve \p numModesOut for allocating memory, and the second to retrieve \p modesOut, \p extentsOut, and \p stridesOut).
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] descNet Pointer to a ::cutensornetNetworkDescriptor_t.
 * \param[out] numModesOut on return, holds the number of modes of the output tensor. Cannot be null.
 * \param[out] dataSizeOut if not null on return, holds the size (in bytes) of the memory needed for the output tensor. Optionally, can be null.
 * \param[out] modeLabelsOut if not null on return, holds the modes of the output tensor. Optionally, can be null.
 * \param[out] extentsOut if not null on return, holds the extents of the output tensor. Optionally, can be null.
 * \param[out] stridesOut if not null on return, holds the strides of the output tensor. Optionally, can be null.
 */
cutensornetStatus_t cutensornetGetOutputTensorDetails(const cutensornetHandle_t handle,
                                                      const cutensornetNetworkDescriptor_t descNet,
                                                      int32_t* numModesOut,
                                                      size_t*  dataSizeOut,
                                                      int32_t* modeLabelsOut,
                                                      int64_t* extentsOut,
                                                      int64_t* stridesOut);

/**
 * \brief Creates a workspace descriptor that holds information about the user provided memory buffer.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[out] workDesc Pointer to the opaque workspace descriptor.
 */
cutensornetStatus_t cutensornetCreateWorkspaceDescriptor(const cutensornetHandle_t handle,
                                                         cutensornetWorkspaceDescriptor_t *workDesc);

/**
 * \brief Computes the workspace size needed to contract the input tensor network using the provided contraction path.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] descNet Describes the tensor network (i.e., its tensors and their connectivity).
 * \param[in] optimizerInfo Opaque structure.
 * \param[out] workDesc The workspace descriptor in which the information is collected.
 */
cutensornetStatus_t cutensornetWorkspaceComputeSizes(const cutensornetHandle_t handle,
                                                     const cutensornetNetworkDescriptor_t descNet,
                                                     const cutensornetContractionOptimizerInfo_t optimizerInfo,
                                                     cutensornetWorkspaceDescriptor_t workDesc);

/**
 * \brief Retrieves the needed workspace size for the given workspace preference and memory space.
 * 
 * The needed sizes must be pre-calculated by calling cutensornetWorkspaceComputeSizes().
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] workDesc Opaque structure describing the workspace.
 * \param[in] workPref Preference of workspace for planning.
 * \param[in] memSpace The memory space where the workspace is allocated.
 * \param[out] workspaceSize Needed workspace size.
 */
cutensornetStatus_t cutensornetWorkspaceGetSize(const cutensornetHandle_t handle,
                                                const cutensornetWorkspaceDescriptor_t workDesc,
                                                cutensornetWorksizePref_t workPref,
                                                cutensornetMemspace_t memSpace,
                                                uint64_t* workspaceSize);

/**
 * \brief Sets the memory address and workspace size of workspace provided by user.
 *
 * A workspace is valid in the following cases:
 *
 *   - \p workspacePtr is valid and \p workspaceSize > 0 
 *   - \p workspacePtr is null and \p workspaceSize > 0 (used during cutensornetCreateContractionPlan() to provide the available workspace).
 *   - \p workspacePtr is null and \p workspaceSize = 0 (workspace memory will be drawn from the user's mempool)
 *
 * A workspace will be validated against the minimal required at usage (cutensornetCreateContractionPlan(), cutensornetContractionAutotune(), cutensornetContraction())
 * 
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in,out] workDesc Opaque structure describing the workspace.
 * \param[in] memSpace The memory space where the workspace is allocated.
 * \param[in] workspacePtr Workspace memory pointer, may be null.
 * \param[in] workspaceSize Workspace size, must be >= 0.
 */
cutensornetStatus_t cutensornetWorkspaceSet(const cutensornetHandle_t handle,
                                            cutensornetWorkspaceDescriptor_t workDesc,
                                            cutensornetMemspace_t memSpace,
                                            void* const workspacePtr,
                                            uint64_t workspaceSize);

/**
 * \brief Retrieves the memory address and workspace size of workspace hosted in the workspace descriptor.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] workDesc Opaque structure describing the workspace.
 * \param[in] memSpace The memory space where the workspace is allocated.
 * \param[out] workspacePtr Workspace memory pointer.
 * \param[out] workspaceSize Workspace size.
 */
cutensornetStatus_t cutensornetWorkspaceGet(const cutensornetHandle_t handle,
                                            const cutensornetWorkspaceDescriptor_t workDesc,
                                            cutensornetMemspace_t memSpace,
                                            void** workspacePtr,
                                            uint64_t* workspaceSize);

/**
 * \brief Frees the workspace descriptor.
 * 
 * Note that this API does not free the memory provided by cutensornetWorkspaceSet().
 *
 * \param[in,out] desc Opaque structure.
 */
cutensornetStatus_t cutensornetDestroyWorkspaceDescriptor( cutensornetWorkspaceDescriptor_t desc );

/**
 * \brief Sets up the required hyper-optimization parameters for the contraction order solver (see cutensornetContractionOptimize())
 * 
 * Note that this function allocates data on the heap; hence, it is critical that cutensornetDestroyContractionOptimizerConfig() is called once \p optimizerConfig is no longer required.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[out] optimizerConfig This data structure holds all information about the user-requested hyper-optimization parameters.
 */
cutensornetStatus_t cutensornetCreateContractionOptimizerConfig(const cutensornetHandle_t handle,
                                                cutensornetContractionOptimizerConfig_t* optimizerConfig);

/**
 * \brief Frees all the memory associated with \p optimizerConfig.
 *
 * \param[in,out] optimizerConfig Opaque structure.
 */
cutensornetStatus_t cutensornetDestroyContractionOptimizerConfig(cutensornetContractionOptimizerConfig_t optimizerConfig);

/**
 * \brief Gets attributes of \p optimizerConfig.
 *
 * \param[in] handle Opaque handle holding cuTENSORNet's library context.
 * \param[in] optimizerConfig Opaque structure that is accessed.
 * \param[in] attr Specifies the attribute that is requested.
 * \param[out] buf On return, this buffer (of size \p sizeInBytes) holds the value that corresponds to \p attr within \p optimizerConfig.
 * \param[in] sizeInBytes Size of \p buf (in bytes).
 */
cutensornetStatus_t cutensornetContractionOptimizerConfigGetAttribute(const cutensornetHandle_t handle,
                                                cutensornetContractionOptimizerConfig_t optimizerConfig,
                                                cutensornetContractionOptimizerConfigAttributes_t attr,
                                                void *buf,
                                                size_t sizeInBytes);
/**
 * \brief Sets attributes of \p optimizerConfig.
 *
 * \param[in] handle Opaque handle holding cuTENSORNet's library context.
 * \param[in] optimizerConfig Opaque structure that is accessed.
 * \param[in] attr Specifies the attribute that is requested.
 * \param[in] buf This buffer (of size \p sizeInBytes) determines the value to which \p attr will be set.
 * \param[in] sizeInBytes Size of \p buf (in bytes).
 */
cutensornetStatus_t cutensornetContractionOptimizerConfigSetAttribute(const cutensornetHandle_t handle,
                                                cutensornetContractionOptimizerConfig_t optimizerConfig,
                                                cutensornetContractionOptimizerConfigAttributes_t attr,
                                                const void *buf,
                                                size_t sizeInBytes);

/**
 * \brief Frees all the memory associated with \p optimizerInfo
 *
 * \param[in,out] optimizerInfo Opaque structure.
 */
cutensornetStatus_t cutensornetDestroyContractionOptimizerInfo(cutensornetContractionOptimizerInfo_t optimizerInfo);

/**
 * \brief Allocates resources for \p optimizerInfo.
 *
 * Note that this function allocates data on the heap; hence, it is critical that cutensornetDestroyContractionOptimizerInfo() is called once \p optimizerInfo is no longer required.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] descNet Describes the tensor network (i.e., its tensors and their connectivity) for which \p optimizerInfo is created.
 * \param[out] optimizerInfo Pointer to ::cutensornetContractionOptimizerInfo_t.
 */
cutensornetStatus_t cutensornetCreateContractionOptimizerInfo(const cutensornetHandle_t handle,
                                             const cutensornetNetworkDescriptor_t descNet,
                                             cutensornetContractionOptimizerInfo_t *optimizerInfo);

/**
 * \brief Computes an "optimized" contraction order as well as slicing info (for more information see Overview section) for a given tensor network such that the total time to solution is minimized while adhering to the user-provided memory constraint.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] descNet Describes the topology of the tensor network (i.e., all tensors, their connectivity and modes).
 * \param[in] optimizerConfig Holds all hyper-optimization parameters that govern the search for an "optimal" contraction order.
 * \param[in] workspaceSizeConstraint Maximal device memory that will be provided by the user (i.e., cuTensorNet has to find a viable path/slicing solution within this user-defined constraint).
 * \param[in,out] optimizerInfo On return, this object will hold all necessary information about the optimized path and the related slicing information. \p optimizerInfo will hold information including (see ::cutensornetContractionOptimizerInfoAttributes_t):
 *      - Total number of slices.
 *      - Total number of sliced modes.
 *      - Information about the sliced modes (i.e., the IDs of the sliced modes (see \p modesIn w.r.t. cutensornetCreateNetworkDescriptor()) as well as their extents (see Overview section for additional documentation).
 *      - Optimized path.
 *      - FLOP count.
 *      - Total number of elements in the largest intermediate tensor.
 *      - The mode labels for all intermediate tensors.
 *      - The estimated runtime and "effective" flops.
 */
cutensornetStatus_t cutensornetContractionOptimize(const cutensornetHandle_t handle,
                                             const cutensornetNetworkDescriptor_t descNet,
                                             const cutensornetContractionOptimizerConfig_t optimizerConfig,
                                             uint64_t workspaceSizeConstraint,
                                             cutensornetContractionOptimizerInfo_t optimizerInfo);

/**
 * \brief Gets attributes of \p optimizerInfo.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] optimizerInfo Opaque structure that is accessed.
 * \param[in] attr Specifies the attribute that is requested.
 * \param[out] buf On return, this buffer (of size \p sizeInBytes) holds the value that corresponds to \p attr within \p optimizeInfo.
 * \param[in] sizeInBytes Size of \p buf (in bytes).
 */
cutensornetStatus_t cutensornetContractionOptimizerInfoGetAttribute(
        const cutensornetHandle_t handle,
        const cutensornetContractionOptimizerInfo_t optimizerInfo,
        cutensornetContractionOptimizerInfoAttributes_t attr,
        void *buf,
        size_t sizeInBytes);

/**
 * \brief Sets attributes of optimizerInfo.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] optimizerInfo Opaque structure that is accessed.
 * \param[in] attr Specifies the attribute that is requested.
 * \param[in] buf This buffer (of size \p sizeInBytes) determines the value to which \p attr will be set.
 * \param[in] sizeInBytes Size of \p buf (in bytes).
 */
cutensornetStatus_t cutensornetContractionOptimizerInfoSetAttribute(
        const cutensornetHandle_t handle,
        cutensornetContractionOptimizerInfo_t optimizerInfo,
        cutensornetContractionOptimizerInfoAttributes_t attr,
        const void *buf,
        size_t sizeInBytes);

/**
 * \brief Gets the packed size of the \p optimizerInfo object.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] optimizerInfo Opaque structure of type cutensornetContractionOptimizerInfo_t.
 * \param[out] sizeInBytes The packed size (in bytes).
 */
cutensornetStatus_t cutensornetContractionOptimizerInfoGetPackedSize(
        const cutensornetHandle_t handle,
        const cutensornetContractionOptimizerInfo_t optimizerInfo,
        size_t *sizeInBytes);

/**
 * \brief Packs the \p optimizerInfo object into the provided buffer.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] optimizerInfo Opaque structure of type cutensornetContractionOptimizerInfo_t.
 * \param[out] buffer On return, this buffer holds the contents of optimizerInfo in packed form.
 * \param[in] sizeInBytes The size of the buffer (in bytes).
 */
cutensornetStatus_t cutensornetContractionOptimizerInfoPackData(
        const cutensornetHandle_t handle,
        const cutensornetContractionOptimizerInfo_t optimizerInfo,
        void *buffer,
        size_t sizeInBytes);

/**
 * \brief Create an optimizerInfo object from the provided buffer.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] descNet Describes the tensor network (i.e., its tensors and their connectivity) for which \p optimizerInfo is created.
 * \param[in] buffer A buffer with the contents of optimizerInfo in packed form.
 * \param[in] sizeInBytes The size of the buffer (in bytes).
 * \param[out] optimizerInfo Pointer to ::cutensornetContractionOptimizerInfo_t.
 */
cutensornetStatus_t cutensornetCreateContractionOptimizerInfoFromPackedData(
        const cutensornetHandle_t handle,
        const cutensornetNetworkDescriptor_t descNet,
        const void *buffer,
        size_t sizeInBytes,
        cutensornetContractionOptimizerInfo_t *optimizerInfo);

/**
 * \brief Update the provided \p optimizerInfo object from the provided buffer.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] buffer A buffer with the contents of optimizerInfo in packed form.
 * \param[in] sizeInBytes The size of the buffer (in bytes).
 * \param[in,out] optimizerInfo Opaque object of type ::cutensornetContractionOptimizerInfo_t that will be updated.
 */
cutensornetStatus_t cutensornetUpdateContractionOptimizerInfoFromPackedData(
                                         const cutensornetHandle_t handle,
                                         const void *buffer,
                                         size_t sizeInBytes,
                                         cutensornetContractionOptimizerInfo_t optimizerInfo);
/**
 * \brief Initializes a ::cutensornetContractionPlan_t.
 *
 * Note that this function allocates data on the heap; hence, it is critical that cutensornetDestroyContractionPlan() is called once \p plan is no longer required.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] descNet Describes the tensor network (i.e., its tensors and their connectivity).
 * \param[in] optimizerInfo Opaque structure.
 * \param[in] workDesc Opaque structure describing the workspace. At the creation of the contraction plan, only the workspace size is needed; the pointer to the workspace memory may be left null. 
 * If a device memory handler is set, \p workDesc can be set either to null (in which case the "recommended" workspace size is inferred, see ::CUTENSORNET_WORKSIZE_PREF_RECOMMENDED) or to a valid ::cutensornetWorkspaceDescriptor_t with the desired workspace size set and a null workspace pointer, see Memory Management API section.
 * \param[out] plan cuTensorNet's contraction plan holds all the information required to perform
 * the tensor contractions; to be precise, it initializes a \p cutensorContractionPlan_t for
 * each tensor contraction that is required to contract the entire tensor network.
*/
cutensornetStatus_t cutensornetCreateContractionPlan(const cutensornetHandle_t handle,
                                                     const cutensornetNetworkDescriptor_t descNet,
                                                     const cutensornetContractionOptimizerInfo_t optimizerInfo,
                                                     const cutensornetWorkspaceDescriptor_t workDesc,
                                                     cutensornetContractionPlan_t* plan);

/**
 * \brief Frees all resources owned by \p plan.
 *
 * \param[in,out] plan Opaque structure.
 */
cutensornetStatus_t cutensornetDestroyContractionPlan(cutensornetContractionPlan_t plan);

/**
 * \brief Auto-tunes the contraction plan to find the best \p cutensorContractionPlan_t for each pair-wise contraction.
 *
 * \note This function is blocking due to the nature of the auto-tuning process.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in,out] plan The plan must already be created (see cutensornetCreateContractionPlan()); the individual contraction plans will be fine-tuned.
 * \param[in] rawDataIn Array of N pointers (N being the number of input tensors specified cutensornetCreateNetworkDescriptor()); ``rawDataIn[i]`` points to the data associated with the i-th input tensor (in device memory).
 * \param[out] rawDataOut Points to the raw data of the output tensor (in device memory).
 * \param[in] workDesc Opaque structure describing the workspace. The provided workspace must be \em valid (the workspace size must be the same as or larger than both the minimum needed and the value provided at plan creation). See cutensornetCreateContractionPlan(), cutensornetWorkspaceGetSize() & cutensornetWorkspaceSet(). 
 * If a device memory handler is set, the \p workDesc can be set to null, or the workspace pointer in \p workDesc can be set to null, and the workspace size can be set either to 0 (in which case the "recommended" size is used, see ::CUTENSORNET_WORKSIZE_PREF_RECOMMENDED) or to a \em valid size. A workspace of the specified size will be drawn from the user's mempool and released back once done.
 * \param[in] pref Controls the auto-tuning process and gives the user control over how much time is spent in this routine.
 * \param[in] stream The CUDA stream on which the computation is performed.
 */
cutensornetStatus_t cutensornetContractionAutotune(const cutensornetHandle_t handle,
                                                   cutensornetContractionPlan_t plan,
                                                   const void* const rawDataIn[],
                                                   void* rawDataOut,
                                                   const cutensornetWorkspaceDescriptor_t workDesc,
                                                   const cutensornetContractionAutotunePreference_t pref,
                                                   cudaStream_t stream);

/**
 * \brief Sets up the required auto-tune parameters for the contraction plan
 * 
 * Note that this function allocates data on the heap; hence, it is critical that cutensornetDestroyContractionAutotunePreference() is called once \p autotunePreference is no longer required.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[out] autotunePreference This data structure holds all information about the user-requested auto-tune parameters.
 */
cutensornetStatus_t cutensornetCreateContractionAutotunePreference(const cutensornetHandle_t handle,
                                                cutensornetContractionAutotunePreference_t* autotunePreference);

/**
 * \brief Gets attributes of \p autotunePreference.
 *
 * \param[in] handle Opaque handle holding cuTENSORNet's library context.
 * \param[in] autotunePreference Opaque structure that is accessed.
 * \param[in] attr Specifies the attribute that is requested.
 * \param[out] buf On return, this buffer (of size \p sizeInBytes) holds the value that corresponds to \p attr within \p autotunePreference.
 * \param[in] sizeInBytes Size of \p buf (in bytes).
 */
cutensornetStatus_t cutensornetContractionAutotunePreferenceGetAttribute(const cutensornetHandle_t handle,
                                                cutensornetContractionAutotunePreference_t autotunePreference,
                                                cutensornetContractionAutotunePreferenceAttributes_t attr,
                                                void *buf,
                                                size_t sizeInBytes);
/**
 * \brief Sets attributes of \p autotunePreference.
 *
 * \param[in] handle Opaque handle holding cuTENSORNet's library context.
 * \param[in] autotunePreference Opaque structure that is accessed.
 * \param[in] attr Specifies the attribute that is requested.
 * \param[in] buf This buffer (of size \p sizeInBytes) determines the value to which \p attr will be set.
 * \param[in] sizeInBytes Size of \p buf (in bytes).
 */
cutensornetStatus_t cutensornetContractionAutotunePreferenceSetAttribute(const cutensornetHandle_t handle,
                                                cutensornetContractionAutotunePreference_t autotunePreference,
                                                cutensornetContractionAutotunePreferenceAttributes_t attr,
                                                const void *buf,
                                                size_t sizeInBytes);

/**
 * \brief Frees all the memory associated with \p autotunePreference
 *
 * \param[in,out] autotunePreference Opaque structure.
 */
cutensornetStatus_t cutensornetDestroyContractionAutotunePreference(cutensornetContractionAutotunePreference_t autotunePreference);

/**
 * \brief DEPRECATED: Performs the actual contraction of the tensor network.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] plan Encodes the execution of a tensor network contraction (see cutensornetCreateContractionPlan() and cutensornetContractionAutotune()).
 * \param[in] rawDataIn Array of N pointers (N being the number of input tensors specified cutensornetCreateNetworkDescriptor()); ``rawDataIn[i]`` points to the data associated with the i-th input tensor (in device memory).
 * \param[out] rawDataOut Points to the raw data of the output tensor (in device memory).
 * \param[in] workDesc Opaque structure describing the workspace. The provided workspace must be \em valid (the workspace size must be the same as or larger than both the minimum needed and the value provided at plan creation). See cutensornetCreateContractionPlan(), cutensornetWorkspaceGetSize() & cutensornetWorkspaceSet()). 
 * If a device memory handler is set, then \p workDesc can be set to null, or the workspace pointer in \p workDesc can be set to null, and the workspace size can be set either to 0 (in which case the "recommended" size is used, see ::CUTENSORNET_WORKSIZE_PREF_RECOMMENDED) or to a \em valid size. A workspace of the specified size will be drawn from the user's mempool and released back once done.
 * \param[in] sliceId The ID of the slice that is currently contracted (this value ranges between ``0`` and ``optimizerInfo.numSlices``); use ``0`` if no slices are used.
 * \param[in] stream The CUDA stream on which the computation is performed.
 *
 * \note If multiple slices are created, the order of contracting over slices using cutensornetContraction() should be ascending
 * starting from slice 0. If parallelizing over slices manually (in any fashion: streams, devices, processes, etc.), please make
 * sure the output tensors (that are subject to a global reduction) are zero-initialized.
 *
 * \note This function is asynchronous w.r.t. the calling CPU thread. The user should guarantee that the memory buffer provided in \p workDesc is valid until a synchronization with the stream or the device is executed.
 */
CUTENSORNET_DEPRECATED(cutensornetContractSlices)
cutensornetStatus_t cutensornetContraction(const cutensornetHandle_t handle,
                                           const cutensornetContractionPlan_t plan,
                                           const void* const rawDataIn[],
                                           void* rawDataOut,
                                           const cutensornetWorkspaceDescriptor_t workDesc,
                                           int64_t sliceId,
                                           cudaStream_t stream);

/**
 * \brief Create a `cutensornetSliceGroup_t` object from a range, which produces a sequence of slice IDs from the specified start (inclusive) to the specified stop (exclusive) values with the specified step. The sequence can be increasing or decreasing depending on the start and stop values.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] sliceIdStart The start slice ID.
 * \param[in] sliceIdStop The final slice ID is the largest (smallest) integer that excludes this value and all those above (below) for an increasing (decreasing) sequence.
 * \param[in] sliceIdStep The step size between two successive slice IDs. A negative step size should be specified for a decreasing sequence.
 * \param[out] sliceGroup Opaque object specifying the slice IDs.
 */
cutensornetStatus_t cutensornetCreateSliceGroupFromIDRange(const cutensornetHandle_t handle,
                                                           int64_t sliceIdStart,
                                                           int64_t sliceIdStop,
                                                           int64_t sliceIdStep,
                                                           cutensornetSliceGroup_t *sliceGroup);
/**
 * \brief Create a `cutensornetSliceGroup_t` object from a sequence of slice IDs. Duplicates in the input slice ID sequence will be removed.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] beginIDSequence A pointer to the beginning of the slice ID sequence.
 * \param[in] endIDSequence A pointer to the end of the slice ID sequence.
 * \param[out] sliceGroup Opaque object specifying the slice IDs.
 */
cutensornetStatus_t cutensornetCreateSliceGroupFromIDs(const cutensornetHandle_t handle,
                                                       const int64_t *beginIDSequence,
                                                       const int64_t *endIDSequence,
                                                       cutensornetSliceGroup_t *sliceGroup);

/**
 * \brief  Releases the resources associated with a `cutensornetSliceGroup_t` object and sets its value to null.
 *
 * \param[in,out] sliceGroup Opaque object specifying the slices to be contracted (see cutensornetCreateSliceGroupFromIDRange() and cutensornetCreateSliceGroupFromIDs()).
 */
cutensornetStatus_t cutensornetDestroySliceGroup(cutensornetSliceGroup_t sliceGroup);

/**
 * \brief Performs the actual contraction of the tensor network.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] plan Encodes the execution of a tensor network contraction (see cutensornetCreateContractionPlan() and cutensornetContractionAutotune()).
 * \param[in] rawDataIn Array of N pointers (N being the number of input tensors specified cutensornetCreateNetworkDescriptor()); ``rawDataIn[i]`` points to the data associated with the i-th input tensor (in device memory).
 * \param[out] rawDataOut Points to the raw data of the output tensor (in device memory).
 * \param[in] accumulateOutput If 0, write the contraction result into rawDataOut; otherwise accumulate the result into rawDataOut.
 * \param[in] workDesc Opaque structure describing the workspace. The provided workspace must be \em valid (the workspace size must be the same as or larger than both the minimum needed and the value provided at plan creation). See cutensornetCreateContractionPlan(), cutensornetWorkspaceGetSize() & cutensornetWorkspaceSet()).
 * If a device memory handler is set, then \p workDesc can be set to null, or the workspace pointer in \p workDesc can be set to null, and the workspace size can be set either to 0 (in which case the "recommended" size is used, see ::CUTENSORNET_WORKSIZE_PREF_RECOMMENDED) or to a \em valid size. A workspace of the specified size will be drawn from the user's mempool and released back once done.
 * \param[in] sliceGroup Opaque object specifying the slices to be contracted (see cutensornetCreateSliceGroupFromIDRange() and cutensornetCreateSliceGroupFromIDs()). *If set to null, all slices will be contracted.*
 * \param[in] stream The CUDA stream on which the computation is performed.
 *
 */
cutensornetStatus_t cutensornetContractSlices(const cutensornetHandle_t handle,
                                              const cutensornetContractionPlan_t plan,
                                              const void* const rawDataIn[],
                                              void* rawDataOut,
                                              int32_t accumulateOutput,
                                              const cutensornetWorkspaceDescriptor_t workDesc,
                                              const cutensornetSliceGroup_t sliceGroup,
                                              cudaStream_t stream);

/**
 * \brief Get the current device memory handler.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[out] devMemHandler If previously set, the struct pointed to by \p handler is filled in, otherwise ::CUTENSORNET_STATUS_NO_DEVICE_ALLOCATOR is returned.
 */
cutensornetStatus_t cutensornetGetDeviceMemHandler(cutensornetHandle_t            handle, 
                                                   cutensornetDeviceMemHandler_t* devMemHandler); 
 
/**
 * \brief Set the current device memory handler.
 *
 * Once set, when cuTensorNet needs device memory in various API calls it will allocate from the user-provided memory pool
 * and deallocate at completion. See ::cutensornetDeviceMemHandler_t and APIs that require ::cutensornetWorkspaceDescriptor_t
 * for further detail.
 *
 * The internal stream order is established using the user-provided stream passed to cutensornetContractionAutotune() and
 * cutensornetContraction().
 *
 * \warning It is <em> undefined behavior </em> for the following scenarios:
 *   - the library handle is bound to a memory handler and subsequently to another handler
 *   - the library handle outlives the attached memory pool
 *   - the memory pool is not <em> stream-ordered </em>
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] devMemHandler the device memory handler that encapsulates the user's mempool. The struct content is copied internally.
 */
cutensornetStatus_t cutensornetSetDeviceMemHandler(cutensornetHandle_t                  handle, 
                                                   const cutensornetDeviceMemHandler_t* devMemHandler); 

/**
 * \brief This function sets the logging callback routine.
 * \param[in] callback Pointer to a callback function. Check ::cutensornetLoggerCallback_t.
 */
cutensornetStatus_t cutensornetLoggerSetCallback(cutensornetLoggerCallback_t callback);

/**
 * \brief This function sets the logging callback routine, along with user data.
 * \param[in] callback Pointer to a callback function. Check ::cutensornetLoggerCallbackData_t.
 * \param[in] userData Pointer to user-provided data to be used by the callback.
 */
cutensornetStatus_t cutensornetLoggerSetCallbackData(cutensornetLoggerCallbackData_t callback,
                                                     void* userData);

/**
 * \brief This function sets the logging output file.
 * \param[in] file An open file with write permission.
 */
cutensornetStatus_t cutensornetLoggerSetFile(FILE* file);

/**
 * \brief This function opens a logging output file in the given path.
 * \param[in] logFile Path to the logging output file.
 */
cutensornetStatus_t cutensornetLoggerOpenFile(const char* logFile);

/**
 * \brief This function sets the value of the logging level.
 * \param[in] level Log level, should be one of the following:
 * Level| Summary           | Long Description
 * -----|-------------------|-----------------
 *  "0" | Off               | logging is disabled (default)
 *  "1" | Errors            | only errors will be logged
 *  "2" | Performance Trace | API calls that launch CUDA kernels will log their parameters and important information
 *  "3" | Performance Hints | hints that can potentially improve the application's performance
 *  "4" | Heuristics Trace  | provides general information about the library execution, may contain details about heuristic status
 *  "5" | API Trace         | API Trace - API calls will log their parameter and important information
 */
cutensornetStatus_t cutensornetLoggerSetLevel(int32_t level);

/**
 * \brief This function sets the value of the log mask.
 *
 * \param[in]  mask  Value of the logging mask.
 * Masks are defined as a combination (bitwise OR) of the following masks:
 * Level| Description       |
 * -----|-------------------|
 *  "0" | Off               |
 *  "1" | Errors            |
 *  "2" | Performance Trace |
 *  "4" | Performance Hints |
 *  "8" | Heuristics Trace  |
 *  "16"| API Trace         |
 *
 * Refer to cutensornetLoggerSetLevel() for details.
 */
cutensornetStatus_t cutensornetLoggerSetMask(int32_t mask);

/**
 * \brief This function disables logging for the entire run.
 */
cutensornetStatus_t cutensornetLoggerForceDisable();

/**
 * \brief Returns Version number of the cuTensorNet library
 */
size_t cutensornetGetVersion();

/**
 * \brief Returns version number of the CUDA runtime that cuTensorNet was compiled against
 * \details Can be compared against the CUDA runtime version from cudaRuntimeGetVersion().
 */
size_t cutensornetGetCudartVersion();

/**
 * \brief Returns the description string for an error code
 * \param[in] error Error code to convert to string.
 * \returns the error string
 * \remarks non-blocking, no reentrant, and thread-safe
 */
const char *cutensornetGetErrorString(cutensornetStatus_t error);

#if defined(__cplusplus)
}
#endif /* __cplusplus */
