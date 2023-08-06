"""Python wrappers around TensorFlow ops.

This file is MACHINE GENERATED! Do not edit.
"""

import collections

from tensorflow.python import pywrap_tfe as pywrap_tfe
from tensorflow.python.eager import context as _context
from tensorflow.python.eager import core as _core
from tensorflow.python.eager import execute as _execute
from tensorflow.python.framework import dtypes as _dtypes

from tensorflow.python.framework import op_def_registry as _op_def_registry
from tensorflow.python.framework import ops as _ops
from tensorflow.python.framework import op_def_library as _op_def_library
from tensorflow.python.util.deprecation import deprecated_endpoints
from tensorflow.python.util import dispatch as _dispatch
from tensorflow.python.util.tf_export import tf_export

from typing import TypeVar

def uniform_dequantize(input, scales, zero_points, Tout, quantization_min_val, quantization_max_val, quantization_axis=-1, name=None):
  r"""Perform dequantization on the quantized Tensor `input`.

  Given quantized `input` which was quantized using `scales` and `zero_points`, performs dequantization using the formula:
  dequantized_data = (quantized_data - zero_point) * scale.

  Args:
    input: A `Tensor`. Must be one of the following types: `qint8`, `qint32`.
      Must be a Tensor of Tin.
    scales: A `Tensor` of type `float32`.
      The float value(s) used as scale(s) when quantizing original data that input represents.
      Must be a scalar Tensor if quantization_axis is -1 (per-tensor quantization), otherwise 1D Tensor of size (input.dim_size(quantization_axis),) (per-axis quantization).
    zero_points: A `Tensor` of type `int32`.
      The int32 value(s) used as zero_point(s) when quantizing original data that input represents.
      Same shape condition as scales.
    Tout: A `tf.DType` from: `tf.float32`.
      The type of output Tensor. A tf.DType from: tf.qint8, tf.qint32
    quantization_min_val: An `int`.
      The quantization min value that was used when input was quantized.
      The purpose of this attribute is typically (but not limited to) to indicate narrow range, where this is set to:
      `(Tin lowest) + 1` if narrow range, and `(Tin lowest)` otherwise.
      For example, if Tin is qint8, this is set to -127 if narrow range quantized or -128 if not.
    quantization_max_val: An `int`.
      The quantization max value that was used when input was quantized.
      The purpose of this attribute is typically (but not limited to) indicate narrow range, where this is set to:
      `(Tout max)` for both narrow range and not narrow range.
      For example, if Tin is qint8, this is set to 127.
    quantization_axis: An optional `int`. Defaults to `-1`.
      Indicates the dimension index of the tensor where per-axis quantization is applied for the slices along that dimension.
      If set to -1 (default), this indicates per-tensor quantization. Otherwise, it must be set within range [0, input.dims()).
    name: A name for the operation (optional).

  Returns:
    A `Tensor` of type `Tout`.
  """
  _ctx = _context._context or _context.context()
  tld = _ctx._thread_local_data
  if tld.is_eager:
    try:
      _result = pywrap_tfe.TFE_Py_FastPathExecute(
        _ctx, "UniformDequantize", name, input, scales, zero_points, "Tout",
        Tout, "quantization_axis", quantization_axis, "quantization_min_val",
        quantization_min_val, "quantization_max_val", quantization_max_val)
      return _result
    except _core._NotOkStatusException as e:
      _ops.raise_from_not_ok_status(e, name)
    except _core._FallbackException:
      pass
    try:
      return uniform_dequantize_eager_fallback(
          input, scales, zero_points, Tout=Tout,
          quantization_axis=quantization_axis,
          quantization_min_val=quantization_min_val,
          quantization_max_val=quantization_max_val, name=name, ctx=_ctx)
    except _core._SymbolicException:
      pass  # Add nodes to the TensorFlow graph.
  # Add nodes to the TensorFlow graph.
  Tout = _execute.make_type(Tout, "Tout")
  quantization_min_val = _execute.make_int(quantization_min_val, "quantization_min_val")
  quantization_max_val = _execute.make_int(quantization_max_val, "quantization_max_val")
  if quantization_axis is None:
    quantization_axis = -1
  quantization_axis = _execute.make_int(quantization_axis, "quantization_axis")
  _, _, _op, _outputs = _op_def_library._apply_op_helper(
        "UniformDequantize", input=input, scales=scales,
                             zero_points=zero_points, Tout=Tout,
                             quantization_min_val=quantization_min_val,
                             quantization_max_val=quantization_max_val,
                             quantization_axis=quantization_axis, name=name)
  _result = _outputs[:]
  if _execute.must_record_gradient():
    _attrs = ("Tin", _op._get_attr_type("Tin"), "Tout",
              _op._get_attr_type("Tout"), "quantization_axis",
              _op._get_attr_int("quantization_axis"), "quantization_min_val",
              _op._get_attr_int("quantization_min_val"),
              "quantization_max_val",
              _op._get_attr_int("quantization_max_val"))
    _inputs_flat = _op.inputs
    _execute.record_gradient(
        "UniformDequantize", _inputs_flat, _attrs, _result)
  _result, = _result
  return _result

