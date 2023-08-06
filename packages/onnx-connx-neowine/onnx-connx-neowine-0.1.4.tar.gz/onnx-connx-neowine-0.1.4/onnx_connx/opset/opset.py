import numpy as np
from .util import _int, _float, _string, _ints, _null, _floats, _strings, _graph, _tensor
from .MaxPool import MaxPool
from .BatchNormalization import BatchNormalization
from .GlobalAveragePool import GlobalAveragePool
from .Conv import Conv
from .Cast import Cast
from .Resize import Resize
import onnx

# Internal operators
def _ref(output_count, tensor):
    pass


# Most of the implementations are fllowd by ONNX reference implementation
def Abs(ouput_count, X):
    return np.abs(X)


def Acos(output_count, X):
    return np.arccos(X)


def Acosh(ouput_count, input):
    return np.arccosh(input)


def Add(ouput_count, A, B):
    return A + B


def And(output_count, A, B):
    return np.logical_and(A, B)


def ArgMax(output_count, data, axis, keepdims, select_last_index):
    if select_last_index == 1:
        data = np.flip(data, axis)

    result = np.argmax(data, axis=axis)
    if keepdims == 1:
        result = np.expand_dims(result, axis)

    if select_last_index == 1:
        result = data.shape[axis] - result - 1

    return result.astype(np.int64)


def ArgMin(output_count, data, axis, keepdims, select_last_index):
    if select_last_index == 1:
        data = np.flip(data, axis)

    result = np.argmin(data, axis=axis)
    if keepdims == 1:
        result = np.expand_dims(result, axis)

    if select_last_index == 1:
        result = data.shape[axis] - result - 1

    return result.astype(np.int64)


def Asin(output_count, input):
    return np.arcsin(input)


def MatMul(output_count, A, B):

    return np.matmul(A, B)


def Relu(output_count, X):
    return np.clip(X, 0, np.inf)


def Reshape(ouput_count, data, shape, allowzero):
    new_shape = np.copy(shape)

    if allowzero == 0:
        zeros_index = np.where(shape == 0)
        new_shape[zeros_index] = np.array(data.shape)[zeros_index]

    reshaped = np.reshape(data, new_shape)

    return reshaped


def Concat(*inputs):
    r"""
    inputs type constraints
        tensor(uint8), tensor(uint16), tensor(uint32), tensor(uint64),
        tensor(int8), tensor(int16), tensor(int32), tensor(int64),
        tensor(bfloat16), tensor(float16), tensor(float), tensor(double),
        tensor(string), tensor(bool), tensor(complex64), tensor(complex128)
    """
    axis = inputs[-1]
    inputs = inputs[1:-1]
    concat_result = np.concatenate(inputs, axis)

    return concat_result


def Exp(output_count, input):
    r"""
    input type constraints
        tensor(float16), tensor(float), tensor(double), tensor(bfloat16)
    """
    return np.exp(input)


def Flatten(output_count, input, axis):
    r"""
        :param input: A Tensor of rank >= axis.
        :param axis: Indicate up to which input dimensions (exclusive) should be flattened to the outer dimension of
                     the output.

        input type constraints
            tensor(uint8), tensor(uint16), tensor(uint32), tensor(uint64), tensor(int8), tensor(int16),
            tensor(int32), tensor(int64), tensor(bfloat16), tensor(float16), tensor(float), tensor(double),
            tensor(string), tensor(bool), tensor(complex64), tensor(complex128)
    """
    if axis < 0:
        axis = len(input.shape) + axis

    front = 1
    end = 1
    if axis != 0:
        for i in range(0, len(input.shape)):
            if i >= axis:
                end *= input.shape[i]
            else:
                front *= input.shape[i]
        return input.reshape(front, end)
    else:
        flatten = 1
        for x in input.shape:
            flatten *= x
        return np.array([input.reshape(flatten)])


def Gather(output_count, data, indices, axis):
    r"""
    :param data: Tensor of rank r >= 1.
    :param indices: Tensor of int32/int64 indices of any rank q.
                    All index values are expected to be
                    within bounds [-s, s-1] along axis of size s.
                    It is an error if any of the index values are out of bounds.
    """
    return np.take(data, indices, axis)


