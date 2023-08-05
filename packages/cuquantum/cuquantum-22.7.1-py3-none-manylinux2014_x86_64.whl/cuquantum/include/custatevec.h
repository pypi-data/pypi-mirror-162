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

/** @file custatevec.h
 *  @details custatevec API Version 1.1.0.14
 */

/**
 * \defgroup overview Overview of cuStateVec key features
 * \{ */

/**
 *  \page state_vector Description of state vectors
 *  In the cuStateVec library, the state vector is always given as a device array and its
 *  data type is specified by a \p cudaDataType_t constant. It's users' responsibility to manage
 *  memory for the state vector.
 *
 *  This version of cuStateVec library supports 128-bit complex (complex128) and 64-bit complex
 *  (complex64) as datatypes of the state vector. The size of a state vector is represented by the
 *  \p nIndexBits argument which corresponds to the number of qubits in a circuit.
 *  Therefore, the state vector size is expressed as \f$2^{\text{nIndexBits}}\f$.
 *
 *  The type ::custatevecIndex_t is provided to express the state vector index, which is
 *  a typedef of the 64-bit signed integer.
 */

/**
 *  \page bit_ordering Bit Ordering
 *  In the cuStateVec library, the bit ordering of the state vector index is defined
 *  in the little endian order. The 0-th index bit is the least significant bit (LSB).
 *  Most functions accept arguments to specify bit positions as integer arrays. Those bit positions
 *  are specified in the little endian order. Values in bit positions are in the range
 *  \f$[0, \text{nIndexBits})\f$.
 *
 *  In order to represent bit strings, a pair of \p bitString and \p bitOrdering arguments
 *  are used. The \p bitString argument specifies bit string values as an array of 0 and 1.
 *  The \p bitOrdering argument specifies the bit positions of the \p bitString array elements
 *  in the little endian order.
 *
 *  In the following example, "10" is specified as a bit string. Bit string values are mapped to
 *  the 2nd and 3rd index bits and can be used to specify a bit mask, \f$*\cdots *10*\f$.
 *
 *  \code
 *   int32_t bitString[]   = {0, 1}
 *   int32_t bitOrdering[] = {1, 2}
 *  \endcode
 */

/**
 *  \page data_types Supported data types
 *
 *  By default, computation is executed by the corresponding precision of the state vector,
 *  double float (FP64) for complex128 and single float (FP32) for complex64.
 *
 *  The cuStateVec library also provides the compute type, allowing computation with reduced
 *  precision. Some cuStateVec functions accept the compute type specified by using
 *  ::custatevecComputeType_t.
 *
 *  Below is the table of combinations of state vector and compute types available in the current
 *  version of the cuStateVec library.
 *
 *  State vector / cudaDataType_t | Matrix / cudaDataType_t  | Compute / custatevecComputeType_t
 *  ------------------------------|--------------------------|----------------------------------
 *  Complex 128 / CUDA_C_F64      | Complex 128 / CUDA_C_F64 | FP64 / CUSTATEVEC_COMPUTE_64F
 *  Complex 64  / CUDA_C_F32      | Complex 128 / CUDA_C_F64 | FP32 / CUSTATEVEC_COMPUTE_32F
 *  Complex 64  / CUDA_C_F32      | Complex 64  / CUDA_C_F32 | FP32 / CUSTATEVEC_COMPUTE_32F
 *
 *  \note ::CUSTATEVEC_COMPUTE_TF32 is not available at this version.
 */

/**
 *  \page workspace Workspace
 *  The cuStateVec library internally manages temporary device memory for executing functions,
 *  which is referred to as context workspace.
 *
 *  The context workspace is attached to the cuStateVec context and allocated when a cuStateVec
 *  context is created by calling custatevecCreate(). The default size of the context workspace
 *  is chosen to cover most typical use cases, obtained by calling
 *  custatevecGetDefaultWorkspaceSize().
 *
 *  When the context workspace cannot provide enough amount of temporary memory or when a device 
 *  memory chunk is shared by two or more functions, there are two options for users:
 *    - Users can provide user-managed device memory for the extra workspace.
 *      Functions that need the extra workspace have their sibling functions suffixed by 
 *      ``GetWorkspaceSize()``. If these functions return a nonzero value via the \p extraBufferSizeInBytes 
 *      argument, users are requested to allocate a device memory and supply the pointer to the allocated 
 *      memory to the corresponding function. The extra workspace should be 256-byte aligned, which is 
 *      automatically satisfied by using ``cudaMalloc()`` to allocate device memory. If the size of 
 *      the extra workspace is not enough, ::CUSTATEVEC_STATUS_INSUFFICIENT_WORKSPACE is returned.
 *    - Users also can set a device memory handler. When it is set to the cuStateVec library context,
 *      the library can directly draw memory from the pool on users's behalf. In this case, users are not
 *      required to allocate device memory explicitly and a null pointer (zero size) can be specified as the
 *      extra workspace (size) in the function. Please refer to ::custatevecDeviceMemHandler_t and
 *      custatevecSetDeviceMemHandler() for details.
 */

/** \} end of overview */

#pragma once

#define CUSTATEVEC_VER_MAJOR 1 //!< cuStateVec major version.
#define CUSTATEVEC_VER_MINOR 1 //!< cuStateVec minor version.
#define CUSTATEVEC_VER_PATCH 0 //!< cuStateVec patch version.
#define CUSTATEVEC_VERSION 1100 //!< cuStateVec Version.

#define CUSTATEVEC_ALLOCATOR_NAME_LEN 64

#include <library_types.h>                        // cudaDataType_t
#include <cuda_runtime_api.h>                     // cudaStream_t

#if !defined(CUSTATEVECAPI)
#    if defined(_WIN32)
#        define CUSTATEVECAPI __stdcall //!< cuStateVec calling convention
#    else
#        define CUSTATEVECAPI           //!< cuStateVec calling convention
#    endif
#endif

#if defined(__cplusplus)
#include <cstdint>                                // integer types
#include <cstdio>                                 // FILE