UniformDequantize = tf_export("raw_ops.UniformDequantize")(_ops.to_raw_op(uniform_dequantize))


def uniform_dequantize_eager_fallback(input, scales, zero_points, Tout, quantization_min_val, quantization_max_val, quantization_axis, name, ctx):
  Tout = _execute.make_type(Tout, "Tout")
  quantization_min_val = _execute.make_int(quantization_min_val, "quantization_min_val")
  quantization_max_val = _execute.make_int(quantization_max_val, "quantization_max_val")
  if quantization_axis is None:
    quantization_axis = -1
  quantization_axis = _execute.make_int(quantization_axis, "quantization_axis")
  _attr_Tin, (input,) = _execute.args_to_matching_eager([input], ctx, [_dtypes.qint8, _dtypes.qint32, ])
  scales = _ops.convert_to_tensor(scales, _dtypes.float32)
  zero_points = _ops.convert_to_tensor(zero_points, _dtypes.int32)
  _inputs_flat = [input, scales, zero_points]
  _attrs = ("Tin", _attr_Tin, "Tout", Tout, "quantization_axis",
  quantization_axis, "quantization_min_val", quantization_min_val,
  "quantization_max_val", quantization_max_val)
  _result = _execute.execute(b"UniformDequantize", 1, inputs=_inputs_flat,
                             attrs=_attrs, ctx=ctx, name=name)
  if _execute.must_record_gradient():
    _execute.record_gradient(
        "UniformDequantize", _inputs_flat, _attrs, _result)
  _result, = _result
  return _result


