# this file is responsible for c/c++ abtraction from the mediapipe
from habana_frameworks.mediapipe.backend.tensor import HPUTensor
from habana_frameworks.mediapipe.backend.utils import get_media_dtype
from habana_frameworks.mediapipe.media_types import readerOutType as ro
from habana_frameworks.mediapipe.media_types import randomCropType as rct  # NOQA

# helper function
from habana_frameworks.mediapipe.backend.legacy import legacy  # NOQA

import media_pipe_types as mpt  # NOQA
import media_pipe_params as mpp  # NOQA
import media_pipe_api as mpa  # NOQA
import media_pipe_proxy as mppy  # NOQA
import numpy as np


def is_ok(func_name, status):
    """
    Method to check backend return status.

    :params func_name: function name as string.
    :params status: return status of backend code.
    :raises RuntimeError: if status is failure.
    """
    if(status != mpt.status.SUCCESS):
        msg = "Media API {} failed! Error Code = {}.".format(func_name, status)
        raise RuntimeError(msg)


class media_manager():
    """
    Class defining media python to c interface for graph and compile time handling.

    """

    def __init__(self, device):
        """
        Constructor method.

        """
        self._device_ = device
        self._num_graph_inputs_ = 0
        self._num_graph_outputs_ = 1
        # this is assumed to have one receipe only
        self._num_graph_ws_ = 1
        # self._batch_size_ = batch_size
        # getting singletom object
        self._mm_ = mpa.MediaManager()
        self._mg_ = mpa.MediaGraph(mpt.device.GAUDI2)  # TODO: mpt.device.GRECO
        # initialize mediaand synapse
        self._mm_.initialize()
        self._recipe_ = None
        self._is_compiled_ = False

    # INFO: 1) dec_output_shape is exact output ordering you want
    #           for rgb-i case it will be 3,224,224,BATCH_SIZE
    #           for rgb-p case it will be 224,224,3,BATCH_SZIE
    #       2) output_tensor_name this is same as input tensor
    #           name of graph which is using it
    def create_decoder_node(self, tensor):
        """
        Method for creating decoder instance.

        """
        ip = mpp.mediaPlaceholderParams()
        ip.shape.numDims = len(tensor.shape)
        check_size = 1
        for i in range(ip.shape.numDims):
            ip.shape.dims[i] = tensor.shape[i]
            check_size = check_size * tensor.shape[i]
        if(check_size == 0 or len(tensor.shape) == 0):
            raise ValueError("op decoder output size is zero")
        assert(check_size)
        ip.output.outputScale = 1.0            # Scale and zerop 1 and 0
        ip.output.outputZp = 0
        ip.output.outputType = mpt.dType.UINT8  # decoder supports UINT8
        ip.layout = tensor.layout

        ret = self._mm_.createGenericNode(self._mg_,
                                          [],
                                          ip,
                                          "decoder_node",
                                          tensor.name)
        is_ok("createGenericNode - decoder", ret)

    # INFO: 1) dec_output_shape is exact output ordering you want
    #           for rgb-i case it will be 3,224,224,BATCH_SIZE
    #           for rgb-p case it will be 224,224,3,BATCH_SZIE
    #       2) output_tensor_name this is same as input tensor
    #           name of graph which is using it
    def create_ops_node(self, op):
        """
        Method for creating media opnode instance.

        """
        inputs = []
        for i in op.input_tensors:
            np = mpa.nodePort()
            np.nodeName = i.name
            np.nodePort = i.src_port  # need to store output numbers here in future
            inputs.append(np)
        cparams = op.cparams()
        if(hasattr(cparams, "params")):
            cparams.params = self._struct_populator_(type(cparams.params),
                                                     op.params)
        cparams.output = self._struct_populator_(type(cparams.output),
                                                 op.c_out_info)
        ret = self._mm_.createGenericNode(self._mg_,
                                          inputs,
                                          cparams,
                                          op.guid,
                                          op.name)
        is_ok("createGenericNode", ret)

    def _struct_populator_(self, cparams_type, pyparams):
        """
        Method for populating backend structure from python dictionary.

        """
        cparams = cparams_type()
        for pykey, pyvalue in pyparams.items():
            if(hasattr(cparams, pykey)):
                if isinstance(getattr(cparams, pykey), np.ndarray):
                    carr = getattr(cparams, pykey)
                    if(len(pyvalue) > len(carr)):
                        msg = "{}.{} length {} , expected {}".format(type(cparams),
                                                                     pykey,
                                                                     len(pyvalue),
                                                                     len(carr))
                        raise ValueError(msg)
                    for i in range(len(pyvalue)):
                        carr[i] = pyvalue[i]
                else:
                    # get datatype and cast the value
                    t = type(getattr(cparams, pykey))
                    setattr(cparams, pykey, t(pyvalue))
            else:
                msg = "{} params has no element {}".format(
                    type(cparams), pykey)
                raise ValueError(msg)
        return cparams

    # name, pyparams, out_info):
    def create_placeholder_node(self, input_tensor, placeholder_type, np_data):
        """
        Method for creating media placeholde node.

        """
        cparams = mpp.mediaPlaceholderParams()
        carr = getattr(cparams.shape, "dims")
        if(len(input_tensor.shape) > len(carr)):
            msg = "{}.{} length {} , expected {}".format(type(input_tensor.shape),
                                                         "dims",
                                                         len(input_tensor.shape),
                                                         MAX_DIMENSIONS_NUM)
            raise ValueError(msg)
        check_size = 1
        for i in range(len(input_tensor.shape)):
            cparams.shape.dims[i] = input_tensor.shape[i]
            check_size = check_size * input_tensor.shape[i]
        if(check_size == 0 or len(input_tensor.shape) == 0):
            raise ValueError("op {} output size is zero".format(
                input_tensor.src_op.name))
        cparams.shape.numDims = len(input_tensor.shape)

        cparams.output = self._struct_populator_(type(cparams.output),
                                                 input_tensor.src_op.out_info)
        cparams.layout = ''

        cparams.type = placeholder_type

        if(not np_data is None):
            cparams.dataPtr = np_data.__array_interface__['data'][0]
        else:
            cparams.dataPtr = 0x0

        ret = self._mm_.createPlaceHolder([],
                                          input_tensor.name,
                                          cparams,
                                          self._mg_)
        is_ok("createGenericNode", ret)

    def compile(self, decoder_op, hpu_graph):
        """
        Method for compiling media graph and generating recipe.

        """
        if(self._is_compiled_ == True):
            return
        # logic to generate nodes automatically
        for i in hpu_graph.input_tensors:
            if (i == decoder_op.output_tensors[0]):
                self.create_decoder_node(i)
            else:
                self.create_placeholder_node(
                    i, mpt.mediaPlaceholderType.NON_CONST_PLACEHOLDER, None)

        for c in hpu_graph.const_tensors:
            self.create_placeholder_node(
                c, mpt.mediaPlaceholderType.CONST_PLACEHOLDER, c.src_op())

        for op in hpu_graph.ops:
            self.create_ops_node(op)
        self._recipe_ = self._mm_.graphCompile(self._mg_)
        self._is_compiled_ = True

    def get_recipe(self):
        """
        Getter method to get media recipe.

        """

        if(self._is_compiled_ == True):
            return self._recipe_
        else:
            # TODO: check whats best for returning from here
            return None

    def __del__(self):
        """
        Destructor method.

        """
        # free any resources being used
        #ret = self._mm_.destroy()
        #is_ok("mm destroy", ret)
        pass  # TODO: check if _mm_.destroy() needed