extern "C" {
#else
#include <stdint.h>                               // integer types
#include <stdio.h>                                // FILE

#endif // defined(__cplusplus)

/**
 * \defgroup datastructures Opaque data structures
 * \{ */

/** 
 * \typedef custatevecIndex_t
 *
 * \brief Type for state vector indexing.
 * \details This type is used to represent the indices of the state vector.
 * As every bit in the state vector index corresponds to one qubit in a circuit,
 * this type is also used to represent bit strings.
 * The bit ordering is in little endian. The 0-th bit is the LSB.
 */
typedef int64_t custatevecIndex_t;


/**
 * \typedef custatevecHandle_t
 * \brief This handle stores necessary information for carrying out state vector calculations.
 * \details This handle holds the cuStateVec library context (device properties, system information,
 * etc.), which is used in all cuStateVec function calls.
 * The handle must be initialized and destroyed using the custatevecCreate() and custatevecDestroy()
 * functions, respectively.
 */
typedef struct custatevecContext* custatevecHandle_t;


/**
 * \typedef custatevecSamplerDescriptor_t
 * \brief This descriptor holds the context of the sampling operation, initialized using custatevecSamplerCreate()
 * and destroyed using custatevecSamplerDestroy(), respectively.
 */

typedef struct custatevecSamplerDescriptor* custatevecSamplerDescriptor_t;


/**
 * \typedef custatevecAccessorDescriptor_t
 * \brief This descriptor holds the context of accessor operation, initialized using custatevecAccessorCreate()
 * and destroyed using custatevecAccessorDestroy(), respectively.
 */

typedef struct custatevecAccessorDescriptor* custatevecAccessorDescriptor_t;


/**
 * \typedef custatevecLoggerCallback_t
 * \brief A callback function pointer type for logging. Use custatevecLoggerSetCallback() to set the callback function.
 * \param[in] logLevel the log level
 * \param[in] functionName the name of the API that logged this message
 * \param[in] message the log message
 */
typedef void(*custatevecLoggerCallback_t)(
        int32_t logLevel,
        const char* functionName,
        const char* message
);

/**
 * \typedef custatevecLoggerCallbackData_t
 * \brief A callback function pointer type for logging, with user data accepted. Use custatevecLoggerSetCallbackData() to set the callback function.
 * \param[in] logLevel the log level
 * \param[in] functionName the name of the API that logged this message
 * \param[in] message the log message
 * \param[in] userData the user-provided data to be used inside the callback function
 */
typedef void(*custatevecLoggerCallbackData_t)(
        int32_t logLevel,
        const char* functionName,
        const char* message,
        void* userData
);

/**
 * \brief The device memory handler structure holds information about the user-provided, \em stream-ordered device memory pool (mempool).
 */
typedef struct { 
  /**
   * A pointer to the user-owned mempool/context object.
   */
  void* ctx;
  /**
   * A function pointer to the user-provided routine for allocating device memory of \p size on \p stream.
   *
   * The allocated memory should be made accessible to the current device (or more
   * precisely, to the current CUDA context bound to the library handle).
   *
   * This interface supports any stream-ordered memory allocator \p ctx. Upon success,
   * the allocated memory can be immediately used on the given stream by any
   * operations enqueued/ordered on the same stream after this call.
   *
   * It is the caller’s responsibility to ensure a proper stream order is established.
   *
   * The allocated memory should be at least 256-byte aligned.
   *
   * \param[in] ctx A pointer to the user-owned mempool object.
   * \param[out] ptr On success, a pointer to the allocated buffer.
   * \param[in] size The amount of memory in bytes to be allocated.
   * \param[in] stream The CUDA stream on which the memory is allocated (and the stream order is established).
   * \return Error status of the invocation. Return 0 on success and any nonzero integer otherwise. This function must not throw if it is a C++ function.
   *
   */
  int (*device_alloc)(void* ctx, void** ptr, size_t size, cudaStream_t stream);
  /**
   * A function pointer to the user-provided routine for deallocating device memory of \p size on \p stream.
   * 
   * This interface supports any stream-ordered memory allocator. Upon success, any 
   * subsequent accesses (of the memory pointed to by the pointer \p ptr) ordered after 
   * this call are undefined behaviors.
   *
   * It is the caller’s responsibility to ensure a proper stream order is established.
   *
   * If the arguments \p ctx and \p size are not the same as those passed to \p device_alloc to 
   * allocate the memory pointed to by \p ptr, the behavior is undefined.
   * 
   * The argument \p stream need not be identical to the one used for allocating \p ptr, as
   * long as the stream order is correctly established. The behavior is undefined if
   * this assumption is not held.
   *
   * \param[in] ctx A pointer to the user-owned mempool object.
   * \param[in] ptr The pointer to the allocated buffer.
   * \param[in] size The size of the allocated memory.
   * \param[in] stream The CUDA stream on which the memory is deallocated (and the stream ordering is established).
   * \return Error status of the invocation. Return 0 on success and any nonzero integer otherwise. This function must not throw if it is a C++ function.
   */
  int (*device_free)(void* ctx, void* ptr, size_t size, cudaStream_t stream); 
  /**
   * The name of the provided mempool.
   */
  char name[CUSTATEVEC_ALLOCATOR_NAME_LEN];
} custatevecDeviceMemHandler_t;

/** \} end of datastructures */


/**
 * \defgroup enumerators Enumerators
 *
 * \{ */

/**
 * \typedef custatevecStatus_t
 * \brief Contains the library status. Each cuStateVec API returns this enumerator.
 */
typedef enum custatevecStatus_t {
    CUSTATEVEC_STATUS_SUCCESS                   = 0, ///< The API call has finished successfully
    CUSTATEVEC_STATUS_NOT_INITIALIZED           = 1, ///< The library handle was not initialized
    CUSTATEVEC_STATUS_ALLOC_FAILED              = 2, ///< Memory allocation in the library was failed
    CUSTATEVEC_STATUS_INVALID_VALUE             = 3, ///< Wrong parameter was passed. For example, a null pointer as input data, or an invalid enum value
    CUSTATEVEC_STATUS_ARCH_MISMATCH             = 4, ///< The device capabilities are not enough for the set of input parameters provided
    CUSTATEVEC_STATUS_EXECUTION_FAILED          = 5, ///< Error during the execution of the device tasks
    CUSTATEVEC_STATUS_INTERNAL_ERROR            = 6, ///< Unknown error occured in the library
    CUSTATEVEC_STATUS_NOT_SUPPORTED             = 7, ///< API is not supported by the backend
    CUSTATEVEC_STATUS_INSUFFICIENT_WORKSPACE    = 8, ///< Workspace on device is too small to execute
    CUSTATEVEC_STATUS_SAMPLER_NOT_PREPROCESSED  = 9, ///< Sampler was called prior to preprocessing
    CUSTATEVEC_STATUS_NO_DEVICE_ALLOCATOR       = 10, ///< The device memory pool was not set
    CUSTATEVEC_STATUS_MAX_VALUE                 = 11
} custatevecStatus_t;


/**
 * \typedef custatevecPauli_t
 * \brief Constants to specify Pauli basis:
 *   - \f$\boldsymbol{\sigma}_0 = \mathbf{I} = \left[ \begin{array}{rr} 1 & 0 \\ 0 & 1 \end{array}\right]\f$
 *   - \f$\boldsymbol{\sigma}_x = \left[ \begin{array}{rr} 0 & 1 \\ 1 & 0 \end{array}\right]\f$
 *   - \f$\boldsymbol{\sigma}_y = \left[ \begin{array}{rr} 0 & -i \\ i & 0 \end{array}\right]\f$
 *   - \f$\boldsymbol{\sigma}_z = \left[ \begin{array}{rr} 1 & 0 \\ 0 & -1 \end{array}\right]\f$
 */
typedef enum custatevecPauli_t {
    CUSTATEVEC_PAULI_I = 0, ///< Identity matrix
    CUSTATEVEC_PAULI_X = 1, ///< Pauli X matrix
    CUSTATEVEC_PAULI_Y = 2, ///< Pauli Y matrix
    CUSTATEVEC_PAULI_Z = 3  ///< Pauli Z matrix
} custatevecPauli_t;


/**
 * \typedef custatevecMatrixLayout_t
 * \brief Constants to specify a matrix's memory layout.
 */
typedef enum custatevecMatrixLayout_t {
    CUSTATEVEC_MATRIX_LAYOUT_COL = 0, ///< Matrix stored in the column-major order
    CUSTATEVEC_MATRIX_LAYOUT_ROW = 1  ///< Matrix stored in the row-major order
} custatevecMatrixLayout_t;


/**
 * \typedef custatevecMatrixType_t
 * \brief Constants to specify the matrix type.
 */
typedef enum custatevecMatrixType_t {
    CUSTATEVEC_MATRIX_TYPE_GENERAL   = 0, ///< Non-specific type
    CUSTATEVEC_MATRIX_TYPE_UNITARY   = 1, ///< Unitary matrix
    CUSTATEVEC_MATRIX_TYPE_HERMITIAN = 2  ///< Hermitian matrix
} custatevecMatrixType_t;

/**
 * \typedef custatevecCollapseOp_t
 * \brief Constants to specify collapse operations
 */

typedef enum custatevecCollapseOp_t {
    CUSTATEVEC_COLLAPSE_NONE               = 0, ///< Do not collapse the statevector
    CUSTATEVEC_COLLAPSE_NORMALIZE_AND_ZERO = 1  ///< Collapse, normalize, and fill zeros in the statevector
} custatevecCollapseOp_t;


/**
 * \typedef custatevecComputeType_t
 *
 * \brief Constants to specify the minimal accuracy for arithmetic operations
 */

typedef enum custatevecComputeType_t {
    CUSTATEVEC_COMPUTE_DEFAULT = 0,           ///< FP32(float) for Complex64, FP64(double) for Complex128
    CUSTATEVEC_COMPUTE_32F     = (1U << 2U),  ///< FP32(float)
    CUSTATEVEC_COMPUTE_64F     = (1U << 4U),  ///< FP64(double)
    CUSTATEVEC_COMPUTE_TF32    = (1U << 12U)  ///< TF32(tensor-float-32)
} custatevecComputeType_t;


/**
 * \typedef custatevecSamplerOutput_t
 *
 * \brief Constants to specify the order of bit strings in sampling outputs
 */

typedef enum custatevecSamplerOutput_t {
    CUSTATEVEC_SAMPLER_OUTPUT_RANDNUM_ORDER   = 0,  ///< the same order as the given random numbers
    CUSTATEVEC_SAMPLER_OUTPUT_ASCENDING_ORDER = 1,  ///< reordered in the ascending order
} custatevecSamplerOutput_t;


/**
 * \typedef custatevecDeviceNetworkType_t
 *
 * \brief Constants to specify the device network topology
 */

typedef enum custatevecDeviceNetworkType_t
{
    CUSTATEVEC_DEVICE_NETWORK_TYPE_SWITCH   = 1, ///< devices are connected via network switch
    CUSTATEVEC_DEVICE_NETWORK_TYPE_FULLMESH = 2, ///< devices are connected by full mesh network
} custatevecDeviceNetworkType_t;


/** \} end of enumerators */

/**
 * \defgroup management Initialization and management routines
 * \{ */

/**
 * \brief This function initializes the cuStateVec library and creates a handle
 * on the cuStateVec context. It must be called prior to any other cuStateVec
 * API functions.
 *
 * \param[in]  handle  the pointer to the handle to the cuStateVec context
 */
custatevecStatus_t 
custatevecCreate(custatevecHandle_t* handle);

/**
 * \brief This function releases resources used by the cuStateVec
 * library.
 *
 * \param[in]  handle  the handle to the cuStateVec context
 */
custatevecStatus_t
custatevecDestroy(custatevecHandle_t handle);


/**
 * \brief This function returns the default workspace size defined by the
 * cuStateVec library.
 *
 * \param[in] handle the handle to the cuStateVec context
 * \param[out] workspaceSizeInBytes default workspace size
 *
 * \details This function returns the default size used for the workspace.
 */
custatevecStatus_t
custatevecGetDefaultWorkspaceSize(custatevecHandle_t handle,
                                  size_t*            workspaceSizeInBytes);


/**
 * \brief This function sets the workspace used by the cuStateVec library.
 *
 * \param[in] handle the handle to the cuStateVec context
 * \param[in] workspace device pointer to workspace
 * \param[in] workspaceSizeInBytes workspace size
 *
 * \details This function sets the workspace attached to the handle.
 * The required size of the workspace is obtained by
 * custatevecGetDefaultWorkspaceSize().
 *
 * By setting a larger workspace, users are able to execute functions without
 * allocating the extra workspace in some functions.
 * 
 * If a device memory handler is set, the \p workspace can be set to null and 
 * the workspace is allocated using the user-defined memory pool.
 */
custatevecStatus_t
custatevecSetWorkspace(custatevecHandle_t handle,
                       void*              workspace,
                       size_t             workspaceSizeInBytes);

/** 
 * \brief This function returns the name string for the input error code.
 * If the error code is not recognized, "unrecognized error code" is returned.
 *
 * \param[in] status Error code to convert to string
 */
const char*
custatevecGetErrorName(custatevecStatus_t status);

/**
 * \brief This function returns the description string for an error code. If 
 * the error code is not recognized, "unrecognized error code" is returned.
 
 * \param[in] status Error code to convert to string
 */
const char*
custatevecGetErrorString(custatevecStatus_t status);

/**
 * \brief This function returns the version information of the cuStateVec 
 * library.
 *
 * \param[in] type requested property (`MAJOR_VERSION`, 
 * `MINOR_VERSION`, or `PATCH_LEVEL`).
 * \param[out] value value of the requested property.
 */
custatevecStatus_t
custatevecGetProperty(libraryPropertyType type,
                      int32_t*            value);

/**
 * \brief This function returns the version information of the cuStateVec 
 *  library.
 */
size_t custatevecGetVersion();

/**
 * \brief This function sets the stream to be used by the cuStateVec library
 * to execute its routine.
 *
 * \param[in]  handle    the handle to the cuStateVec context
 * \param[in]  streamId  the stream to be used by the library
 */
custatevecStatus_t
custatevecSetStream(custatevecHandle_t handle,
                    cudaStream_t       streamId);


/**
 * \brief This function gets the cuStateVec library stream used to execute all
 * calls from the cuStateVec library functions.
 *
 * \param[in]  handle    the handle to the cuStateVec context
 * \param[out] streamId  the stream to be used by the library
 */
custatevecStatus_t
custatevecGetStream(custatevecHandle_t handle,
                    cudaStream_t*      streamId);

/**
 * \brief Experimental: This function sets the logging callback function.
 *
 * \param[in]  callback   Pointer to a callback function. See ::custatevecLoggerCallback_t.
 */
custatevecStatus_t
custatevecLoggerSetCallback(custatevecLoggerCallback_t callback);

/**
 * \brief Experimental: This function sets the logging callback function with user data.
 *
 * \param[in]  callback   Pointer to a callback function. See ::custatevecLoggerCallbackData_t.
 * \param[in]  userData   Pointer to user-provided data.
 */
custatevecStatus_t
custatevecLoggerSetCallbackData(custatevecLoggerCallbackData_t callback,
                                void* userData);

/**
 * \brief Experimental: This function sets the logging output file. 
 * \note Once registered using this function call, the provided file handle
 * must not be closed unless the function is called again to switch to a 
 * different file handle.
 *
 * \param[in]  file  Pointer to an open file. File should have write permission.
 */
custatevecStatus_t
custatevecLoggerSetFile(FILE* file);

/**
 * \brief Experimental: This function opens a logging output file in the given 
 * path.
 *
 * \param[in]  logFile  Path of the logging output file.
 */
custatevecStatus_t
custatevecLoggerOpenFile(const char* logFile);

/**
 * \brief Experimental: This function sets the value of the logging level.
 * \details Levels are defined as follows:
 * Level| Summary           | Long Description
 * -----|-------------------|-----------------
 *  "0" | Off               | logging is disabled (default)
 *  "1" | Errors            | only errors will be logged
 *  "2" | Performance Trace | API calls that launch CUDA kernels will log their parameters and important information
 *  "3" | Performance Hints | hints that can potentially improve the application's performance
 *  "4" | Heuristics Trace  | provides general information about the library execution, may contain details about heuristic status
 *  "5" | API Trace         | API Trace - API calls will log their parameter and important information
 * \param[in]  level  Value of the logging level.
 */
custatevecStatus_t
custatevecLoggerSetLevel(int32_t level);

/**
 * \brief Experimental: This function sets the value of the logging mask.
 * Masks are defined as a combination of the following masks:
 * Level| Description       |
 * -----|-------------------|
 *  "0" | Off               |
 *  "1" | Errors            |
 *  "2" | Performance Trace |
 *  "4" | Performance Hints |
 *  "8" | Heuristics Trace  |
 *  "16"| API Trace         |
 * Refer to ::custatevecLoggerCallback_t for the details.
 * \param[in]  mask  Value of the logging mask.
 */
custatevecStatus_t
custatevecLoggerSetMask(int32_t mask);

/**
 * \brief Experimental: This function disables logging for the entire run.
 */
custatevecStatus_t
custatevecLoggerForceDisable();

/**
 * \brief Get the current device memory handler.
 *
 * \param[in] handle Opaque handle holding cuStateVec's library context.
 * \param[out] handler If previously set, the struct pointed to by \p handler is filled in, otherwise ::CUSTATEVEC_STATUS_NO_DEVICE_ALLOCATOR is returned.
 */
custatevecStatus_t custatevecGetDeviceMemHandler(custatevecHandle_t            handle, 
                                                 custatevecDeviceMemHandler_t* handler); 
 
/**
 * \brief Set the current device memory handler.
 *
 * Once set, when cuStateVec needs device memory in various API calls it will allocate from the user-provided memory pool
 * and deallocate at completion. See custatevecDeviceMemHandler_t and APIs that require extra workspace for further detail.
 *
 * The internal stream order is established using the user-provided stream set via custatevecSetStream().
 *
 * If \p handler argument is set to nullptr, the library handle will detach its existing memory handler.
 *
 * \warning It is <em> undefined behavior </em> for the following scenarios:
 *   - the library handle is bound to a memory handler and subsequently to another handler
 *   - the library handle outlives the attached memory pool
 *   - the memory pool is not <em> stream-ordered </em>
 *
 * \param[in] handle Opaque handle holding cuStateVec's library context.
 * \param[in] handler the device memory handler that encapsulates the user's mempool. The struct content is copied internally.
 */
custatevecStatus_t custatevecSetDeviceMemHandler(custatevecHandle_t                  handle, 
                                                 const custatevecDeviceMemHandler_t* handler); 
/** \} end of management*/

/**
 * \defgroup singlegpuapi Single GPU API
 *
 * \{ */

/*
 * Sum of squared absolute values of state vector elements
 */

/**
 * \brief Calculates the sum of squared absolute values on a given Z product basis.
 * 
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] sv state vector
 * \param[in] svDataType data type of state vector
 * \param[in] nIndexBits the number of index bits
 * \param[out] abs2sum0 pointer to a host or device variable to store the sum of squared absolute values for parity == 0
 * \param[out] abs2sum1 pointer to a host or device variable to store the sum of squared absolute values for parity == 1
 * \param[in] basisBits pointer to a host array of Z-basis index bits
 * \param[in] nBasisBits the number of basisBits
 *
 * \details This function calculates sums of squared absolute values on a given Z product basis.
 * If a null pointer is specified to \p abs2sum0 or \p abs2sum1, the sum for the corresponding
 * value is not calculated.
 * Since the sum of (\p abs2sum0 + \p abs2sum1) is identical to the norm of the state vector,
 * one can calculate the probability where parity == 0 as (\p abs2sum0 / (\p abs2sum0 + \p abs2sum1)).
 */

custatevecStatus_t
custatevecAbs2SumOnZBasis(custatevecHandle_t  handle,
                          const void*         sv,
                          cudaDataType_t      svDataType,
                          const uint32_t      nIndexBits,
                          double*             abs2sum0,
                          double*             abs2sum1,
                          const int32_t*      basisBits,
                          const uint32_t      nBasisBits);


/**
 * \brief Calculate abs2sum array for a given set of index bits
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] sv state vector
 * \param[in] svDataType data type of state vector
 * \param[in] nIndexBits the number of index bits
 * \param[out] abs2sum pointer to a host or device array of sums of squared absolute values
 * \param[in] bitOrdering pointer to a host array of index bit ordering
 * \param[in] bitOrderingLen the length of bitOrdering
 * \param[in] maskBitString pointer to a host array for a bit string to specify mask
 * \param[in] maskOrdering  pointer to a host array for the mask ordering
 * \param[in] maskLen the length of mask
 *
 * \details Calculates an array of sums of squared absolute values of state vector elements.
 * The abs2sum array can be on host or device. The index bit ordering abs2sum array is specified
 * by the \p bitOrdering and \p bitOrderingLen arguments. Unspecified bits are folded (summed up).
 *
 * The \p maskBitString, \p maskOrdering and \p maskLen arguments set bit mask in the state
 * vector index.  The abs2sum array is calculated by using state vector elements whose indices 
 * match the mask bit string. If the \p maskLen argument is 0, null pointers can be specified to the
 * \p maskBitString and \p maskOrdering arguments, and all state vector elements are used
 * for calculation.
 *
 * By definition, bit positions in \p bitOrdering and \p maskOrdering arguments should not overlap.
 *
 * The empty \p bitOrdering can be specified to calculate the norm of state vector. In this case,
 * 0 is passed to the \p bitOrderingLen argument and the \p bitOrdering argument can be a null pointer.
 *
 * \note Since the size of abs2sum array is proportional to \f$ 2^{bitOrderingLen} \f$ ,
 * the max length of \p bitOrdering depends on the amount of available memory and \p maskLen.
 */

custatevecStatus_t
custatevecAbs2SumArray(custatevecHandle_t handle,
                       const void*        sv,
                       cudaDataType_t     svDataType,
                       const uint32_t     nIndexBits,
                       double*            abs2sum,
                       const int32_t*     bitOrdering,
                       const uint32_t     bitOrderingLen,
                       const int32_t*     maskBitString,
                       const int32_t*     maskOrdering,
                       const uint32_t     maskLen);


/**
 * \brief Collapse state vector on a given Z product basis.
 * 
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] sv state vector
 * \param[in] svDataType data type of state vector
 * \param[in] nIndexBits the number of index bits
 * \param[in] parity parity, 0 or 1
 * \param[in] basisBits pointer to a host array of Z-basis index bits
 * \param[in] nBasisBits the number of Z basis bits
 * \param[in] norm normalization factor
 *
 * \details This function collapses state vector on a given Z product basis.
 * The state elements that match the parity argument are scaled by a factor
 * specified in the \p norm argument. Other elements are set to zero.
 */

custatevecStatus_t
custatevecCollapseOnZBasis(custatevecHandle_t handle,
                           void*              sv,
                           cudaDataType_t     svDataType,
                           const uint32_t     nIndexBits,
                           const int32_t      parity,
                           const int32_t*     basisBits,
                           const uint32_t     nBasisBits,
                           double             norm);


/**
 * \brief Collapse state vector to the state specified by a given bit string.
 * 
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] sv state vector
 * \param[in] svDataType data type of state vector
 * \param[in] nIndexBits the number of index bits
 * \param[in] bitString pointer to a host array of bit string
 * \param[in] bitOrdering pointer to a host array of bit string ordering
 * \param[in] bitStringLen length of bit string
 * \param[in] norm normalization constant
 *
 * \details This function collapses state vector to the state specified by a given bit string.
 * The state vector elements specified by the \p bitString, \p bitOrdering and \p bitStringLen arguments are
 * normalized by the \p norm argument. Other elements are set to zero.
 *
 * At least one basis bit should be specified, otherwise this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 */

custatevecStatus_t
custatevecCollapseByBitString(custatevecHandle_t handle,
                              void*              sv,
                              cudaDataType_t     svDataType,
                              const uint32_t     nIndexBits,
                              const int32_t*     bitString,
                              const int32_t*     bitOrdering,
                              const uint32_t     bitStringLen,
                              double             norm);


/*
 * Measurement
 */

/**
 * \brief Measurement on a given Z-product basis
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] sv state vector
 * \param[in] svDataType data type of state vector
 * \param[in] nIndexBits the number of index bits
 * \param[out] parity parity, 0 or 1
 * \param[in] basisBits pointer to a host array of Z basis bits
 * \param[in] nBasisBits the number of Z basis bits
 * \param[in] randnum random number, [0, 1).
 * \param[in] collapse Collapse operation
 *
 * \details This function does measurement on a given Z product basis.
 * The measurement result is the parity of the specified Z product basis.
 * At least one basis bit should be specified, otherwise this function fails.
 *
 * If ::CUSTATEVEC_COLLAPSE_NONE is specified for the collapse argument,
 * this function only returns the measurement result without collapsing the state vector.
 * If ::CUSTATEVEC_COLLAPSE_NORMALIZE_AND_ZERO is specified,
 * this function collapses the state vector as custatevecCollapseOnZBasis() does.
 *
 * If a random number is not in [0, 1), this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 * At least one basis bit should be specified, otherwise this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 */

custatevecStatus_t
custatevecMeasureOnZBasis(custatevecHandle_t          handle,
                          void*                       sv,
                          cudaDataType_t              svDataType,
                          const uint32_t              nIndexBits,
                          int32_t*                    parity,
                          const int32_t*              basisBits,
                          const uint32_t              nBasisBits,
                          const double                randnum,
                          enum custatevecCollapseOp_t collapse);



/**
 * \brief Batched single qubit measurement
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] sv state vector
 * \param[in] svDataType data type of the state vector
 * \param[in] nIndexBits the number of index bits
 * \param[out] bitString pointer to a host array of measured bit string
 * \param[in] bitOrdering pointer to a host array of bit string ordering
 * \param[in] bitStringLen length of bitString
 * \param[in] randnum random number, [0, 1).
 * \param[in] collapse  Collapse operation
 *
 * \details This function does batched single qubit measurement and returns a bit string.
 * The \p bitOrdering argument specifies index bits to be measured.  The measurement
 * result is stored in \p bitString in the ordering specified by the \p bitOrdering argument.
 *
 * If ::CUSTATEVEC_COLLAPSE_NONE is specified for the \p collapse argument, this function
 * only returns the measured bit string without collapsing the state vector.
 * When ::CUSTATEVEC_COLLAPSE_NORMALIZE_AND_ZERO is specified, this function
 * collapses the state vector as custatevecCollapseByBitString() does.
 *
 * If a random number is not in [0, 1), this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 * At least one basis bit should be specified, otherwise this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 */
custatevecStatus_t
custatevecBatchMeasure(custatevecHandle_t          handle,
                       void*                       sv,
                       cudaDataType_t              svDataType,
                       const uint32_t              nIndexBits,
                       int32_t*                    bitString,
                       const int32_t*              bitOrdering,
                       const uint32_t              bitStringLen,
                       const double                randnum,
                       enum custatevecCollapseOp_t collapse);


/**
 * \brief Batched single qubit measurement for partial vector
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] sv partial state vector
 * \param[in] svDataType data type of the state vector
 * \param[in] nIndexBits the number of index bits
 * \param[out] bitString pointer to a host array of measured bit string
 * \param[in] bitOrdering pointer to a host array of bit string ordering
 * \param[in] bitStringLen length of bitString
 * \param[in] randnum random number, [0, 1).
 * \param[in] collapse  Collapse operation
 * \param[in] offset partial sum of squared absolute values
 * \param[in] abs2sum sum of squared absolute values for the entire state vector
 *
 * \details This function does batched single qubit measurement and returns a bit string.
 * The \p bitOrdering argument specifies index bits to be measured.  The measurement
 * result is stored in \p bitString in the ordering specified by the \p bitOrdering argument.
 *
 * If ::CUSTATEVEC_COLLAPSE_NONE is specified for the collapse argument, this function
 * only returns the measured bit string without collapsing the state vector.
 * When ::CUSTATEVEC_COLLAPSE_NORMALIZE_AND_ZERO is specified, this function
 * collapses the state vector as custatevecCollapseByBitString() does.
 *
 * This function assumes that \p sv is partial state vector and drops some most significant bits.
 * Prefix sums for lower indices and the entire state vector must be provided as \p offset and \p abs2sum, respectively.
 * When \p offset == \p abs2sum == 0, this function behaves in the same way as custatevecBatchMeasure().
 *
 * If a random number is not in [0, 1), this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 * At least one basis bit should be specified, otherwise this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 */

custatevecStatus_t
custatevecBatchMeasureWithOffset(custatevecHandle_t          handle,
                                 void*                       sv,
                                 cudaDataType_t              svDataType,
                                 const uint32_t              nIndexBits,
                                 int32_t*                    bitString,
                                 const int32_t*              bitOrdering,
                                 const uint32_t              bitStringLen,
                                 const double                randnum,
                                 enum custatevecCollapseOp_t collapse,
                                 const double                offset,
                                 const double                abs2sum);


/*
 *  Gate application
 */

/**
 * \brief Apply the exponential of a multi-qubit Pauli operator.
 * 
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] sv state vector
 * \param[in] svDataType data type of the state vector
 * \param[in] nIndexBits the number of bits in the state vector index
 * \param[in] theta theta
 * \param[in] paulis host pointer to custatevecPauli_t array
 * \param[in] targets pointer to a host array of target bits
 * \param[in] nTargets the number of target bits
 * \param[in] controls pointer to a host array of control bits
 * \param[in] controlBitValues pointer to a host array of control bit values
 * \param[in] nControls the number of control bits
 *
 * \details Apply exponential of a tensor product of Pauli bases
 * specified by bases, \f$ e^{i \theta P} \f$, where \f$P\f$ is the product of Pauli bases.
 * The \p paulis, \p targets, and \p nTargets arguments specify Pauli bases and their bit
 * positions in the state vector index.
 *
 * At least one target and a corresponding Pauli basis should be specified.
 *
 * The \p controls and \p nControls arguments specifies the control bit positions
 * in the state vector index.
 *
 * The \p controlBitValues argument specifies bit values of control bits. The ordering
 * of \p controlBitValues is specified by the \p controls argument. If a null pointer is
 * specified to this argument, all control bit values are set to 1.
 */

custatevecStatus_t
custatevecApplyPauliRotation(custatevecHandle_t       handle,
                             void*                    sv,
                             cudaDataType_t           svDataType,
                             const uint32_t           nIndexBits,
                             double                   theta,
                             const custatevecPauli_t* paulis,
                             const int32_t*           targets,
                             const uint32_t           nTargets,
                             const int32_t*           controls,
                             const int32_t*           controlBitValues,
                             const uint32_t           nControls);


/**
 * \brief This function gets the required workspace size for custatevecApplyMatrix().
 *
 * \param[in] handle the handle to the cuStateVec context
 * \param[in] svDataType Data type of the state vector
 * \param[in] nIndexBits the number of index bits of the state vector
 * \param[in] matrix host or device pointer to a matrix
 * \param[in] matrixDataType data type of matrix
 * \param[in] layout enumerator specifying the memory layout of matrix
 * \param[in] adjoint apply adjoint of matrix
 * \param[in] nTargets the number of target bits
 * \param[in] nControls the number of control bits
 * \param[in] computeType computeType of matrix multiplication
 * \param[out] extraWorkspaceSizeInBytes  workspace size
 *
 * \details This function returns the required extra workspace size to execute
 * custatevecApplyMatrix().
 * \p extraWorkspaceSizeInBytes will be set to 0 if no extra buffer is required
 * for a given set of arguments.
 */
custatevecStatus_t
custatevecApplyMatrixGetWorkspaceSize(custatevecHandle_t       handle,
                                      cudaDataType_t           svDataType,
                                      const uint32_t           nIndexBits,
                                      const void*              matrix,
                                      cudaDataType_t           matrixDataType,
                                      custatevecMatrixLayout_t layout,
                                      const int32_t            adjoint,
                                      const uint32_t           nTargets,
                                      const uint32_t           nControls,
                                      custatevecComputeType_t  computeType,
                                      size_t*                  extraWorkspaceSizeInBytes);

/**
 * \brief Apply gate matrix
 * 
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] sv state vector
 * \param[in] svDataType data type of the state vector
 * \param[in] nIndexBits the number of index bits of the state vector
 * \param[in] matrix host or device pointer to a square matrix
 * \param[in] matrixDataType data type of matrix
 * \param[in] layout enumerator specifying the memory layout of matrix
 * \param[in] adjoint apply adjoint of matrix
 * \param[in] targets pointer to a host array of target bits
 * \param[in] nTargets the number of target bits
 * \param[in] controls pointer to a host array of control bits
 * \param[in] controlBitValues pointer to a host array of control bit values
 * \param[in] nControls the number of control bits
 * \param[in] computeType computeType of matrix multiplication
 * \param[in] extraWorkspace extra workspace
 * \param[in] extraWorkspaceSizeInBytes extra workspace size
 *
 * \details Apply gate matrix to a state vector.
 * The state vector size is \f$2^\text{nIndexBits}\f$.
 *
 * The matrix argument is a host or device pointer of a 2-dimensional array for a square matrix.
 * The size of matrix is (\f$2^\text{nTargets} \times 2^\text{nTargets}\f$ ) and the value type is specified by the
 * \p matrixDataType argument. The \p layout argument specifies the matrix layout which can be in either
 * the row-major or column-major order.
 * The \p targets and \p controls arguments specify target and control bit positions in the state vector
 * index.
 *
 * The \p controlBitValues argument specifies bit values of control bits. The ordering
 * of \p controlBitValues is specified by the \p controls argument. If a null pointer is
 * specified to this argument, all control bit values are set to 1.
 *
 * By definition, bit positions in \p targets and \p controls arguments should not overlap.
 *
 * This function may return ::CUSTATEVEC_STATUS_INSUFFICIENT_WORKSPACE for large \p nTargets.
 * In such cases, the \p extraWorkspace and \p extraWorkspaceSizeInBytes arguments should be specified
 * to provide extra workspace.  The size of required extra workspace is obtained by
 * calling custatevecApplyMatrixGetWorkspaceSize().
 * A null pointer can be passed to the \p extraWorkspace argument if no extra workspace is
 * required.
 * Also, if a device memory handler is set, the \p extraWorkspace can be set to null, 
 * and the \p extraWorkspaceSizeInBytes can be set to 0.
 */

custatevecStatus_t
custatevecApplyMatrix(custatevecHandle_t          handle,
                      void*                       sv,
                      cudaDataType_t              svDataType,
                      const uint32_t              nIndexBits,
                      const void*                 matrix,
                      cudaDataType_t              matrixDataType,
                      custatevecMatrixLayout_t    layout,
                      const int32_t               adjoint,
                      const int32_t*              targets,
                      const uint32_t              nTargets,
                      const int32_t*              controls,
                      const int32_t*              controlBitValues,
                      const uint32_t              nControls,
                      custatevecComputeType_t     computeType,
                      void*                       extraWorkspace,
                      size_t                      extraWorkspaceSizeInBytes);


/*
 * Expectation
 */

/**
 * \brief This function gets the required workspace size for custatevecComputeExpectation().
 *
 * \param[in] handle the handle to the cuStateVec context
 * \param[in] svDataType Data type of the state vector
 * \param[in] nIndexBits the number of index bits of the state vector
 * \param[in] matrix host or device pointer to a matrix
 * \param[in] matrixDataType data type of matrix
 * \param[in] layout enumerator specifying the memory layout of matrix
 * \param[in] nBasisBits the number of target bits
 * \param[in] computeType computeType of matrix multiplication
 * \param[out] extraWorkspaceSizeInBytes size of the extra workspace
 *
 * \details This function returns the size of the extra workspace required to execute
 * custatevecComputeExpectation().
 * \p extraWorkspaceSizeInBytes will be set to 0 if no extra buffer is required.
 */

custatevecStatus_t
custatevecComputeExpectationGetWorkspaceSize(custatevecHandle_t       handle,
                                             cudaDataType_t           svDataType,
                                             const uint32_t           nIndexBits,
                                             const void*              matrix,
                                             cudaDataType_t           matrixDataType,
                                             custatevecMatrixLayout_t layout,
                                             const uint32_t           nBasisBits,
                                             custatevecComputeType_t  computeType,
                                             size_t*                  extraWorkspaceSizeInBytes);

/**
 * \brief Compute expectation of matrix observable.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[out] expectationValue host pointer to a variable to store an expectation value
 * \param[in] expectationDataType data type of expect
 * \param[out] residualNorm result of matrix type test
 * \param[in] sv state vector
 * \param[in] svDataType data type of the state vector
 * \param[in] nIndexBits the number of index bits of the state vector
 * \param[in] matrix observable as matrix
 * \param[in] matrixDataType data type of matrix
 * \param[in] layout matrix memory layout
 * \param[in] basisBits pointer to a host array of basis index bits
 * \param[in] nBasisBits the number of basis bits
 * \param[in] computeType computeType of matrix multiplication
 * \param[in] extraWorkspace pointer to an extra workspace
 * \param[in] extraWorkspaceSizeInBytes the size of extra workspace
 *
 * \details This function calculates expectation for a given matrix observable.
 * The acceptable values for the \p expectationDataType argument are CUDA_R_64F and CUDA_C_64F.
 *
 * The \p basisBits and \p nBasisBits arguments specify the basis to calculate expectation.  For the
 * \p computeType argument, the same combinations for custatevecApplyMatrix() are
 * available.
 *
 * This function may return ::CUSTATEVEC_STATUS_INSUFFICIENT_WORKSPACE for large \p nBasisBits.
 * In such cases, the \p extraWorkspace and \p extraWorkspaceSizeInBytes arguments should be specified
 * to provide extra workspace. The size of required extra workspace is obtained by
 * calling custatevecComputeExpectationGetWorkspaceSize().
 * A null pointer can be passed to the \p extraWorkspace argument if no extra workspace is
 * required.
 * Also, if a device memory handler is set, the \p extraWorkspace can be set to null, 
 * and the \p extraWorkspaceSizeInBytes can be set to 0.
 *
 * \note The \p residualNorm argument is not available in this version.
 * If a matrix given by the matrix argument may not be a Hermitian matrix,
 * please specify CUDA_C_64F to the \p expectationDataType argument and check the imaginary part of
 * the calculated expectation value.
 */

custatevecStatus_t
custatevecComputeExpectation(custatevecHandle_t       handle,
                             const void*              sv,
                             cudaDataType_t           svDataType,
                             const uint32_t           nIndexBits,
                             void*                    expectationValue,
                             cudaDataType_t           expectationDataType,
                             double*                  residualNorm,
                             const void*              matrix,
                             cudaDataType_t           matrixDataType,
                             custatevecMatrixLayout_t layout,
                             const int32_t*           basisBits,
                             const uint32_t           nBasisBits,
                             custatevecComputeType_t  computeType,
                             void*                    extraWorkspace,
                             size_t                   extraWorkspaceSizeInBytes);


/*
 * Sampler
 */

/**
 * \brief Create sampler descriptor.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] sv pointer to state vector
 * \param[in] svDataType data type of state vector
 * \param[in] nIndexBits the number of index bits of the state vector
 * \param[out] sampler pointer to a new sampler descriptor
 * \param[in] nMaxShots the max number of shots used for this sampler context
 * \param[out] extraWorkspaceSizeInBytes workspace size
 *
 * \details This function creates a sampler descriptor.
 * If an extra workspace is required, its size is set to \p extraWorkspaceSizeInBytes.
 */

custatevecStatus_t 
custatevecSamplerCreate(custatevecHandle_t             handle,
                        const void*                    sv,
                        cudaDataType_t                 svDataType,
                        const uint32_t                 nIndexBits,
                        custatevecSamplerDescriptor_t* sampler,
                        uint32_t                       nMaxShots,
                        size_t*                        extraWorkspaceSizeInBytes);


/**
 * \brief This function releases resources used by the sampler.
 *
 * \param[in] sampler the sampler descriptor
 */
custatevecStatus_t
custatevecSamplerDestroy(custatevecSamplerDescriptor_t sampler);


/**
 * \brief Preprocess the state vector for preparation of sampling.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] sampler the sampler descriptor
 * \param[in] extraWorkspace extra workspace
 * \param[in] extraWorkspaceSizeInBytes size of the extra workspace
 *
 * \details This function prepares internal states of the sampler descriptor.
 * If a device memory handler is set, the \p extraWorkspace can be set to null, 
 * and the \p extraWorkspaceSizeInBytes can be set to 0.
 * Otherwise, a pointer passed to the \p extraWorkspace argument is associated to the sampler handle
 * and should be kept during its life time.
 * The size of \p extraWorkspace is obtained when custatevecSamplerCreate() is called.
 */

custatevecStatus_t
custatevecSamplerPreprocess(custatevecHandle_t             handle,
                            custatevecSamplerDescriptor_t  sampler,
                            void*                          extraWorkspace,
                            const size_t                   extraWorkspaceSizeInBytes);


/**
 * \brief Get the squared norm of the state vector.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] sampler the sampler descriptor
 * \param[out] norm the norm of the state vector
 *
 * \details This function returns the squared norm of the state vector.
 * An intended use case is sampling with multiple devices.
 * This API should be called after custatevecSamplerPreprocess().
 * Otherwise, the behavior of this function is undefined.
 */

custatevecStatus_t
custatevecSamplerGetSquaredNorm(custatevecHandle_t            handle,
                                custatevecSamplerDescriptor_t sampler,
                                double*                       norm);


/**
 * \brief Apply the partial norm and norm to the state vector to the sample descriptor.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] sampler the sampler descriptor
 * \param[in] subSVOrd sub state vector ordinal
 * \param[in] nSubSVs the number of sub state vectors
 * \param[in] offset cumulative sum offset for the sub state vector
 * \param[in] norm norm for all sub vectors
 *
 * \details This function applies offsets assuming the given state vector is a sub state vector.
 * An intended use case is sampling with distributed state vectors.
 * The \p nSubSVs argument should be a power of 2 and \p subSVOrd should be less than \p nSubSVs.
 * Otherwise, this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 */

custatevecStatus_t
custatevecSamplerApplySubSVOffset(custatevecHandle_t            handle,
                                  custatevecSamplerDescriptor_t sampler,
                                  int32_t                       subSVOrd,
                                  uint32_t                      nSubSVs,
                                  double                        offset,
                                  double                        norm);

/**
 * \brief Sample bit strings from the state vector.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] sampler the sampler descriptor
 * \param[out] bitStrings pointer to a host array to store sampled bit strings
 * \param[in] bitOrdering pointer to a host array of bit ordering for sampling
 * \param[in] bitStringLen the number of bits in bitOrdering
 * \param[in] randnums pointer to an array of random numbers
 * \param[in] nShots the number of shots
 * \param[in] output the order of sampled bit strings
 *
 * \details This function does sampling.
 * The \p bitOrdering and \p bitStringLen arguments specify bits to be sampled.
 * Sampled bit strings are represented as an array of ::custatevecIndex_t and
 * are stored to the host memory buffer that the \p bitStrings argument points to.
 *
 * The \p randnums argument is an array of user-generated random numbers whose length is \p nShots.
 * The range of random numbers should be in [0, 1).  A random number given by the \p randnums
 * argument is clipped to [0, 1) if its range is not in [0, 1).
 *
 * The \p output argument specifies the order of sampled bit strings:
 *   - If ::CUSTATEVEC_SAMPLER_OUTPUT_RANDNUM_ORDER is specified,
 * the order of sampled bit strings is the same as that in the \p randnums argument.
 *   - If ::CUSTATEVEC_SAMPLER_OUTPUT_ASCENDING_ORDER is specified, bit strings are returned in the ascending order.
 *
 * This API should be called after custatevecSamplerPreprocess().
 * Otherwise, the behavior of this function is undefined.
 * By calling custatevecSamplerApplySubSVOffset() prior to this function, it is possible to sample bits 
 * corresponding to the ordinal of sub state vector.  
 */

custatevecStatus_t 
custatevecSamplerSample(custatevecHandle_t             handle,
                        custatevecSamplerDescriptor_t  sampler,
                        custatevecIndex_t*             bitStrings,
                        const int32_t*                 bitOrdering,
                        const uint32_t                 bitStringLen,
                        const double*                  randnums,
                        const uint32_t                 nShots,
                        enum custatevecSamplerOutput_t output);



/*
 *  Beta2
 */


/**
 * \brief Get the extra workspace size required by custatevecApplyGeneralizedPermutationMatrix().
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] svDataType data type of the state vector
 * \param[in] nIndexBits the number of index bits of the state vector
 * \param[in] permutation host or device pointer to a permutation table
 * \param[in] diagonals host or device pointer to diagonal elements
 * \param[in] diagonalsDataType data type of diagonals
 * \param[in] targets pointer to a host array of target bits
 * \param[in] nTargets the number of target bits
 * \param[in] nControls the number of control bits
 * \param[out] extraWorkspaceSizeInBytes extra workspace size
 *
 * \details This function gets the size of extra workspace size required to execute
 * custatevecApplyGeneralizedPermutationMatrix().
 * \p extraWorkspaceSizeInBytes will be set to 0 if no extra buffer is required
 * for a given set of arguments.
 */

custatevecStatus_t
custatevecApplyGeneralizedPermutationMatrixGetWorkspaceSize(custatevecHandle_t        handle,
                                                            cudaDataType_t            svDataType,
                                                            const uint32_t            nIndexBits,
                                                            const custatevecIndex_t*  permutation,
                                                            const void*               diagonals,
                                                            cudaDataType_t            diagonalsDataType,
                                                            const int32_t*            targets,
                                                            const uint32_t            nTargets,
                                                            const uint32_t            nControls,
                                                            size_t*                   extraWorkspaceSizeInBytes);


/**
 * \brief Apply generalized permutation matrix.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] sv state vector
 * \param[in] svDataType data type of the state vector
 * \param[in] nIndexBits the number of index bits of the state vector
 * \param[in] permutation host or device pointer to a permutation table
 * \param[in] diagonals host or device pointer to diagonal elements
 * \param[in] diagonalsDataType data type of diagonals
 * \param[in] adjoint apply adjoint of generalized permutation matrix
 * \param[in] targets pointer to a host array of target bits
 * \param[in] nTargets the number of target bits
 * \param[in] controls pointer to a host array of control bits
 * \param[in] controlBitValues pointer to a host array of control bit values
 * \param[in] nControls the number of control bits
 * \param[in] extraWorkspace extra workspace
 * \param[in] extraWorkspaceSizeInBytes extra workspace size
 *
 * \details This function applies the generalized permutation matrix.
 *
 * The generalized permutation matrix, \f$A\f$, is expressed as \f$A = DP\f$,
 * where \f$D\f$ and \f$P\f$ are diagonal and permutation matrices, respectively.
 *
 * The permutation matrix, \f$P\f$, is specified as a permutation table which is an array of
 * ::custatevecIndex_t and passed to the \p permutation argument.
 *
 * The diagonal matrix, \f$D\f$, is specified as an array of diagonal elements.
 * The length of both arrays is \f$ 2^{{\text nTargets}} \f$.
 * The \p diagonalsDataType argument specifies the type of diagonal elements.
 *
 * Below is the table of combinations of \p svDataType and \p diagonalsDataType arguments available in
 * this version.
 *
 *  \p svDataType  | \p diagonalsDataType
 *  ---------------|---------------------
 *  CUDA_C_F64     | CUDA_C_F64
 *  CUDA_C_F32     | CUDA_C_F64
 *  CUDA_C_F32     | CUDA_C_F32
 *
 * This function can also be used to only apply either the diagonal or the permutation matrix.
 * By passing a null pointer to the \p permutation argument, \f$P\f$ is treated as an identity matrix,
 * thus, only the diagonal matrix \f$D\f$ is applied. Likewise, if a null pointer is passed to the \p diagonals
 * argument, \f$D\f$ is treated as an identity matrix, and only the permutation matrix \f$P\f$ is applied.
 *
 * The permutation argument should hold integers in [0, \f$ 2^{nTargets} \f$).  An integer should appear
 * only once, otherwise the behavior of this function is undefined.
 *
 * The \p permutation and \p diagonals arguments should not be null at the same time.
 * In this case, this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 *
 * This function may return ::CUSTATEVEC_STATUS_INSUFFICIENT_WORKSPACE for large \p nTargets or
 * \p nIndexBits.  In such cases, the \p extraWorkspace and \p extraWorkspaceSizeInBytes arguments should be
 * specified to provide extra workspace.  The size of required extra workspace is obtained by
 * calling custatevecApplyGeneralizedPermutationMatrixGetWorkspaceSize().
 *
 * A null pointer can be passed to the \p extraWorkspace argument if no extra workspace is
 * required.
 * Also, if a device memory handler is set, the \p extraWorkspace can be set to null, 
 * and the \p extraWorkspaceSizeInBytes can be set to 0.
 *
 * \note In this version, custatevecApplyGeneralizedPermutationMatrix() does not return error if an
 * invalid \p permutation argument is specified.
 */

custatevecStatus_t
custatevecApplyGeneralizedPermutationMatrix(custatevecHandle_t       handle,
                                            void*                    sv,
                                            cudaDataType_t           svDataType,
                                            const uint32_t           nIndexBits,
                                            custatevecIndex_t*       permutation,
                                            const void*              diagonals,
                                            cudaDataType_t           diagonalsDataType,
                                            const int32_t            adjoint,
                                            const int32_t*           targets,
                                            const uint32_t           nTargets,
                                            const int32_t*           controls,
                                            const int32_t*           controlBitValues,
                                            const uint32_t           nControls,
                                            void*                    extraWorkspace,
                                            size_t                   extraWorkspaceSizeInBytes);


/**
 * \brief Calculate expectation values for a batch of (multi-qubit) Pauli operators.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] sv state vector
 * \param[in] svDataType data type of the state vector
 * \param[in] nIndexBits the number of index bits of the state vector
 * \param[out] expectationValues pointer to a host array to store expectation values
 * \param[in] pauliOperatorsArray pointer to a host array of Pauli operator arrays
 * \param[in] nPauliOperatorArrays the number of Pauli operator arrays
 * \param[in] basisBitsArray host array of basis bit arrays
 * \param[in] nBasisBitsArray host array of the number of basis bits
 *
 * This function calculates multiple expectation values for given sequences of
 * Pauli operators by a single call.
 *
 * A single Pauli operator sequence, pauliOperators, is represented by using an array
 * of ::custatevecPauli_t. The basis bits on which these Pauli operators are acting are
 * represented by an array of index bit positions. If no Pauli operator is specified
 * for an index bit, the identity operator (::CUSTATEVEC_PAULI_I) is implicitly assumed.
 *
 * The length of pauliOperators and basisBits are the same and specified by nBasisBits.
 *
 * The number of Pauli operator sequences is specified by the \p nPauliOperatorArrays argument.
 *
 * Multiple sequences of Pauli operators are represented in the form of arrays of arrays
 * in the following manners:
 *   - The \p pauliOperatorsArray argument is an array for arrays of ::custatevecPauli_t.
 *   - The \p basisBitsArray is an array of the arrays of basis bit positions.
 *   - The \p nBasisBitsArray argument holds an array of the length of Pauli operator sequences and
 *     basis bit arrays.
 *
 * Calculated expectation values are stored in a host buffer specified by the \p expectationValues
 * argument of length \p nPauliOpeartorsArrays.
 *
 * This function returns ::CUSTATEVEC_STATUS_INVALID_VALUE if basis bits specified
 * for a Pauli operator sequence has duplicates and/or out of the range of [0, \p nIndexBits).
 *
 * This function accepts empty Pauli operator sequence to get the norm of the state vector.
 */

custatevecStatus_t
custatevecComputeExpectationsOnPauliBasis(custatevecHandle_t        handle,
                                          const void*               sv,
                                          cudaDataType_t            svDataType,
                                          const uint32_t            nIndexBits,
                                          double*                   expectationValues,
                                          const custatevecPauli_t** pauliOperatorsArray,
                                          const uint32_t            nPauliOperatorArrays,
                                          const int32_t**           basisBitsArray,
                                          const uint32_t*           nBasisBitsArray);


/**
 * \brief Create accessor to copy elements between the state vector and an external buffer.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] sv state vector
 * \param[in] svDataType Data type of state vector
 * \param[in] nIndexBits the number of index bits of state vector
 * \param[in] accessor pointer to an accessor descriptor
 * \param[in] bitOrdering pointer to a host array to specify the basis bits of the external buffer
 * \param[in] bitOrderingLen the length of bitOrdering
 * \param[in] maskBitString pointer to a host array to specify the mask values to limit access
 * \param[in] maskOrdering pointer to a host array for the mask ordering
 * \param[in] maskLen the length of mask
 * \param[out] extraWorkspaceSizeInBytes the required size of extra workspace
 *
 * Accessor copies state vector elements between the state vector and external buffers.
 * During the copy, the ordering of state vector elements are rearranged according to the bit
 * ordering specified by the \p bitOrdering argument.
 *
 * The state vector is assumed to have the default ordering: the LSB is the 0th index bit and the
 * (N-1)th index bit is the MSB for an N index bit system.  The bit ordering of the external
 * buffer is specified by the \p bitOrdering argument.
 * When 3 is given to the \p nIndexBits argument and [1, 2, 0] to the \p bitOrdering argument,
 * the state vector index bits are permuted to specified bit positions.  Thus, the state vector
 * index is rearranged and mapped to the external buffer index as [0, 4, 1, 5, 2, 6, 3, 7].
 *
 * The \p maskBitString, \p maskOrdering and \p maskLen arguments specify the bit mask for the state
 * vector index being accessed.
 * If the \p maskLen argument is 0, the \p maskBitString and/or \p maskOrdering arguments can be null.
 *
 * All bit positions [0, \p nIndexBits), should appear exactly once, either in the \p bitOrdering or the
 * \p maskOrdering arguments.
 * If a bit position does not appear in these arguments and/or there are overlaps of bit positions,
 * this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 *
 * The extra workspace improves performance if the accessor is called multiple times with 
 * small external buffers placed on device.
 * A null pointer can be specified to the \p extraWorkspaceSizeInBytes if the extra workspace is not
 * necessary.
 */
custatevecStatus_t
custatevecAccessorCreate(custatevecHandle_t              handle,
                         void*                           sv,
                         cudaDataType_t                  svDataType,
                         const uint32_t                  nIndexBits,
                         custatevecAccessorDescriptor_t* accessor,
                         const int32_t*                  bitOrdering,
                         const uint32_t                  bitOrderingLen,
                         const int32_t*                  maskBitString,
                         const int32_t*                  maskOrdering,
                         const uint32_t                  maskLen,
                         size_t*                         extraWorkspaceSizeInBytes);


/**
 * \brief Create accessor for the constant state vector
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] sv state vector
 * \param[in] svDataType Data type of state vector
 * \param[in] nIndexBits the number of index bits of state vector
 * \param[in] accessor pointer to an accessor descriptor
 * \param[in] bitOrdering pointer to a host array to specify the basis bits of the external buffer
 * \param[in] bitOrderingLen the length of bitOrdering
 * \param[in] maskBitString pointer to a host array to specify the mask values to limit access
 * \param[in] maskOrdering pointer to a host array for the mask ordering
 * \param[in] maskLen the length of mask
 * \param[out] extraWorkspaceSizeInBytes the required size of extra workspace
 *
 * This function is the same as custatevecAccessorCreate(), but only accepts the constant
 * state vector.
 */

custatevecStatus_t
custatevecAccessorCreateView(custatevecHandle_t              handle,
                             const void*                     sv,
                             cudaDataType_t                  svDataType,
                             const uint32_t                  nIndexBits,
                             custatevecAccessorDescriptor_t* accessor,
                             const int32_t*                  bitOrdering,
                             const uint32_t                  bitOrderingLen,
                             const int32_t*                  maskBitString,
                             const int32_t*                  maskOrdering,
                             const uint32_t                  maskLen,
                             size_t*                         extraWorkspaceSizeInBytes);


/**
 * \brief This function releases resources used by the accessor.
 *
 * \param[in] accessor the accessor descriptor
 */
custatevecStatus_t
custatevecAccessorDestroy(custatevecAccessorDescriptor_t accessor);


/**
 * \brief Set the external workspace to the accessor
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] accessor the accessor descriptor
 * \param[in] extraWorkspace extra workspace
 * \param[in] extraWorkspaceSizeInBytes extra workspace size
 *
 * This function sets the extra workspace to the accessor.
 * The required size for extra workspace can be obtained by custatevecAccessorCreate() or custatevecAccessorCreateView().
 * if a device memory handler is set, the \p extraWorkspace can be set to null, 
 * and the \p extraWorkspaceSizeInBytes can be set to 0.
 */

custatevecStatus_t
custatevecAccessorSetExtraWorkspace(custatevecHandle_t              handle,
                                    custatevecAccessorDescriptor_t  accessor,
                                    void*                           extraWorkspace,
                                    size_t                          extraWorkspaceSizeInBytes);


/**
 * \brief Copy state vector elements to an external buffer
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] accessor the accessor descriptor
 * \param[out] externalBuffer pointer to  a host or device buffer to receive copied elements
 * \param[in] begin index in the permuted bit ordering for the first elements being copied to the state vector
 * \param[in] end index in the permuted bit ordering for the last elements being copied to the state vector (non-inclusive)
 *
 * This function copies state vector elements to an external buffer specified by
 * the \p externalBuffer argument.  During the copy, the index bit is permuted as specified by
 * the \p bitOrdering argument in custatevecAccessorCreate() or custatevecAccessorCreateView().
 *
 * The \p begin and \p end arguments specify the range of state vector elements being copied.
 * Both arguments have the bit ordering specified by the \p bitOrdering argument.
 */

custatevecStatus_t
custatevecAccessorGet(custatevecHandle_t              handle,
                      custatevecAccessorDescriptor_t  accessor,
                      void*                           externalBuffer,
                      const custatevecIndex_t         begin,
                      const custatevecIndex_t         end);

/**
 * \brief Set state vector elements from an external buffer
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] accessor the accessor descriptor
 * \param[in] externalBuffer pointer to a host or device buffer of complex values being copied to the state vector
 * \param[in] begin index in the permuted bit ordering for the first elements being copied from the state vector
 * \param[in] end index in the permuted bit ordering for the last elements being copied from the state vector (non-inclusive)
 *
 * This function sets complex numbers to the state vector by using an external buffer specified by
 * the \p externalBuffer argument.  During the copy, the index bit is permuted as specified by
 * the \p bitOrdering argument in custatevecAccessorCreate().
 *
 * The \p begin and \p end arguments specify the range of state vector elements being set
 * to the state vector. Both arguments have the bit ordering specified by the \p bitOrdering
 * argument.
 *
 * If a read-only accessor created by calling custatevecAccessorCreateView() is provided, this
 * function returns ::CUSTATEVEC_STATUS_NOT_SUPPORTED.
 */

custatevecStatus_t
custatevecAccessorSet(custatevecHandle_t              handle,
                      custatevecAccessorDescriptor_t  accessor,
                      const void*                     externalBuffer,
                      const custatevecIndex_t         begin,
                      const custatevecIndex_t         end);

/**
 * \brief Swap index bits and reorder state vector elements in one device
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] sv state vector
 * \param[in] svDataType Data type of state vector
 * \param[in] nIndexBits the number of index bits of state vector
 * \param[in] bitSwaps pointer to a host array of swapping bit index pairs
 * \param[in] nBitSwaps the number of bit swaps
 * \param[in] maskBitString pointer to a host array to mask output
 * \param[in] maskOrdering  pointer to a host array to specify the ordering of maskBitString
 * \param[in] maskLen the length of mask
 * 
 * This function updates the bit ordering of the state vector by swapping the pairs of bit positions.
 * 
 * The state vector is assumed to have the default ordering: the LSB is the 0th index bit and the
 * (N-1)th index bit is the MSB for an N index bit system. 
 * The \p bitSwaps argument specifies the swapped bit index pairs, whose values must be in the range
 * [0, \p nIndexBits).
 *
 * The \p maskBitString, \p maskOrdering and \p maskLen arguments specify the bit mask for the state
 * vector index being permuted.
 * If the \p maskLen argument is 0, the \p maskBitString and/or \p maskOrdering arguments can be null.
 * 
 * A bit position can be included in both \p bitSwaps and \p maskOrdering.
 * When a masked bit is swapped, state vector elements whose original indices match the mask bit string 
 * are written to the permuted indices while other elements are not copied.
 */

custatevecStatus_t
custatevecSwapIndexBits(custatevecHandle_t handle,
                        void*              sv,
                        cudaDataType_t     svDataType,
                        const uint32_t     nIndexBits,
                        const int2*        bitSwaps,
                        const uint32_t     nBitSwaps,
                        const int32_t*     maskBitString,
                        const int32_t*     maskOrdering,
                        const uint32_t     maskLen);

/*
 * Matrix type test
 */

/**
 * \brief Get extra workspace size for custatevecTestMatrixType()
 *
 * \param[in] handle the handle to cuStateVec library
 * \param[in] matrix host or device pointer to a matrix
 * \param[in] matrixType matrix type
 * \param[in] matrixDataType data type of matrix
 * \param[in] layout enumerator specifying the memory layout of matrix
 * \param[in] nTargets the number of target bits, up to 15
 * \param[in] adjoint flag to control whether the adjoint of matrix is tested
 * \param[in] computeType compute type
 * \param[out] extraWorkspaceSizeInBytes workspace size
 *
 * \details This function gets the size of an extra workspace required to execute
 * custatevecTestMatrixType().
 * \p extraWorkspaceSizeInBytes will be set to 0 if no extra buffer is required.
 */

custatevecStatus_t
custatevecTestMatrixTypeGetWorkspaceSize(custatevecHandle_t       handle,
                                         custatevecMatrixType_t   matrixType,
                                         const void*              matrix,
                                         cudaDataType_t           matrixDataType,
                                         custatevecMatrixLayout_t layout,
                                         const uint32_t           nTargets,
                                         const int32_t            adjoint,
                                         custatevecComputeType_t  computeType,
                                         size_t*                  extraWorkspaceSizeInBytes);

/**
 * \brief Test the deviation of a given matrix from a Hermitian (or Unitary) matrix.
 *
 * \param[in] handle the handle to cuStateVec library
 * \param[out] residualNorm host pointer, to store the deviation from certain matrix type
 * \param[in] matrixType matrix type
 * \param[in] matrix host or device pointer to a matrix
 * \param[in] matrixDataType data type of matrix
 * \param[in] layout enumerator specifying the memory layout of matrix
 * \param[in] nTargets the number of target bits, up to 15
 * \param[in] adjoint flag to control whether the adjoint of matrix is tested
 * \param[in] computeType compute type
 * \param[in] extraWorkspace extra workspace
 * \param[in] extraWorkspaceSizeInBytes extra workspace size
 *
 * \details This function tests if the type of a given matrix matches the type given by
 * the \p matrixType argument.
 *
 * For tests for the unitary type, \f$ R = (AA^{\dagger} - I) \f$ is calculated where \f$ A \f$ is the given matrix.
 * The sum of absolute values of \f$ R \f$ matrix elements is returned.
 *
 * For tests for the Hermitian type, \f$ R = (M - M^{\dagger}) / 2 \f$ is calculated. The sum of squared
 * absolute values of \f$ R \f$ matrix elements is returned.
 *
 * This function may return ::CUSTATEVEC_STATUS_INSUFFICIENT_WORKSPACE for large \p nTargets.
 * In such cases, the \p extraWorkspace and \p extraWorkspaceSizeInBytes arguments should be specified
 * to provide extra workspace.
 * The required size of an extra workspace is obtained by calling custatevecTestMatrixTypeGetWorkspaceSize().
 * A null pointer can be passed to the \p extraWorkspace argument if no extra workspace is required.
 * Also, if a device memory handler is set, the \p extraWorkspace can be set to null, 
 * and the \p extraWorkspaceSizeInBytes can be set to 0.
 * 
 * \note The \p nTargets argument must be no more than 15 in this version.
 * For larger \p nTargets, this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 */

custatevecStatus_t
custatevecTestMatrixType(custatevecHandle_t       handle,
                         double*                  residualNorm,
                         custatevecMatrixType_t   matrixType,
                         const void*              matrix,
                         cudaDataType_t           matrixDataType,
                         custatevecMatrixLayout_t layout,
                         const uint32_t           nTargets,
                         const int32_t            adjoint,
                         custatevecComputeType_t  computeType,
                         void*                    extraWorkspace,
                         size_t                   extraWorkspaceSizeInBytes);

/** \} singlegpuapi */

/**
 * \defgroup multigpuapi Multi GPU API
 *
 * \{ */

/**
 * \brief Swap index bits and reorder state vector elements for multiple sub state vectors
 *        distributed to multiple devices
 *
 * \param[in] handles pointer to a host array of custatevecHandle_t
 * \param[in] nHandles the number of handles specified in the handles argument
 * \param[in,out] subSVs pointer to an array of sub state vectors
 * \param[in] svDataType the data type of the state vector specified by the subSVs argument
 * \param[in] nGlobalIndexBits the number of global index bits of distributed state vector
 * \param[in] nLocalIndexBits the number of local index bits in sub state vector
 * \param[in] indexBitSwaps pointer to a host array of index bit pairs being swaped
 * \param[in] nIndexBitSwaps the number of index bit swaps
 * \param[in] maskBitString pointer to a host array to mask output
 * \param[in] maskOrdering  pointer to a host array to specify the ordering of maskBitString
 * \param[in] maskLen the length of mask
 * \param[in] deviceNetworkType the device network topology
 *
 * This function updates the bit ordering of the state vector distributed in multiple devices
 *  by swapping the pairs of bit positions.
 *
 * This function assumes the state vector is split into multiple sub state vectors and distributed
 *  to multiple devices to represent a (\p nGlobalIndexBits + \p nLocalIndexBits) qubit system.
 *
 * The \p handles argument should receive cuStateVec handles created for all devices where sub
 *  state vectors are allocated. If two or more cuStateVec handles created for the same device are
 *  given, this function will return an error, ::CUSTATEVEC_STATUS_INVALID_VALUE.
 * The \p handles argument should contain a handle created on the current device, as all operations
 *  in this function will be ordered on the stream of the current device's handle.
 *  Otherwise, this function returns an error, ::CUSTATEVEC_STATUS_INVALID_VALUE.
 *
 * Sub state vectors are specified by the \p subSVs argument as an array of device pointers.
 *  All sub state vectors are assumed to hold the same number of index bits specified by the \p
 *  nLocalIndexBits. Thus, each sub state vectors holds (1 << \p nLocalIndexBits) state vector
 *  elements. The global index bits is identical to the index of sub state vectors.  The number
 *  of sub state vectors is given as (1 << \p nGlobalIndexBits). The max value of
 *  \p nGlobalIndexBits is 5, which corresponds to 32 sub state vectors.
 *
 * The index bit of the distributed state vector has the default ordering: The index bits of the
 *  sub state vector are mapped from the 0th index bit to the (\p nLocalIndexBits-1)-th index bit.
 *  The global index bits are mapped from the (\p nLocalIndexBits)-th bit to the
 *  (\p nGlobalIndexBits + \p nLocalIndexBits - 1)-th bit.
 *
 * The \p indexBitSwaps argument specifies the index bit pairs being swapped. Each index bit pair
 *  can be a pair of two global index bits or a pair of a global and a local index bit.
 *  Any pair of two local index bits is not accepted. Please use custatevecSwapIndexBits()
 *  for swapping local index bits.
 *
 * The \p maskBitString, \p maskOrdering and \p maskLen arguments specify the bit string mask that
 *  limits the state vector elements swapped during the call.
 *  Bits in \p maskOrdering can overlap index bits specified in the \p indexBitSwaps argument.
 *  In such cases, the mask bit string is applied for the bit positions before index bit swaps.
 *  If the \p maskLen argument is 0, the \p maskBitString and/or \p maskOrdering arguments can be
 *  null.
 *
 * The \p deviceNetworkType argument specifies the device network topology to optimize the data
 *  transfer sequence. The following two network topologies are assumed:
 *  - Switch network: devices connected via NVLink with an NVSwitch (ex. DGX A100 and DGX-2) or
 *    PCIe device network with a single PCIe switch
 *  - Full mesh network: all devices are connected by full mesh connections
 *    (ex. DGX Station V100/A100)
 *
 * \note **Important notice**
 * This function assumes \em bidirectional GPUDirect P2P is supported and enabled by
 *  ``cudaDeviceEnablePeerAccess()`` between all devices where sub state vectors are allocated.
 *  If GPUDirect P2P is not enabled, the call to ``custatevecMultiDeviceSwapIndexBits()`` that
 *  accesses otherwise inaccessible device memory allocated in other GPUs would result in a
 *  segmentation fault.
 *
 * \note
 * For the best performance, please use \f$2^n\f$ number of devices and allocate one sub state vector
 *  in each device. This function allows to use non-\f$2^n\f$ number of devices, to allocate two or
 *  more sub state vectors on a device, or to allocate all sub state vectors on a single device
 *  to cover various hardware configurations. However, the performance is always the best when
 *  a single sub state vector is allocated on each \f$2^n\f$ number of devices.
 *
 * \note
 * The copy on each participating device is enqueued on the CUDA stream bound to the corresponding
 *  handle via custatevecSetStream().
 *  All CUDA calls before the call of this function are correctly ordered if these calls are issued
 *  on the streams set to \p handles. This function is asynchronously executed. Please use
 *  `cudaStreamSynchronize()` (for synchronization) or `cudaStreamWaitEvent()` (for establishing
 *  the stream order) with the stream set to the handle of the current device.
 */

custatevecStatus_t
custatevecMultiDeviceSwapIndexBits(custatevecHandle_t*                 handles,
                                   const uint32_t                      nHandles,
                                   void**                              subSVs,
                                   const cudaDataType_t                svDataType,
                                   const uint32_t                      nGlobalIndexBits,
                                   const uint32_t                      nLocalIndexBits,
                                   const int2*                         indexBitSwaps,
                                   const uint32_t                      nIndexBitSwaps,
                                   const int32_t*                      maskBitString,
                                   const int32_t*                      maskOrdering,
                                   const uint32_t                      maskLen,
                                   const custatevecDeviceNetworkType_t deviceNetworkType);

/** \} multigpuapi */

#if defined(__cplusplus)
} // extern "C"
#endif // defined(__cplusplus)