def uniform_quantize(input, scales, zero_points, Tout, quantization_min_val, quantization_max_val, quantization_axis=-1, name=None):
  r"""Perform quantization on Tensor `input`.

  Given `input`, `scales` and `zero_points`, performs quantization using the formula:
  quantized_data = floor(input_data * (1.0f / scale) + 0.5f) + zero_point

  Args:
    input: A `Tensor`. Must be one of the following types: `float32`.
      Must be a Tensor of Tin.
    scales: A `Tensor` of type `float32`.
      The float value(s) to use as scale(s) to quantize `input`.
      Must be a scalar Tensor if quantization_axis is -1 (per-tensor quantization), otherwise 1D Tensor of size (input.dim_size(quantization_axis),) (per-axis quantization).
    zero_points: A `Tensor` of type `int32`.
      The int32 value(s) to use as zero_point(s) to quantize `input`.
      Same shape condition as scales.
    Tout: A `tf.DType` from: `tf.qint8, tf.qint32`.
      The type of output Tensor. A tf.DType from: tf.float32
    quantization_min_val: An `int`.
      The quantization min value to quantize `input`.
      The purpose of this attribute is typically (but not limited to) to indicate narrow range, where this is set to:
      `(Tin lowest) + 1` if narrow range, and `(Tin lowest)` otherwise.
      For example, if Tin is qint8, this is set to -127 if narrow range quantized or -128 if not.
    quantization_max_val: An `int`.
      The quantization max value to quantize `input`.
      The purpose of this attribute is typically (but not limited to) indicate narrow range, where this is set to:
      `(Tout max)` for both narrow range and not narrow range.
      For example, if Tin is qint8, this is set to 127.
    quantization_axis: An optional `int`. Defaults to `-1`.
      Indicates the dimension index of the tensor where per-axis quantization is applied for the slices along that dimension.
      If set to -1 (default), this indicates per-tensor quantization. Otherwise, it must be set within range [0, input.dims()).
    name: A name for the operation (optional).

  Returns:
    A `Tensor` of type `Tout`.
  """
  _ctx = _context._context or _context.context()
  tld = _ctx._thread_local_data
  if tld.is_eager:
    try:
      _result = pywrap_tfe.TFE_Py_FastPathExecute(
        _ctx, "UniformQuantize", name, input, scales, zero_points, "Tout",
        Tout, "quantization_axis", quantization_axis, "quantization_min_val",
        quantization_min_val, "quantization_max_val", quantization_max_val)
      return _result
    except _core._NotOkStatusException as e:
      _ops.raise_from_not_ok_status(e, name)
    except _core._FallbackException:
      pass
    try:
      return uniform_quantize_eager_fallback(
          input, scales, zero_points, Tout=Tout,
          quantization_axis=quantization_axis,
          quantization_min_val=quantization_min_val,
          quantization_max_val=quantization_max_val, name=name, ctx=_ctx)
    except _core._SymbolicException:
      pass  # Add nodes to the TensorFlow graph.
  # Add nodes to the TensorFlow graph.
  Tout = _execute.make_type(Tout, "Tout")
  quantization_min_val = _execute.make_int(quantization_min_val, "quantization_min_val")
  quantization_max_val = _execute.make_int(quantization_max_val, "quantization_max_val")
  if quantization_axis is None:
    quantization_axis = -1
  quantization_axis = _execute.make_int(quantization_axis, "quantization_axis")
  _, _, _op, _outputs = _op_def_library._apply_op_helper(
        "UniformQuantize", input=input, scales=scales,
                           zero_points=zero_points, Tout=Tout,
                           quantization_min_val=quantization_min_val,
                           quantization_max_val=quantization_max_val,
                           quantization_axis=quantization_axis, name=name)
  _result = _outputs[:]
  if _execute.must_record_gradient():
    _attrs = ("Tin", _op._get_attr_type("Tin"), "Tout",
              _op._get_attr_type("Tout"), "quantization_axis",
              _op._get_attr_int("quantization_axis"), "quantization_min_val",
              _op._get_attr_int("quantization_min_val"),
              "quantization_max_val",
              _op._get_attr_int("quantization_max_val"))
    _inputs_flat = _op.inputs
    _execute.record_gradient(
        "UniformQuantize", _inputs_flat, _attrs, _result)
  _result, = _result
  return _result

UniformQuantize = tf_export("raw_ops.UniformQuantize")(_ops.to_raw_op(uniform_quantize))


def uniform_quantize_eager_fallback(input, scales, zero_points, Tout, quantization_min_val, quantization_max_val, quantization_axis, name, ctx):
  Tout = _execute.make_type(Tout, "Tout")
  quantization_min_val = _execute.make_int(quantization_min_val, "quantization_min_val")
  quantization_max_val = _execute.make_int(quantization_max_val, "quantization_max_val")
  if quantization_axis is None:
    quantization_axis = -1
  quantization_axis = _execute.make_int(quantization_axis, "quantization_axis")
  _attr_Tin, (input,) = _execute.args_to_matching_eager([input], ctx, [_dtypes.float32, ])
  scales = _ops.convert_to_tensor(scales, _dtypes.float32)
  zero_points = _ops.convert_to_tensor(zero_points, _dtypes.int32)
  _inputs_flat = [input, scales, zero_points]
  _attrs = ("Tin", _attr_Tin, "Tout", Tout, "quantization_axis",
  quantization_axis, "quantization_min_val", quantization_min_val,
  "quantization_max_val", quantization_max_val)
  _result = _execute.execute(b"UniformQuantize", 1, inputs=_inputs_flat,
                             attrs=_attrs, ctx=ctx, name=name)
  if _execute.must_record_gradient():
    _execute.record_gradient(
        "UniformQuantize", _inputs_flat, _attrs, _result)
  _result, = _result
  return _result