def Identity(output_count, input):
    r"""
    :param input: Input tensor.

    input type constraints
        tensor(uint8), tensor(uint16), tensor(uint32), tensor(uint64), tensor(int8), tensor(int16),
        tensor(int32), tensor(int64), tensor(bfloat16), tensor(float16), tensor(float), tensor(double),
        tensor(string), tensor(bool), tensor(complex64), tensor(complex128), seq(tensor(uint8)),
        seq(tensor(uint16)), seq(tensor(uint32)), seq(tensor(uint64)), seq(tensor(int8)), seq(tensor(int16)),
        seq(tensor(int32)), seq(tensor(int64)), seq(tensor(float16)), seq(tensor(float)), seq(tensor(double)),
        seq(tensor(string)), seq(tensor(bool)), seq(tensor(complex64)), seq(tensor(complex128))
    """
    if type(input) == list:
        return [np.copy(i) for i in input]
    else:
        return np.copy(input)


def LeakyRelu(ouput_count, X, alpha):
    return np.clip(X, 0, np.inf) + np.clip(X, -np.inf, 0) * alpha


def Log(output_count, input):
    return np.log(input)


def Mul(output_count, A, B):
    return A * B


def Shape(output_count, data):
    return np.array(data.shape, dtype=np.int64)


def Sigmoid(output_count, X):
    return 1.0 / (1.0 + np.exp(np.negative(X)))


def Slice(output_count, data, starts, ends, axes, steps):
    # TODO : Naive implementation.
    expr = [":"] * len(data.shape)
    if axes is None:
        axes = np.array([i for i in range(len(data.shape))])

    for i in range(axes.shape[0]):
        if steps is None:
            expr[axes[i]] = f"{starts[i]}:{ends[i]}"
        else:
            expr[axes[i]] = f"{starts[i]}:{ends[i]}:{steps[i]}"

    slice_str = (",").join(expr)
    eval_str = f"data[{slice_str}]"

    return eval(eval_str)


def Split(output_count, input, split, axis):
    outputs = []
    start = 0

    if split is None:
        return tuple(np.array_split(input, output_count, axis))

    for i in range(split.shape[0]):
        expr = [":"] * len(input.shape)
        expr[axis] = f"{start}:{start + split[i]}"
        slice_str = (",").join(expr)
        eval_str = f"input[{slice_str}]"
        outputs.append(eval(eval_str))
        start = split[i]

    return tuple(outputs)


def Tanh(output_count, X):
    return np.tanh(X)


def Transpose(output_count, data, perm):
    if not perm:
        return np.transpose(data)
    return np.transpose(data, perm)


def Clip(output_count, X, min_val, max_val):
    if min_val is None:
        if np.issubdtype(X.dtype, np.integer):
            min_val = np.iinfo(X.dtype).min
        elif np.issubdtype(X.dtype, np.floating):
            min_val = -np.inf

    if max_val is None:
        if np.issubdtype(X.dtype, np.integer):
            max_val = np.iinfo(X.dtype).max
        elif np.issubdtype(X.dtype, np.floating):
            max_val = np.inf

    return np.clip(X, min_val, max_val)