#  this class is responsible for all runtime relatedmantaience in mediapipe
class pipe_manager():
    """
    Class defining media python to c interface for runtime handling.

    """

    def __init__(self, queue_depth, img_cwhb, framework, proxy,
                 python_proxy, output_tensors):
        """
        Constructor method.

        """
        self._batch_size_ = img_cwhb[3]
        self._rt_host_buf_tensor_node_ = []
        self._num_rt_host_bufs_ = 0
        self._cold_run_ = True
        self._queue_depth_ = queue_depth
        self._py_proxy_ = python_proxy
        self._fw_type_ = framework
        self.tensor_list = []
        self._graph_output_tensors_ = output_tensors
        self.get_ngops_buf_funcs = []
        self.get_var_buf_funcs = []
        self.reader_output_type = ro.FILE_LIST

        dma_nhgop_list = self._get_dma_nhgop_list_(output_tensors[1:])
        media_dtype = get_media_dtype(output_tensors[0].dtype)

        self._pm_ = mpa.pipeManager(queue_depth,
                                    img_cwhb[0],
                                    img_cwhb[1],
                                    img_cwhb[2],
                                    img_cwhb[3],
                                    framework,
                                    proxy,
                                    media_dtype,
                                    dma_nhgop_list)
        # this is only for run_hpu ctypes case
        self._pm_addr_ = self._pm_.get_ptr()

    def _get_dma_nhgop_list_(self, dma_ngop_bufs):
        """
        Method for generating list of no graph operation nodes.

        """
        nhgop_list = []
        for i in range(len(dma_ngop_bufs)):
            o = dma_ngop_bufs[i]
            metaDtype = mpa.metadata()
            metaDtype.dtype = get_media_dtype(o.dtype)
            metaDtype.numShapeDim = len(o.shape)
            check_size = 1
            for j in range(metaDtype.numShapeDim):
                metaDtype.shape[j] = o.shape[j]
                check_size = check_size * o.shape[j]
            if(check_size == 0 or metaDtype.numShapeDim == 0):
                raise ValueError("metadata {} has zero size!!!".format(i))
            nhgop_list.append(metaDtype)
        return nhgop_list

    def _gen_media_output_tensors_(self, outputs):
        """
        Method for generating list of output tensor nodes.

        """
        output_tensor = []
        for o in outputs:
            output_tensor.append(
                Tensor(o.shape, o.dtype, o.dtype))
        return output_tensor

    def acquire_device(self, device):
        """
        Method to acquire device

        """
        ret = self._pm_.acquireDevice(device)
        is_ok("acquireDevice", ret)

    def add_cpp_compute_node(self, metadata_processor):
        """
        Method to add a cpp compute node
        """
        self._pm_.add_cpp_compute_node(metadata_processor)

    def media_init(self, recipe, num_outputs, num_inputs):
        """
        Method to initialize media backend.

        """
        if(recipe == None):
            raise RuntimeError("receipe not found")
        # this will be default present since slice and reshape are always present
        # INFO: ws is always one as of now
        num_ws = 1
        ret = self._pm_.mediaMemAlloc(recipe,
                                      num_outputs,
                                      num_inputs,
                                      num_ws)
        is_ok("mediaMemAlloc", ret)

    def decoder_init(self, decoder_op):
        """
        Method to initialize decoder.

        """
        self.decoder_op = decoder_op
        params = decoder_op.params
        largest_file = decoder_op.input_tensors[0].src_op.get_largest_file()
        in_pic_fmt = mpt.MediaPictureFormat.MEDIA_IN_NV12
        out_pic_fmt = mpt.MediaPictureFormat.MEDIA_OUT_RGB_INTERLEAVED
        if(params['output_format'] == 'rgb-i'):
            out_pic_fmt = mpt.MediaPictureFormat.MEDIA_OUT_RGB_INTERLEAVED
        elif(params['output_format'] == 'rgb-p'):
            out_pic_fmt = mpt.MediaPictureFormat.MEDIA_OUT_RGB_PLANAR
        else:
            msg = "Media decoder pic format supported rgb-i rgb-p sent :{}.".format(
                out_pic_fmt)
            raise ValueError(msg)

        random_crop_param = mpa.mediaRandomCrop()
        random_crop_param.scale_min = params['scale_min']
        random_crop_param.scale_max = params['scale_max']
        random_crop_param.ratio_min = params['ratio_min']
        random_crop_param.ratio_max = params['ratio_max']
        random_crop_param.seed = params['seed']
        reader_op = self.decoder_op.input_tensors[0].src_op
        self.reader_output_type = reader_op.get_media_output_type()
        if(self.reader_output_type == ro.FILE_LIST):
            input_format = mpt.mediaInputType.FILE_LIST
        elif(self.reader_output_type == ro.BUFFER_LIST):
            input_format = mpt.mediaInputType.BUFFER_LIST
        elif(self.reader_output_type == ro.ADDRESS_LIST):
            input_format = mpt.mediaInputType.ADDRESS_LIST
        else:
            raise ValueError("invalid input format")

        random_crop_type = mpt.RandomCropType.NO_RANDOM_CROP
        if(params['random_crop_type'] == rct.NO_RANDOM_CROP):
            random_crop_type = mpt.RandomCropType.NO_RANDOM_CROP
        elif(params['random_crop_type'] == rct.PYT_RANDOM_CROP):
            random_crop_type = mpt.RandomCropType.PYT_RANDOM_CROP
        elif(params['random_crop_type'] == rct.TF_RANDOM_CROP):
            random_crop_type = mpt.RandomCropType.TF_RANDOM_CROP
        elif(params['random_crop_type'] == rct.CENTER_CROP):
            random_crop_type = mpt.RandomCropType.CENTER_CROP
        else:
            raise RuntimeError("wrong random crop type provided")

        ret = self._pm_.decoderMemInit(largest_file,
                                       input_format,
                                       in_pic_fmt,
                                       out_pic_fmt,
                                       params['resize'][0],
                                       params['resize'][1],
                                       params['filter'],
                                       random_crop_type,
                                       random_crop_param)

        is_ok("decoderMemInit", ret)

    def get_ordered_hpu_input_output_tensor_names(self):
        """
        Getter method to get list if input output tensors from receipe.

        """
        in_tensor_name = self._pm_.getInputTensorNames()
        out_tensor_name = self._pm_.getOutputTensorNames()
        return in_tensor_name, out_tensor_name

    def initialize_host_buffer(self):
        """
        Method to initialize host buffers for runtime.

        """
        #rt_host_buf_idx = np.array(rt_host_buf_idx)
        ret = self._pm_.initializeHostBuffer()
        is_ok("initializeHostBuffer", ret)

    def start_worker(self):
        """
        Method to start c worker.

        """
        ret = self._pm_.startPipelineExecutor()
        is_ok("startPipelineExecutor", ret)

    def init_iterator(self):
        """
        Method initialize iterator.

        """
        self.legacy = legacy(self._batch_size_)

    def run_hpu(self, input_list, rand_crp, var_np_buf, ngop_np_buf):
        """
        Method for performing execution on device.

        """
        output_0 = 0
        output_1 = []
        # if self._py_proxy_ is not None:
        if self._fw_type_ == mppy.fwType.PYTHON_FW:
            o = self._graph_output_tensors_[0]
            p = self._py_proxy_
            output_0 = p.new_tensor_dataptr(shape=o.np_shape, dtype=o.dtype)
            self.tensor_list.append(output_0)
            for i in range(1, len(self._graph_output_tensors_)):
                o = self._graph_output_tensors_[i]
                tensor_m = p.new_tensor_dataptr(
                    shape=o.np_shape, dtype=o.dtype)
                output_1.append(tensor_m)
                self.tensor_list.append(tensor_m)
        self.legacy.run_hpu(self._pm_addr_,
                            input_list,
                            self.reader_output_type,
                            rand_crp,
                            var_np_buf,
                            ngop_np_buf,
                            output_0,
                            output_1)

    def free_device_tensor(self, dev_addr):
        """
        Method to free device tensors.

        """
        # if self._py_proxy_ is not None:
        if self._fw_type_ == mppy.fwType.PYTHON_FW:
            self._py_proxy_.delete_tensor(dev_addr)
        elif self._fw_type_ == mppy.fwType.SYNAPSE_FW:
            self._pm_.freeRawDevBuffer(dev_addr)
        elif self._fw_type_ == mppy.fwType.TF_FW:
            pass
        else:
            raise RuntimeError("unknown FW type ", self._fw_type_)

    def get_output(self):
        """
        Method to catch the processed output from device.

        """
        outputs = self._pm_.getOutput()
        self.legacy.get_output()  # this is required to pop from the queue of legacy module

        tensorlist = []
        #print("Got get_output as ", outputs)
        for i in range(len(outputs)):
            # if self._py_proxy_ is not None:
            if self._fw_type_ == mppy.fwType.PYTHON_FW:
                self.tensor_list.remove(outputs[i])
            tensorlist.append(
                HPUTensor(self._graph_output_tensors_[i], outputs[i], self))
        return tensorlist

    def as_cpu(self, device_addr, npy_buf):
        """
        Method to perform device to host transfer.

        """
        pointer, read_only_flag = npy_buf.__array_interface__['data']
        ret = self._pm_.asCpu(device_addr, pointer, npy_buf.nbytes)
        is_ok("asCpu", ret)

    def flush_pipeline(self):
        """
        Method to flush pending command from the pipe.

        """
        ret = self._pm_.flushPipeline()
        is_ok("flushPipeline", ret)
        # if self._py_proxy_ is not None:
        if self._fw_type_ == mppy.fwType.PYTHON_FW:
            # TODO: check if tensor_list can be removed
            self._py_proxy_.flush_tensors(self.tensor_list)
            self.tensor_list.clear()

    def stop_worker(self):
        """
        Method to stop c worker.

        """
        ret = self._pm_.stopPipelineExecutor()
        is_ok("stopPipelineExecutor", ret)

    def free_host_buffer(self):
        """
        Method to free host buffers.

        """
        ret = self._pm_.freeHostBuffer()
        is_ok("freeHostBuffer", ret)

    def media_deinit(self):
        """
        Method to deinitialize media backend.

        """
        ret = self._pm_.mediaMemDealloc()
        is_ok("mediaMemDealloc", ret)

    def decoder_deinit(self):
        """
        Method to deinitialize decoder.

        """
        ret = self._pm_.decoderMemDealloc()
        is_ok("decoderMemDealloc", ret)

    def release_device(self):
        """
        Method to release device.

        """
        ret = self._pm_.releaseDevice()
        is_ok("releaseDevice", ret)