def uniform_quantized_dot_hybrid(lhs, rhs, rhs_scales, rhs_zero_points, Tout, rhs_quantization_min_val, rhs_quantization_max_val, rhs_quantization_axis=-1, name=None):
  r"""Perform hybrid quantized dot of float Tensor `lhs` and quantized Tensor `rhs`.

  Given float `lhs` and quantized `rhs`, internally performs quantization on `lhs`, and then performs quantized dot on quantized lhs and `rhs`.
  The internal quantization on `lhs` is a quantization to qint8, dynamic range, per-batch (per-axis along axis 0), asymmetric, and not narrow range (the range is [-128, 127]).
  `lhs` and `rhs` must be 2D Tensors and the lhs.dim_size(1) must match rhs.dim_size(0).
  `rhs` must be quantized Tensor, where its data value is quantized using the formula:
  quantized_data = clip(original_data / scale + zero_point, quantization_min_val, quantization_max_val).

  Args:
    lhs: A `Tensor`. Must be one of the following types: `float32`.
      Must be a 2D Tensor of Tlhs.
    rhs: A `Tensor`. Must be one of the following types: `qint8`.
      Must be a 2D Tensor of Trhs.
    rhs_scales: A `Tensor` of type `float32`.
      The float value(s) used as scale when quantizing original data that rhs represents.
      Must be a scalar Tensor (per-tensor quantization) or 1D Tensor of size (rhs.dim_size(1),) (per-channel quantization).
    rhs_zero_points: A `Tensor` of type `int32`.
      The int32 value(s) used as zero_point when quantizing original data that rhs represents.
      Same shape condition as rhs_scales.
    Tout: A `tf.DType` from: `tf.float32`. The type of output Tensor.
    rhs_quantization_min_val: An `int`.
      The min value of the quantized data stored in rhs.
      For example, if Trhs is qint8, this must be set to -127 if narrow range quantized or -128 if not.
    rhs_quantization_max_val: An `int`.
      The max value of the quantized data stored in rhs.
      For example, if Trhs is qint8, this must be set to 127.
    rhs_quantization_axis: An optional `int`. Defaults to `-1`.
      Indicates the dimension index of the tensor where per-axis quantization is applied for the slices along that dimension.
      If set to -1 (default), this indicates per-tensor quantization.
      For dot op rhs, only per-tensor quantization or per-channel quantization along dimension 1 is supported.
      Thus, this attribute must be set to -1 or 1. Other values are rejected.
    name: A name for the operation (optional).

  Returns:
    A `Tensor` of type `Tout`.
  """
  _ctx = _context._context or _context.context()
  tld = _ctx._thread_local_data
  if tld.is_eager:
    try:
      _result = pywrap_tfe.TFE_Py_FastPathExecute(
        _ctx, "UniformQuantizedDotHybrid", name, lhs, rhs, rhs_scales,
        rhs_zero_points, "Tout", Tout, "rhs_quantization_axis",
        rhs_quantization_axis, "rhs_quantization_min_val",
        rhs_quantization_min_val, "rhs_quantization_max_val",
        rhs_quantization_max_val)
      return _result
    except _core._NotOkStatusException as e:
      _ops.raise_from_not_ok_status(e, name)
    except _core._FallbackException:
      pass
    try:
      return uniform_quantized_dot_hybrid_eager_fallback(
          lhs, rhs, rhs_scales, rhs_zero_points, Tout=Tout,
          rhs_quantization_axis=rhs_quantization_axis,
          rhs_quantization_min_val=rhs_quantization_min_val,
          rhs_quantization_max_val=rhs_quantization_max_val, name=name,
          ctx=_ctx)
    except _core._SymbolicException:
      pass  # Add nodes to the TensorFlow graph.
  # Add nodes to the TensorFlow graph.
  Tout = _execute.make_type(Tout, "Tout")
  rhs_quantization_min_val = _execute.make_int(rhs_quantization_min_val, "rhs_quantization_min_val")
  rhs_quantization_max_val = _execute.make_int(rhs_quantization_max_val, "rhs_quantization_max_val")
  if rhs_quantization_axis is None:
    rhs_quantization_axis = -1
  rhs_quantization_axis = _execute.make_int(rhs_quantization_axis, "rhs_quantization_axis")
  _, _, _op, _outputs = _op_def_library._apply_op_helper(
        "UniformQuantizedDotHybrid", lhs=lhs, rhs=rhs, rhs_scales=rhs_scales,
                                     rhs_zero_points=rhs_zero_points,
                                     Tout=Tout,
                                     rhs_quantization_min_val=rhs_quantization_min_val,
                                     rhs_quantization_max_val=rhs_quantization_max_val,
                                     rhs_quantization_axis=rhs_quantization_axis,
                                     name=name)
  _result = _outputs[:]
  if _execute.must_record_gradient():
    _attrs = ("Tlhs", _op._get_attr_type("Tlhs"), "Trhs",
              _op._get_attr_type("Trhs"), "Tout", _op._get_attr_type("Tout"),
              "rhs_quantization_axis",
              _op._get_attr_int("rhs_quantization_axis"),
              "rhs_quantization_min_val",
              _op._get_attr_int("rhs_quantization_min_val"),
              "rhs_quantization_max_val",
              _op._get_attr_int("rhs_quantization_max_val"))
    _inputs_flat = _op.inputs
    _execute.record_gradient(
        "UniformQuantizedDotHybrid", _inputs_flat, _attrs, _result)
  _result, = _result
  return _result

