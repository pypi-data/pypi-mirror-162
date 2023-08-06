from habana_frameworks.mediapipe.media_types import dtype as dt
from habana_frameworks.mediapipe.media_types import layout as lt
import media_pipe_types as mpt  # NOQA
import media_pipe_proxy as mppy  # NOQA
import numpy as np


def str_to_media_dtype(in_type):
    """
    Method to get convert string dtype to backend media dtype.

    :params in_type: media dtype.
    :returns : backend media dtype.
    """
    mdtype = None
    if(in_type == 'uint8'):
        mdtype = mpt.dType.UINT8
    elif(in_type == 'uint16'):
        mdtype = mpt.dType.UINT16
    elif(in_type == 'uint32'):
        mdtype = mpt.dType.UINT32
    elif(in_type == 'uint64'):
        mdtype = mpt.dType.UINT64
    elif(in_type == 'int8'):
        mdtype = mpt.dType.INT8
    elif(in_type == 'int16'):
        mdtype = mpt.dType.INT16
    elif(in_type == 'int32'):
        mdtype = mpt.dType.INT32
    elif(in_type == 'int64'):
        mdtype = mpt.dType.INT64
    elif(in_type == 'bfloat16'):
        mdtype = mpt.dType.BFLOAT16
    elif(in_type == 'float16'):
        mdtype = mpt.dType.FLOAT16
    elif(in_type == 'float32'):
        mdtype = mpt.dType.FLOAT32
    else:
        raise ValueError("invalid dtype {}".format(in_type))
    return mdtype


def media_dtype_to_str(in_type):
    """
    Method to get convert backend media dtype to string dtype.

    :params in_type: backend media dtype.
    :returns : string media dtype.
    """
    mdtype = None
    if(in_type == mpt.dType.UINT8):
        mdtype = 'uint8'
    elif(in_type == mpt.dType.UINT16):
        mdtype = 'uint16'
    elif(in_type == mpt.dType.UINT32):
        mdtype = 'uint32'
    elif(in_type == mpt.dType.UINT64):
        mdtype = 'uint64'
    elif(in_type == mpt.dType.INT8):
        mdtype = 'int8'
    elif(in_type == mpt.dType.INT16):
        mdtype = 'int16'
    elif(in_type == mpt.dType.INT32):
        mdtype = 'int32'
    elif(in_type == mpt.dType.INT64):
        mdtype = 'int64'
    elif(in_type == mpt.dType.BFLOAT16):
        mdtype = 'bfloat16'
    elif(in_type == mpt.dType.FLOAT16):
        mdtype = 'float16'
    elif(in_type == mpt.dType.FLOAT32):
        mdtype = 'float32'
    else:
        raise ValueError("invalid dtype {}".format(in_type))
    return mdtype


def get_str_dtype(in_type):
    """
    Method to get string datatype.

    :params in_type: input dtype.
    :returns : string media dtype.
    """
    str = None
    if (type(in_type) is mpt.dType):
        str = media_dtype_to_str(in_type)
    else:
        raise ValueError("invalid dtype {}".format(in_type))
    return str


def np_to_media_dtype(in_type):
    """
    Method to get convert numpy dtype to backend media dtype.

    :params in_type: numpy dtype.
    :returns : backend media dtype.
    """
    mdtype = None
    if(in_type == np.uint8):
        mdtype = mpt.dType.UINT8
    elif(in_type == np.uint16):
        mdtype = mpt.dType.UINT16
    elif(in_type == np.uint32):
        mdtype = mpt.dType.UINT32
    elif(in_type == np.uint64):
        mdtype = mpt.dType.UINT64
    elif(in_type == np.int8):
        mdtype = mpt.dType.INT8
    elif(in_type == np.int16):
        mdtype = mpt.dType.INT16
    elif(in_type == np.int32):
        mdtype = mpt.dType.INT32
    elif(in_type == np.int64):
        mdtype = mpt.dType.INT64
    # this needs special handling
    # elif(in_type == np.bfloat16):
    #    mdtype = mpt.dType.BFLOAT16
    elif(in_type == np.float16):
        mdtype = mpt.dType.FLOAT16
    elif(in_type == np.float32):
        mdtype = mpt.dType.FLOAT32
    else:
        raise ValueError("invalid dtype {}".format(in_type))
    return mdtype


def get_media_dtype(in_type):
    """
    Method to get backend media datatype.

    :params in_type: input dtype.
    :returns : backend media datatype.
    """
    mdtype = None
    if(type(in_type) is str):
        mdtype = str_to_media_dtype(in_type)
    elif (isinstance(np.dtype, type(in_type))):
        mdtype = np_to_media_dtype(in_type)
    elif (type(in_type) is mpt.dType):
        mdtype = in_type
    else:
        raise ValueError("invalid dtype {}".format(in_type))
    return mdtype


