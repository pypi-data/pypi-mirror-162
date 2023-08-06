from habana_frameworks.mediapipe.backend.operator_specs import schema
from habana_frameworks.mediapipe.operators.cpu_nodes.cpu_nodes import media_constants, media_dummy, media_func_data, media_ext_cpu_op
from habana_frameworks.mediapipe.media_types import dtype as dt
from habana_frameworks.mediapipe.operators.cpu_nodes.cpu_node_params import *
import media_pipe_params as mpp  # NOQA

schema.add_operator("MediaDummy", None, 0, 0, 1,
                    empty_params, None, media_dummy, None)

schema.add_operator("MediaConst", None, 0, 0, 1,
                    media_constant_params, None, media_constants, dt.UINT8)

schema.add_operator("MediaFunc", None, 0, 4, 1,
                    media_func_params, None, media_func_data, dt.UINT8)

schema.add_operator("MediaExtCpuOp", None, 0, 10, None,
                    media_ext_cpu_op_params, None, media_ext_cpu_op, dt.UINT8)