version = 18
each_opset_version = {
    'Add' : [14, 13, 7, 6, 1] ,
    'Asin' : [7] ,
    'Atan' : [7] ,
    'Atanh' : [9] ,
    'AveragePool' : [11, 10, 7, 1] ,
    'BatchNormalization' : [15, 14, 9, 7, 6, 1] ,
    'Cast' : [13, 9, 6, 1] ,
    'Clip' : [13, 12, 11, 6, 1] ,
    'Concat' : [13, 11, 4, 1] ,
    'Constant' : [13, 12, 11, 9, 1] ,
    'ConstantOfShape' : [9] ,
    'Conv' : [11, 1] ,
    'ConvInteger' : [10] ,
    'Div' : [14, 13, 7, 6, 1] ,
    'Expand' : [13, 8] ,
    'Flatten' : [13, 11, 9, 1] ,
    'Gather' : [13, 11, 1] ,
    'Gemm' : [13, 11, 9, 7, 6, 1] ,
    'GlobalAveragePool' : [1] ,
    'HardSigmoid' : [6, 1] ,
    'Identity' : [16, 14, 13, 1] ,
    'If' : [16, 13, 11, 1] ,
    'LSTM' : [14, 7, 1] ,
    'LeakyRelu' : [16, 6, 1] ,
    'Log' : [13, 6, 1] ,
    'MatMul' : [13, 9, 1] ,
    'MatMulInteger' : [10] ,
    'MaxPool' : [12, 11, 10, 8, 1] ,
    'Mul' : [14, 13, 7, 6, 1] ,
    'Not' : [1] ,
    'Pad' : [13, 11, 2, 1] ,
    'QLinearAdd' : [1] ,
    'QLinearConv' : [10] ,
    'QLinearMatMul' : [10] ,
    'QuantizeLinear' : [13, 10] ,
    'RNN' : [14, 7, 1] ,
    'Relu' : [14, 13, 6, 1] ,
    'Reshape' : [14, 13, 5, 1] ,
    'Round' : [11] ,
    'Selu' : [6, 1] ,
    'Shape' : [15, 13, 1] ,
    'Sigmoid' : [13, 6, 1] ,
    'Slice' : [13, 11, 10, 1] ,
    'Split' : [13, 11, 2, 1] ,
    'Sqrt' : [13, 6, 1] ,
    'Squeeze' : [13, 11, 1] ,
    'Sub' : [14, 13, 7, 6, 1] ,
    'Tan' : [7] ,
    'Tanh' : [13, 6, 1] ,
    'Transpose' : [13, 1] ,
    'Unsqueeze' : [13, 11, 1] ,
    'QLinearGlobalAveragePool' : [1] ,
    'DequantizeLinear' : [1] ,

}
opset = {
    'QLinearConcat' : None,
    '_ref': _ref,
    'Abs': Abs,
    'Acos': Acos,
    'Acosh': Acosh,
    'Add': Add,
    'And': And,
    'ArgMax': ArgMax,
    'ArgMin': ArgMin,
    'Asin': Asin,
    'Asinh': None,
    'Atan': None,
    'Atanh': None,
    'AveragePool': None,
    'BatchNormalization': BatchNormalization,
    'BitShift': None,
    'Cast': Cast,
    'Ceil': None,
    'Celu': None,
    'Clip': Clip,
    'Compress': None,
    'Concat': Concat,
    'ConcatFromSequence': None,
    'Constant': None,
    'ConstantOfShape': None,
    'Conv': Conv,
    'ConvInteger': None,
    'ConvTranspose': None,
    'Cos': None,
    'Cosh': None,
    'CumSum': None,
    'DepthToSpace': None,
    'DequantizeLinear': None,
    'Det': None,
    'Div': None,
    'Dropout': None,
    'Einsum': None,
    'Elu': None,
    'Equal': None,
    'Erf': None,
    'Exp': Exp,
    'Expand': None,
    'EyeLike': None,
    'Flatten': Flatten,
    'Floor': None,
    'GRU': None,
    'Gather': Gather,
    'GatherElements': None,
    'GatherND': None,
    'Gemm': None,
    'GlobalAveragePool': GlobalAveragePool,
    'GlobalLpPool': None,
    'GlobalMaxPool': None,
    'Greater': None,
    'HardSigmoid': None,
    'Hardmax': None,
    'Identity': Identity,
    'If': None,
    'InstanceNormalization': None,
    'IsInf': None,
    'IsNaN': None,
    'LRN': None,
    'LSTM': None,
    'LeakyRelu': LeakyRelu,
    'Less': None,
    'Log': Log,
    'Loop': None,
    'LpNormalization': None,
    'LpPool': None,
    'MatMul': MatMul,
    'MatMulInteger': None,
    'Max': None,
    'MaxPool': MaxPool,
    'MaxRoiPool': None,
    'MaxUnpool': None,
    'Mean': None,
    'Min': None,
    'Mod': None,
    'Mul': Mul,
    'Multinomial': None,
    'Neg': None,
    'NonMaxSuppression': None,
    'NonZero': None,
    'Not': None,
    'OneHot': None,
    'Or': None,
    'PRelu': None,
    'Pad': None,
    'Pow': None,
    'QLinearConv': None,
    'QLinearMatMul': None,
    'QuantizeLinear': None,
    'RNN': None,
    'RandomNormal': None,
    'RandomNormalLike': None,
    'RandomUniform': None,
    'RandomUniformLike': None,
    'Reciprocal': None,
    'ReduceL1': None,
    'ReduceL2': None,
    'ReduceLogSum': None,
    'ReduceLogSumExp': None,
    'ReduceMax': None,
    'ReduceMean': None,
    'ReduceMin': None,
    'ReduceProd': None,
    'ReduceSum': None,
    'ReduceSumSquare': None,
    'Relu': Relu,
    'Reshape': Reshape,
    'Resize': Resize,
    'ReverseSequence': None,
    'RoiAlign': None,
    'Round': None,
    'Scan': None,
    'Scatter (deprecated)': None,
    'ScatterElements': None,
    'ScatterND': None,
    'Selu': None,
    'SequenceAt': None,
    'SequenceConstruct': None,
    'SequenceEmpty': None,
    'SequenceErase': None,
    'SequenceInsert': None,
    'SequenceLength': None,
    'Shape': Shape,
    'Shrink': None,
    'Sigmoid': Sigmoid,
    'Sign': None,
    'Sin': None,
    'Sinh': None,
    'Size': None,
    'Slice': Slice,
    'Softplus': None,
    'Softsign': None,
    'SpaceToDepth': None,
    'Split': Split,
    'SplitToSequence': None,
    'Sqrt': None,
    'Squeeze': None,
    'StringNormalizer': None,
    'Sub': None,
    'Sum': None,
    'Tan': None,
    'Tanh': Tanh,
    'TfIdfVectorizer': None,
    'ThresholdedRelu': None,
    'Tile': None,
    'TopK': None,
    'Transpose': Transpose,
    'Trilu': None,
    'Unique': None,
    'Unsqueeze': None,
    'Upsample (deprecated)': None,
    'Where': None,
    'Xor': None,
    'Function': None,
    'DynamicQuantizeLinear': None,
    'GreaterOrEqual': None,
    'HardSwish': None,
    'LessOrEqual': None,
    'LogSoftmax': None,
    'MeanVarianceNormalization': None,
    'NegativeLogLikelihoodLoss': None,
    'Range': None,
    'Softmax': None,
    'SoftmaxCrossEntropyLoss': None,
    'QLinearAdd' : None,
    'QLinearGlobalAveragePool' : None,
    'QLinearConcat' : None,
}