def str_to_np_dtype(in_type):
    """
    Method to get convert string type to numpy dtype.

    :params in_type: string dtype.
    :returns : numpy dtype.
    """
    nptype = None
    if(in_type == 'uint8'):
        nptype = np.uint8
    elif(in_type == 'uint16'):
        nptype = np.uint16
    elif(in_type == 'uint32'):
        nptype = np.uint32
    elif(in_type == 'uint64'):
        nptype = np.uint64
    elif(in_type == 'int8'):
        nptype = np.int8
    elif(in_type == 'int16'):
        nptype = np.int16
    elif(in_type == 'int32'):
        nptype = np.int32
    elif(in_type == 'int64'):
        nptype = np.int64
    # needs special handling
    # elif(in_type == 'bfloat16'):
    #    nptype = mpt.dType.BFLOAT16
    elif(in_type == 'bfloat16'):
        nptype = np.float16  # this is a workaround since bflaot16 has issue
    elif(in_type == 'float16'):
        nptype = np.float16
    elif(in_type == 'float32'):
        nptype = np.float32
    elif(in_type == ''):
        nptype = np.void
    else:
        raise ValueError("invalid dtype {}".format(in_type))
    return nptype


def media_to_np_dtype(in_type):
    """
    Method to get convert media backend dtype to numpy dtype.

    :params in_type: media backend dtype.
    :returns : numpy dtype.
    """
    nptype = None
    if(in_type == mpt.dType.UINT8):
        nptype = np.uint8
    elif(in_type == mpt.dType.UINT16):
        nptype = np.uint16
    elif(in_type == mpt.dType.UINT32):
        nptype = np.uint32
    elif(in_type == mpt.dType.UINT64):
        nptype = np.uint64
    elif(in_type == mpt.dType.INT8):
        nptype = np.int8
    elif(in_type == mpt.dType.INT16):
        nptype = np.int16
    elif(in_type == mpt.dType.INT32):
        nptype = np.int32
    elif(in_type == mpt.dType.INT64):
        nptype = np.int64
    # needs special handling
    # elif(in_type == 'bfloat16'):
    # elif(in_type == mpt.dType.BFLOAT16):  #TODO: Check if need to enable
        #nptype = np.float16
    elif(in_type == mpt.dType.FLOAT16):
        nptype = np.float16
    elif(in_type == mpt.dType.FLOAT32):
        nptype = np.float32
    else:
        raise ValueError("invalid dtype {}".format(in_type))
    return nptype


def get_numpy_dtype(in_type):
    """
    Method to get backend media datatype.

    :params in_type: input dtype.
    :returns : numpy datatype.
    """
    nptype = None
    if(type(in_type) is str):
        nptype = str_to_np_dtype(in_type)
    elif (type(in_type) is mpt.dType):
        nptype = media_to_np_dtype(in_type)
    elif (isinstance(np.dtype, type(in_type))):
        nptype = in_type
    else:
        raise ValueError("invalid dtype {}".format(in_type))
    return nptype


def str_to_media_fw_type(in_type):
    """
    Method to get convert string framework type to media backend framework type.

    :params in_type: string framework type.
    :returns : media backend framework type.
    """
    fw_type = ""
    if (in_type == "TF_FW"):
        fw_type = mppy.fwType.TF_FW
    elif(in_type == "SYNAPSE_FW"):
        fw_type = mppy.fwType.SYNAPSE_FW
    elif(in_type == "PYTHON_FW"):
        fw_type = mppy.fwType.PYTHON_FW
    else:
        raise ValueError("invalid fw type {}".format(in_type))
    return fw_type


def get_media_fw_type(in_type):
    """
    Method to get backend media framework type.

    :params in_type: input media framework type.
    :returns : backend framework type.
    """
    fw_type = None
    if(type(in_type) is str):
        fw_type = str_to_media_fw_type(in_type)
    elif(type(in_type) is mppy.fwType):
        fw_type = in_type
    else:
        raise ValueError("invalid fw type {}".format(in_type))
    return fw_type


def is_valid_dtype(in_type):
    """
    Method to check if given dtype is valid or not

    :params in_type: input media dtype:
    :returns : bool result.<True/False>
    """
    if(in_type == dt.UINT8 or in_type == dt.UINT16 or in_type == dt.UINT32 or in_type == dt.UINT64 or
       in_type == dt.INT8 or in_type == dt.INT16 or in_type == dt.INT32 or in_type == dt.INT64 or
       in_type == dt.FLOAT16 or in_type == dt.BFLOAT16 or in_type == dt.FLOAT32 or in_type == dt.NDT):
        return True
    else:
        return False


def is_valid_layout(in_lyt):
    """
    Method to check if given layout is valid or not

    :params in_lyt: input layout:
    :returns : bool result.<True/False>
    """
    if(in_lyt == lt.NA or in_lyt == lt.FHWC or in_lyt == lt.NCHW or in_lyt == lt.NHWC):
        return True
    else:
        return False


def getDeviceIdFromDeviceName(device):
    """
    Method to get device id from device name

    :params device: device name.<hpu:0/hpu:/hpu>
    :returns : device id.
    """
    # "hpu:0", "hpu:", "hpu": device id 0

    if device is None:
        raise ValueError("device is None")

    index = device.find(":")
    if index == -1:
        if device == "hpu":
            device_id = 0
        else:
            raise ValueError("hpu device {} not valid".format(device))
    else:
        device_name = device[:index]
        if device_name != "hpu":
            raise ValueError("hpu device {} not valid".format(device))

        if index == (len(device) - 1):
            device_id = 0
        else:
            if device[index+1:].isdigit() == True:
                device_id = int(device[index+1:])
                if device_id != 0:
                    raise ValueError(
                        "hpu device:{} device id not valid".format(device))
            else:
                raise ValueError(
                    "hpu device:{} device id not valid".format(device))
    return device_id
