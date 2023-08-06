import sys
import os
import argparse
import numpy as np
import onnx
from onnx import numpy_helper
import struct
from .proto import ConnxModelProto
import torch
from glob import glob
import zipfile

def load_model(path, ref_print, outputPath) -> ConnxModelProto:
    proto = onnx.load_model(path)
    return ConnxModelProto(proto, ref_print, outputPath)
  

def compile_from_model(model_proto, path) -> int:
    connx = ConnxModelProto(model_proto)
    connx.compile(path)

    return 0


def load_tensor(path) -> onnx.TensorProto:
    tensor = onnx.TensorProto()
    with open(path, 'rb') as f:
        tensor.ParseFromString(f.read())

    return tensor

def load_sequenceProto(path) -> onnx.SequenceProto :
    _sequenceProto = onnx.SequenceProto()
    with open(path, 'rb') as f :
        _sequenceProto.ParseFromString(f.read())
    return _sequenceProto

def load_optionalProto(path) -> onnx.OptionalProto :
    _optionalProto = onnx.OptionalProto()
    with open(path, 'rb') as f :
        _optionalProto.ParseFromString(f.read())
    return _optionalProto

def compile(*_args: str) -> int:
    parser = argparse.ArgumentParser(description='ONNX-CONNX Command Line Interface')
    parser.add_argument('onnx', metavar='onnx', nargs='+', help='an input ONNX model file or tensor pb file')
    parser.add_argument('-d', action='store_true', help='dump human readable onnx metadata to standard output')
    parser.add_argument('-o', metavar='output directory', type=str, default='out', nargs='?',
                        help='output directory(default is out)')
    parser.add_argument('--ref', metavar='ref print boolean', type=int, default=0, help="default(no print) --> --ref 0 || print ref --> --ref 1")
    parser.add_argument('--shape', nargs='+', type=str, dest='shape_data', help="if shape (1,2,3,4) -> --shape 1 2 3 4")
    # parser.add_argument('-p', metavar='profile', type=str, nargs='?', help='specify configuration file')
    # parser.add_argument('e-c', metavar='comment', type=str, nargs='?', choices=['true', 'false', 'True', 'False'],
    #                     heelp='output comments(true or false)')
    # parse args
    ref_print_arg = 0
    

    if len(_args) > 0:
        args = parser.parse_args(_args)
    else:
        args = parser.parse_args()
    if not (('input_' in args.onnx[0]) or ('output_' in args.onnx[0]) or (args.onnx[0].endswith('.onnx'))) :
        # bin/convert
        # args.onnx[0] = args.onnx[0][:-12]
        try :
            # tensorlow model
            print("tensorflow model")
            file_name = args.onnx[0][::-1].split('/', maxsplit=1)[0][::-1]
            temp = args.onnx[0][::-1].split('/', maxsplit=1)[1][::-1]
            os.system("mkdir {0}/converted_onnx_{1}".format(temp,file_name))
            os.system("python -m tf2onnx.convert --saved-model ""{0}"" --large_model --opset 11 --output ""./{1}/converted_onnx_{2}/tensorflow_model.onnx""".format(args.onnx[0], temp, file_name))
            tensorflow_zip = zipfile.ZipFile("./{0}/converted_onnx_{1}/tensorflow_model.onnx".format(temp,file_name))
            tensorflow_zip.extractall("./{0}/converted_onnx_{1}".format(temp,file_name))
            tensorflow_zip.close()
            os.system("rm -rf ./{0}/converted_onnx_{1}/tensorflow_model.onnx".format(temp, file_name))
            file_list = glob("./{0}/converted_onnx_{1}/*.onnx".format(temp,file_name))
            if args.ref :
                ref_print_arg = args.ref
            model = load_model(file_list[0],ref_print_arg, args.o)
            if args.d:
                model.dump()
            else:
                model.compile(args.o)
            os.system("rm -rf ./{0}/converted_onnx_{1}".format(temp, file_name))
        
        except :
            # pytorch model
            print("pytorch model")
            file_name = args.onnx[0][::-1].split('/', maxsplit=1)[0][::-1]
            temp = args.onnx[0][::-1].split('/', maxsplit=1)[1][::-1]
            os.system("rm -rf ./{0}/converted_onnx_{1}".format(temp, file_name))

            model_scripted = torch.jit.load(args.onnx[0])
            input_shape = []
            for i in range(0,len(args.shape_data)) :
                # input_shape.append(int(args.shape_data[i]))
                input_shape.append(int(args.shape_data[i]))
            # tuple_input_shape = tuple(input_shape)
            os.system("mkdir {0}/temp".format(temp))
            torch.onnx.export(model_scripted, torch.randn(*tuple(input_shape)), "./{0}/temp/pytorch_model.onnx".format(temp), export_params=True, opset_version=11)

            if args.ref :
                ref_print_arg = args.ref
            model = load_model("./{0}/temp/pytorch_model.onnx".format(temp),ref_print_arg, args.o)
            if args.d:
                model.dump()
            else:
                model.compile(args.o)
            os.system("rm -rf {0}/temp".format(temp))
    else :
        for path in args.onnx:
            if path.endswith('.onnx'):
                print("onnx model")
                if args.ref :
                    ref_print_arg = args.ref

                model = load_model(path,ref_print_arg, args.o)

                if args.d:
                    model.dump()
                else:
                    model.compile(args.o)
            elif path.endswith('.pb'):
                # tensor = load_tensor(path)

                if args.d:
                    tensor = load_tensor(path) #CJ FIX

                    array = numpy_helper.to_array(tensor)

                    np.set_printoptions(suppress=True, threshold=sys.maxsize, linewidth=160)
                    print(array)
                else:
                    name = os.path.basename(path).strip('.pb') + '.data'
                    try :
                        # tensor type Proto input/ouput
                        tensor = load_tensor(path) #CJ FIX
                        with open(os.path.join(args.o, name), 'wb') as out:
                            out.write(struct.pack('=I', tensor.data_type))
                            out.write(struct.pack('=I', len(tensor.dims)))
                            for i in range(len(tensor.dims)):
                                out.write(struct.pack('=I', tensor.dims[i]))
                            array = numpy_helper.to_array(tensor)
                            out.write(array.tobytes())
                    except :
                        # Sequence type / Optional type Proto
                        try :
                            # Sequence type Proto input/output
                            _sequence = load_sequenceProto(path) #CJ FIX
                            with open(os.path.join(args.o, name), 'wb') as out:
                                out.write(struct.pack('=I', _sequence.TENSOR))
                                out.write(struct.pack('=I', _sequence.SPARSE_TENSOR))
                                out.write(struct.pack('=I', _sequence.SEQUENCE))
                                out.write(struct.pack('=I', _sequence.MAP))
                                out.write(struct.pack('=I', _sequence.OPTIONAL))
                                array = numpy_helper.to_list(_sequence)
                                out.write(struct.pack('=I', len(_sequence.tensor_values)))
                                for i in range(0,len(_sequence.tensor_values)) :
                                    out.write(struct.pack('=I', _sequence.tensor_values[i].data_type))
                                    out.write(struct.pack('=I', len(_sequence.tensor_values[i].dims)))
                                    for j in range(0,len(_sequence.tensor_values[i].dims)) :
                                        out.write(struct.pack('=I', _sequence.tensor_values[i].dims[j]))
                                    out.write(array[i].tobytes())
                        except :
                            # Optional type Proto input/output
                            _optional = load_optionalProto(path) #CJ FIX
                            with open(os.path.join(args.o, name), 'wb') as out:
                                out.write(struct.pack('=I', _optional.TENSOR))
                                out.write(struct.pack('=I', _optional.SPARSE_TENSOR))
                                out.write(struct.pack('=I', _optional.SEQUENCE))
                                out.write(struct.pack('=I', _optional.MAP))
                                out.write(struct.pack('=I', _optional.OPTIONAL))
                                array = numpy_helper.to_optional(_optional)
                                try :
                                    out.write(struct.pack('=I', len(_optional.tensor_values)))
                                    for i in range(0,len(_optional.tensor_values)) :
                                        out.write(struct.pack('=I', len(_optional.tensor_values[i].dims)))
                                        for j in range(0,len(_optional.tensor_values[i].dims)) :
                                            out.write(struct.pack('=I', _optional.tensor_values[i].dims[j]))
                                        out.write(struct.pack('=I', _optional.tensor_values[i].data_type))
                                        out.write(array[i].tobytes())
                                except :
                                    out.write(struct.pack('=I', _optional.elem_type))
    return 0

def convert(modelpath, outpath = 'out', isdump = None, isref = None) -> int:
    if isref == 1 :
        ref_print_arg = isref
    else :
        isref == 0 or isref == None
        ref_print_arg = 0
        
    model = load_model(modelpath,ref_print_arg, outpath)
    print(model)
    if isdump == 1 :
        model.dump()
    else :
        model.compile(outpath)