UniformQuantizedDotHybrid = tf_export("raw_ops.UniformQuantizedDotHybrid")(_ops.to_raw_op(uniform_quantized_dot_hybrid))


def uniform_quantized_dot_hybrid_eager_fallback(lhs, rhs, rhs_scales, rhs_zero_points, Tout, rhs_quantization_min_val, rhs_quantization_max_val, rhs_quantization_axis, name, ctx):
  Tout = _execute.make_type(Tout, "Tout")
  rhs_quantization_min_val = _execute.make_int(rhs_quantization_min_val, "rhs_quantization_min_val")
  rhs_quantization_max_val = _execute.make_int(rhs_quantization_max_val, "rhs_quantization_max_val")
  if rhs_quantization_axis is None:
    rhs_quantization_axis = -1
  rhs_quantization_axis = _execute.make_int(rhs_quantization_axis, "rhs_quantization_axis")
  _attr_Tlhs, (lhs,) = _execute.args_to_matching_eager([lhs], ctx, [_dtypes.float32, ])
  _attr_Trhs, (rhs,) = _execute.args_to_matching_eager([rhs], ctx, [_dtypes.qint8, ])
  rhs_scales = _ops.convert_to_tensor(rhs_scales, _dtypes.float32)
  rhs_zero_points = _ops.convert_to_tensor(rhs_zero_points, _dtypes.int32)
  _inputs_flat = [lhs, rhs, rhs_scales, rhs_zero_points]
  _attrs = ("Tlhs", _attr_Tlhs, "Trhs", _attr_Trhs, "Tout", Tout,
  "rhs_quantization_axis", rhs_quantization_axis, "rhs_quantization_min_val",
  rhs_quantization_min_val, "rhs_quantization_max_val",
  rhs_quantization_max_val)
  _result = _execute.execute(b"UniformQuantizedDotHybrid", 1,
                             inputs=_inputs_flat, attrs=_attrs, ctx=ctx,
                             name=name)
  if _execute.must_record_gradient():
    _execute.record_gradient(
        "UniformQuantizedDotHybrid", _inputs_flat, _attrs, _result)
  _result, = _result
  return _result

