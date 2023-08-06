from habana_frameworks.mediapipe.media_types import readerOutType as ro
from ctypes import *

MEDIA = CDLL("libmedia.so")

media_error = {
    0: "mediaSuccess",
    -1: "mediaFail",
    -2: "mediaInvalidArgument",
    -3: "mediaNotSupported",
    -4: "mediaEndOfFile"
}


class FileList(Structure):
    _fields_ = [('filePath', POINTER(c_char_p))]


class BufferList(Structure):
    _fields_ = [('bufferAddr', POINTER(c_char_p)),
                ('bufferSizes', POINTER(c_uint32))]


class InputTypeList(Union):
    _fields_ = [('fileList', FileList),
                ('bufferList', BufferList)]


class InputList(Structure):
    _fields_ = [('list', InputTypeList),
                ('listSize', c_int)]


class MediaCrop (Structure):
    _fields_ = [('crop_x', c_double),
                ('crop_y', c_double),
                ('crop_width', c_double),
                ('crop_height', c_double)]


unknown_error = -len(media_error)
media_success = 0


def is_ok(func, status):
    """
    Method to check backend return status.

    :params func_name: function name as string.
    :params status: return status of backend code.
    :raises RuntimeError: if status is failure.
    """

    if (status <= unknown_error) or (status > 0):
        print("Error Code = ", status)
        raise RuntimeError("Media API {} failed! Error Code = {}.".format(
            func.__name__, "mediaErrorUnknown"))
    elif status != media_success:
        raise RuntimeError("Media API {} failed! Error Code = {}.".format(
            func.__name__, media_error[status]))
    else:
        #logger.LOG_TRACE("{}(): Success.".format(func.__name__))
        pass


class legacy:
    """
    Class defining legacy mediapipe backend interface.

    """

    def __init__(self, batch_size):
        """
        Constructor method.

        :params batch_size: batch size.
        """
        self.batch_size = batch_size
        self.run_hpu_q = []
        self.max_queue_size = 3  # limited by codec

    def run_hpu(self, pipeManager, input_list, input_type, rand_crp, host_buffer, bypass_host_buffers, out_dev_buffer, meta_dev_buf_list):
        """
        Method invoke on device execution.

        """
        mediaPipelineRunHpu = MEDIA.mediaPipelineRunHpu
        mediaPipelineRunHpu.restypes = c_int
        mediaPipelineRunHpu.argtypes = [c_void_p,
                                        POINTER(InputList),
                                        POINTER(MediaCrop),
                                        POINTER(c_void_p),
                                        POINTER(c_void_p),
                                        c_uint64,
                                        POINTER(c_uint64)]
        ctx = None
        itl = InputTypeList()
        if(input_type == ro.FILE_LIST):
            fl_arr = (c_char_p * (len(input_list) + 1))()
            for i in range(len(input_list)):
                fl_arr[i] = bytes(input_list[i], 'utf-8')
            fl = FileList(fl_arr)
            itl.fileList = fl
        elif(input_type == ro.BUFFER_LIST):
            bl_arr = (c_char_p * (len(input_list) + 1))()
            size_arr = (c_uint32 * (len(input_list) + 1))()
            for i in range(len(input_list)):
                bl_arr[i] = input_list[i].__array_interface__['data'][0]
                # INFO: sizes must be multiple of 64
                # size_arr[i] = ((len(input_list[i]) + 63) & (-64))
                size_arr[i] = len(input_list[i])
                #print("{} addr {} len {}".format(i,input_list[i].__array_interface__['data'][0],len(input_list[i])))

            bl = BufferList(bl_arr,
                            size_arr)
            itl.bufferList = bl
            ctx = input_list
        elif(input_type == ro.ADDRESS_LIST):
            bl_arr = (c_char_p * (len(input_list) + 1))()
            size_arr = (c_uint32 * (len(input_list) + 1))()
            for i in range(len(input_list)):
                addr = bytes(input_list[i][0], 'utf-8')
                bl_arr[i] = addr
                size_arr[i]= input_list[i][1]
                #print("{} addr {} len {}".format(i,bl_arr[i],size_arr[i]))
            bl = BufferList(bl_arr,
                            size_arr)
            itl.bufferList = bl
            ctx = input_list
        else:
            raise ValueError("unsupported input type")

        il = InputList(itl, len(input_list))
        # start_time1 =  time.perf_counter()
        if (rand_crp is None):
            crop_param_array = 0
        else:
            crop_param_array = (MediaCrop * self.batch_size)()
            for i in range(self.batch_size):
                crop_param_array[i].crop_x = c_double(rand_crp[i][0])
                crop_param_array[i].crop_y = c_double(rand_crp[i][1])
                crop_param_array[i].crop_width = c_double(rand_crp[i][2])
                crop_param_array[i].crop_height = c_double(rand_crp[i][3])

        #start_time2 =  time.perf_counter()
        # INFO: +1 is for accomodating decoder input
        num_host_buffer = len(host_buffer) + 1
        hb_pp = (c_void_p * (num_host_buffer))()
        hb_pp[0] = c_void_p(0)
        for i in range(num_host_buffer - 1):
            pointer = host_buffer[i].__array_interface__['data'][0]
            hb_pp[i + 1] = c_void_p(pointer)

        num_bypass_buffers = len(bypass_host_buffers)
        byp_hb_pp = (c_void_p * num_bypass_buffers)()
        for i in range(num_bypass_buffers):
            pointer = bypass_host_buffers[i].__array_interface__['data'][0]
            byp_hb_pp[i] = c_void_p(pointer)
        #start_time3 =  time.perf_counter()

        cmeta_dev_buf_list = (c_uint64 * len(meta_dev_buf_list))()
        for i in range(len(meta_dev_buf_list)):
            cmeta_dev_buf_list[i] = c_uint64(meta_dev_buf_list[i])

        self.run_hpu_q.append(il)
        self.run_hpu_q.append(ctx)
        self.run_hpu_q.append(crop_param_array)
        err = mediaPipelineRunHpu(c_void_p(pipeManager),
                                  byref(il),
                                  cast(crop_param_array, POINTER(MediaCrop)),
                                  hb_pp,
                                  byp_hb_pp,
                                  c_uint64(out_dev_buffer),
                                  cmeta_dev_buf_list)
        is_ok(mediaPipelineRunHpu, err)
        #end_time = time.perf_counter()

        # print("================================")
        # print("inside run_hpu")
        # print("Time Elapsed total = " , (end_time - start_time0))
        #print("Time Elapsed filelist = " , (start_time1 - start_time0))
        #print("Time Elapsed crop = " , (start_time2 - start_time1))
        #print("Time Elapsed rtbuffers = " , (start_time3 - start_time2))
        #print("Time Elapsed c api = " , (end_time - start_time3))
        # print("================================")

    def get_output(self):
        """
        Method to getoutput. Here it is responsible for clearing the cache held.

        """
        self.run_hpu_q.pop(0)
        self.run_hpu_q.pop(0)
        self.run_hpu_q.pop(0)
        if(len(self.run_hpu_q) > (3*self.max_queue_size)):
            raise RuntimeError("Hpu queue overflow")