#  minimum input count, maximum input count]
# -1 means unlimited
argcount = {
    '_ref': [1, 1],
    'Abs': [1, 1],
    'Acos': [1, 1],
    'Acosh': [1, 1],
    'Add': [2, 2],
    'And': [2, 2],
    'ArgMax': [1, 1],
    'ArgMin': [1, 1],
    'Asin': [1, 1],
    'Asinh': [1, 1],
    'Atan': [1, 1],
    'Atanh': [1, 1],
    'AveragePool': [1, 1],
    'BatchNormalization': [5, 5],
    'BitShift': [2, 2],
    'Cast': [1, 1],
    'Ceil': [1, 1],
    'Celu': [1, 1],
    'Clip': [1, 3],
    'Compress': [2, 2],
    'Concat': [1, -1],
    'ConcatFromSequence': None,
    'Constant': None,
    'ConstantOfShape': [1,1],
    'Conv': [2, 3],
    'ConvInteger': [2,4],
    'ConvTranspose': None,
    'Cos': None,
    'Cosh': None,
    'CumSum': None,
    'DepthToSpace': None,
    'DequantizeLinear': [2,3],
    'Det': None,
    'Div': None,
    'Dropout': None,
    'Einsum': None,
    'Elu': None,
    'Equal': None,
    'Erf': None,
    'Exp': [1, 1],
    'Expand': None,
    'EyeLike': None,
    'Flatten': [1, 1],
    'Floor': None,
    'GRU': None,
    'Gather': [2, 2],
    'GatherElements': None,
    'GatherND': None,
    'Gemm': [2,3],
    'GlobalAveragePool': [1, 1],
    'GlobalLpPool': None,
    'GlobalMaxPool': None,
    'Greater': None,
    'HardSigmoid': None,
    'Hardmax': None,
    'Identity': [1, 1],
    'If': None,
    'InstanceNormalization': None,
    'IsInf': None,
    'IsNaN': None,
    'LRN': None,
    'LSTM': [3,8],
    'LeakyRelu': [1, 1],
    'Less': None,
    'Log': [1, 1],
    'Loop': [2,-1],
    'LpNormalization': None,
    'LpPool': None,
    'MatMul': [2, 2],
    'MatMulInteger': [2,4],
    'Max': None,
    'MaxPool': [1, 1],
    'MaxRoiPool': None,
    'MaxUnpool': None,
    'Mean': None,
    'Min': None,
    'Mod': None,
    'Mul': [2, 2],
    'Multinomial': None,
    'Neg': None,
    'NonMaxSuppression': None,
    'NonZero': None,
    'Not': None,
    'OneHot': None,
    'Or': None,
    'PRelu': None,
    'Pad': [2,3],
    'Pow': None,
    'QLinearConv': [8,9],
    'QLinearMatMul': [8,8],
    'QuantizeLinear': [2,3],
    'RNN': [3,6],
    'RandomNormal': None,
    'RandomNormalLike': None,
    'RandomUniform': None,
    'RandomUniformLike': None,
    'Reciprocal': None,
    'ReduceL1': None,
    'ReduceL2': None,
    'ReduceLogSum': None,
    'ReduceLogSumExp': None,
    'ReduceMax': None,
    'ReduceMean': None,
    'ReduceMin': None,
    'ReduceProd': None,
    'ReduceSum': None,
    'ReduceSumSquare': None,
    'Relu': [1, 1],
    'Reshape': [2, 2],
    'Resize': [1, 4],
    'ReverseSequence': None,
    'RoiAlign': None,
    'Round': None,
    'Scan': None,
    'Scatter (deprecated)': None,
    'ScatterElements': None,
    'ScatterND': None,
    'Selu': None,
    'SequenceAt': None,
    'SequenceConstruct': [1,-1],
    'SequenceEmpty': None,
    'SequenceErase': None,
    'SequenceInsert': [2,3],
    'SequenceLength': None,
    'Shape': [1, 1],
    'Shrink': None,
    'Sigmoid': [1, 1],
    'Sign': None,
    'Sin': None,
    'Sinh': None,
    'Size': None,
    'Slice': [3, 5],
    'Softplus': None,
    'Softsign': None,
    'SpaceToDepth': None,
    'Split': [1, 2],
    'SplitToSequence': None,
    'Sqrt': None,
    'Squeeze': None,
    'StringNormalizer': None,
    'Sub': None,
    'Sum': None,
    'Tan': None,
    'Tanh': [1, 1],
    'TfIdfVectorizer': None,
    'ThresholdedRelu': None,
    'Tile': None,
    'TopK': None,
    'Transpose': [1, 1],
    'Trilu': None,
    'Unique': None,
    'Unsqueeze': [2,2],
    'Upsample (deprecated)': None,
    'Where': None,
    'Xor': None,
    'Function': None,
    'DynamicQuantizeLinear': None,
    'GreaterOrEqual': None,
    'HardSwish': None,
    'LessOrEqual': None,
    'LogSoftmax': None,
    'MeanVarianceNormalization': None,
    'NegativeLogLikelihoodLoss': None,
    'Range': None,
    'Softmax': None,
    'SoftmaxCrossEntropyLoss': None,
    'QLinearAdd' : [7,8],
    'QLinearGlobalAveragePool' : [5,5],
    'QLinearConcat' : [3,-1],
    'OptionalGetElement' : None,
    'OptionalHasElement' : None,
    'Optional' : [0,1],
}

