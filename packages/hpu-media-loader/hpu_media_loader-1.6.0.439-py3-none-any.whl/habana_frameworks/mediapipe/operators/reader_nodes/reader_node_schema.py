from habana_frameworks.mediapipe.backend.operator_specs import schema
from habana_frameworks.mediapipe.operators.reader_nodes.coco_reader import coco_reader
from habana_frameworks.mediapipe.operators.reader_nodes.read_image_from_dir import read_image_from_dir
from habana_frameworks.mediapipe.operators.reader_nodes.read_image_jpeg import read_image_jpeg_sanity
from habana_frameworks.mediapipe.operators.reader_nodes.read_image_from_dir_buf import read_image_from_dir_buffer
from habana_frameworks.mediapipe.operators.reader_nodes.reader_nodes import media_ext_reader_op
from habana_frameworks.mediapipe.operators.reader_nodes.reader_node_params import *

import media_pipe_params as mpp  # NOQA


# add operators to the list of supported ops
# schema.add_operator(oprator_name,guid, min_inputs,max_inputs,num_outputs,params_of_operator)

schema.add_operator("MediaExtReaderOp", None, 0, 0, 1,
                    media_ext_reader_op_params, None, media_ext_reader_op, dt.NDT)

schema.add_operator("ReadImageDatasetFromDir", None, 0, 0,
                    2, read_image_from_dir_params, None, read_image_from_dir, dt.NDT)

schema.add_operator("ReadImageJpegSanity", None, 0, 0,
                    2, read_image_from_dir_params, None, read_image_jpeg_sanity, dt.NDT)

schema.add_operator("ReadImageDatasetFromDirBuffer", None, 0, 0,
                    2, read_image_from_dir_params, None, read_image_from_dir_buffer, dt.NDT)

schema.add_operator("CocoReader", None, 0, 0,
                    7, coco_reader_params, None, coco_reader, dt.NDT)