attrset = {
    '_ref': [_int('ref_count', 0)],
    'Abs': [],
    'Acos': [],
    'Acosh': [],
    'Add': [],
    'And': [],
    'ArgMax': [_int('axis', 0), _int('keepdims', 1), _int('select_last_index', 0)],
    'ArgMin': [_int('axis', 0), _int('keepdims', 1), _int('select_last_index', 0)],
    'Asin': [],
    'Asinh': [],
    'Atan': [],
    'Atanh': [],
    'AveragePool': [_string('auto_pad', 'NOTSET'), _int('ceil_mode', 0), _int('count_include_pad', 0),
                    _ints('kernel_shape', []), _ints('pads', []), _ints('strides', [1])],
    'BatchNormalization': [_float('epsilon', 1e-05), _float('momentum', 0.9), _int('training_mode', 0)],
    'BitShift': [_string('direction', '')],
    'Cast': [_int('to', 0)],
    'Ceil': [],
    'Celu': [_float('alpha', 1.0)],
    'Clip': [],
    'Compress': [_int('axis', 0)],
    'Concat': [_int('axis', 0)],
    'ConcatFromSequence': [_int('axis', 0), _int('new_axis', 0)],
    'Constant': [_tensor('value')],
    'ConstantOfShape': [_tensor('value')],
    'Conv': [_string('auto_pad', 'NOTSET'), _ints('dilations', []), _int('group', 1),
             _ints('kernel_shape', []), _ints('pads', []), _ints('strides', [])],
    'ConvInteger': [_string('auto_pad', 'NOTSET'), _ints('dilations', []), _int('group', 1),
             _ints('kernel_shape', []), _ints('pads', []), _ints('strides', [])],
    'ConvTranspose': [],
    'Cos': [],
    'Cosh': [],
    'CumSum': [],
    'DepthToSpace': [],
    'DequantizeLinear': [_int('axis', 1)],
    'Det': [],
    'Div': [],
    'Dropout': [],
    'Einsum': [],
    'Elu': [],
    'Equal': [],
    'Erf': [],
    'Exp': [],
    'Expand': [],
    'EyeLike': [],
    'Flatten': [_int('axis', 1)],
    'Floor': [],
    'GRU': [],
    'Gather': [_int('axis', 0)],
    'GatherElements': [],
    'GatherND': [],
    'Gemm': [_float('alpha', 1.0), _float('beta', 1.0), _int('transA', 0), _int('transB', 0)],
    'GlobalAveragePool': [],
    'GlobalLpPool': [],
    'GlobalMaxPool': [],
    'Greater': [],
    'HardSigmoid': [_float('alpha',0.2), _float('beta',0.5)],
    'Hardmax': [],
    'Identity': [],
    'If': [_graph('else_branch'), _graph('then_branch')],
    'InstanceNormalization': [],
    'IsInf': [],
    'IsNaN': [],
    'LRN': [],
    'LSTM': [_floats('activation_alpha', []), _floats('activation_beta', []), _strings('activations', ['Sigmoid', 'Tanh', 'Tanh']), _float('clip'), _string('direction', 'forward'), _int('hidden_size'), _int('input_forget', 0), _int('layout',0)],
    'LeakyRelu': [_float('alpha', 0.01)],
    'Less': [],
    'Log': [],
    'Loop': [_graph('body')],
    'LpNormalization': [],
    'LpPool': [],
    'MatMul': [],
    'MatMulInteger': [],
    'Max': [],
    'MaxPool': [_string('auto_pad', 'NOTSET'), _int('ceil_mode', 0), _ints('dilations', [1]),
                _ints('kernel_shape', []), _ints('pads', []), _int('storage_order', 0), _ints('strides', [1])],
    'MaxRoiPool': [],
    'MaxUnpool': [],
    'Mean': [],
    'Min': [],
    'Mod': [],
    'Mul': [],
    'Multinomial': [],
    'Neg': [],
    'NonMaxSuppression': [],
    'NonZero': [],
    'Not': [],
    'OneHot': [],
    'Or': [],
    'PRelu': [],
    'Pad': [_string('mode', 'constant')],
    'Pow': [],
    'QLinearConv': [_string('auto_pad', 'NOTSET'), _ints('dilations', []), _int('group', 1), _ints('kernel_shape', []), _ints('pads', []), _ints('strides', [])],
    'QLinearMatMul': [],
    'QuantizeLinear': [_int('axis', 1)],
    'RNN': [_floats('activation_alpha',[]), _floats('activation_beta',[]), _strings('activations',['Tanh', 'Tanh']), _float('clip'), _string('direction', 'forward'), _int('hidden_size'), _int('layout',0)],
    'RandomNormal': [],
    'RandomNormalLike': [],
    'RandomUniform': [],
    'RandomUniformLike': [],
    'Reciprocal': [],
    'ReduceL1': [],
    'ReduceL2': [],
    'ReduceLogSum': [],
    'ReduceLogSumExp': [],
    'ReduceMax': [],
    'ReduceMean': [],
    'ReduceMin': [],
    'ReduceProd': [],
    'ReduceSum': [],
    'ReduceSumSquare': [],
    'Relu': [],
    'Reshape': [_int('allowzero', 0)],
    'Resize': [_string('coordinate_transformation_mode', 'half_pixel'),
               _float('cubic_coeff_a', -0.75),
               _int('exclude_outside', 0),
               _float('extrapolation_value', 0.0),
               _string('mode', 'nearest'),
               _string('nearest_mode', 'round_prefer_floor')],
    'ReverseSequence': [],
    'RoiAlign': [],
    'Round': [],
    'Scan': [],
    'Scatter (deprecated)': [],
    'ScatterElements': [],
    'ScatterND': [],
    'Selu': [_float('alpha', 1.67326), _float('gamma', 1.0507)],
    'SequenceAt': [],
    'SequenceConstruct': [],
    'SequenceEmpty': [],
    'SequenceErase': [],
    'SequenceInsert': [],
    'SequenceLength': [],
    'Shape': [_int('end'), _int('start', 0)],
    'Shrink': [],
    'Sigmoid': [],
    'Sign': [],
    'Sin': [],
    'Sinh': [],
    'Size': [],
    'Slice': [_ints('axes', []), _ints('ends', []), _ints('starts', [])],
    'Softplus': [],
    'Softsign': [],
    'SpaceToDepth': [],
    'Split': [_int('axis', 0)],
    'SplitToSequence': [],
    'Sqrt': [],
    'Squeeze': [_ints('axes', [])],
    'StringNormalizer': [],
    'Sub': [],
    'Sum': [],
    'Tan': [],
    'Tanh': [],
    'TfIdfVectorizer': [],
    'ThresholdedRelu': [],
    'Tile': [],
    'TopK': [],
    'Transpose': [_ints('perm', [])],
    'Trilu': [],
    'Unique': [],
    'Unsqueeze': [],
    'Upsample (deprecated)': [],
    'Where': [],
    'Xor': [],
    'Function': [],
    'DynamicQuantizeLinear': [],
    'GreaterOrEqual': [],
    'HardSwish': [],
    'LessOrEqual': [],
    'LogSoftmax': [],
    'MeanVarianceNormalization': [],
    'NegativeLogLikelihoodLoss': [],
    'Range': [],
    'Softmax': [],
    'SoftmaxCrossEntropyLoss': [],
    'QLinearAdd' : [],
    'QLinearGlobalAveragePool' : [_int('channels_last', 0)],
    'QLinearConcat' : [_int('axis')],
    'OptionalGetElement' : [],
    'OptionalHasElement' : [],
    'Optional' : [_tensor('type')],
    'QGemm' : [],
}
