from habana_frameworks.mediapipe.media_types import dtype as dt
from habana_frameworks.mediapipe.backend.operator_specs import schema
from habana_frameworks.mediapipe.media_types import dtype as dt
from habana_frameworks.mediapipe.operators.hpu_nodes.hpu_nodes import *
from habana_frameworks.mediapipe.operators.hpu_nodes.hpu_node_params import *

import media_pipe_params as mpp  # NOQA


# add operators to the list of supported ops
# schema.add_operator(oprator_name,guid, min_inputs,max_inputs,num_outputs,params_of_operator)
schema.add_operator("Resize", 'resize_image', 1, 1, 1,
                    resize_params, mpp.resizeParams, media_hpu_ops, dt.UINT8)

schema.add_operator("ColorSpaceConversion", 'color_space_conversion',
                    1, 1, 1, color_space_params, mpp.colorSpaceConversionParams, media_hpu_ops, dt.UINT8)

schema.add_operator("Crop", 'crop',
                    1, 1, 1, crop_params, mpp.cropParams, media_hpu_ops, dt.UINT8)

schema.add_operator("CropMirrorNorm", 'crop_mirror_norm',
                    3, 3, 1, cmn_params, mpp.cropMirrorNormParams, media_hpu_ops, dt.UINT8)

schema.add_operator("Reshape", 'reshape',
                    1, 1, 1, reshape_params, mpp.mediaReshapeNdParams, media_hpu_ops, dt.UINT8)

schema.add_operator("Contrast", 'contrast',
                    1, 2, 1, contrast_params, mpp.contrastParams, media_hpu_ops, dt.UINT8)

schema.add_operator("Brightness", 'brightness',
                    1, 2, 1, brightness_params, mpp.brightnessParams, media_hpu_ops, dt.UINT8)

schema.add_operator("Saturation", 'saturation',
                    1, 2, 1, saturation_params, mpp.saturationParams, media_hpu_ops, dt.UINT8)

schema.add_operator("Transpose", 'transpose', 1, 1, 1,
                    transpose_params, mpp.transposeParams, media_hpu_ops, dt.UINT8)

schema.add_operator("Slice", 'slice', 1, 1, 1,
                    slice_params, mpp.mediaSliceParams, media_hpu_ops, dt.UINT8)

schema.add_operator("Constant", 'constant', 1, 1, 1,
                    empty_params, mpp.mediaConstantParams, media_hpu_ops, dt.UINT8)

schema.add_operator("MemCpy", 'memcpy', 1, 1, 1,
                    empty_params, mpp.mediaCopyParams, media_hpu_ops, dt.UINT8)

schema.add_operator("Cast", 'cast', 1, 1, 1,
                    cast_params, mpp.mediaCastParams, media_hpu_ops, dt.FLOAT32)

schema.add_operator("BitwiseOr", 'bitwise_or', 2, 2, 1,
                    empty_params, mpp.bitwiseBinaryParams, media_hpu_ops, dt.UINT8)

schema.add_operator("BitwiseAnd", 'bitwise_and', 2, 2, 1,
                    empty_params, mpp.bitwiseBinaryParams, media_hpu_ops, dt.UINT8)

schema.add_operator("BitwiseXor", 'bitwise_xor', 2, 2, 1,
                    empty_params, mpp.bitwiseBinaryParams, media_hpu_ops, dt.UINT8)

schema.add_operator("GatherND", "gather_nd", 2, 2,
                    1, empty_params, mpp.mediaGatherParams, media_hpu_ops, dt.UINT8)

schema.add_operator("Add", 'add', 2, 2, 1,
                    empty_params, mpp.mediaArithmeticParams, media_hpu_ops, dt.UINT8)

schema.add_operator("Neg", 'neg', 1, 1, 1,
                    empty_params, mpp.mediaArithmeticParams, media_hpu_ops, dt.INT8)  # TODO: To test

schema.add_operator("Mult", 'mult', 2, 2, 1,
                    empty_params, mpp.mediaArithmeticParams, media_hpu_ops, dt.UINT8)

schema.add_operator("Sub", 'sub', 2, 2, 1,
                    empty_params, mpp.mediaArithmeticParams, media_hpu_ops, dt.UINT8)

schema.add_operator("RandomFlip", "random_flip", 2, 2,
                    1, flip_params, mpp.flipParams, media_hpu_ops, dt.UINT8)

schema.add_operator("RandomBernoulli", "random_bernoulli", 1, 1,
                    1, random_bernoulli_params, mpp.mediaRandomBernoulliParams, media_hpu_ops, dt.UINT8)

schema.add_operator("Flip", "flip_3d", 1, 1,
                    1, flip_params, mpp.flipParams, media_hpu_ops, dt.UINT8)

schema.add_operator("Normalize", "normalize", 1, 1,
                    1, normalize_params, mpp.normalizeParams, media_hpu_ops, dt.UINT8)

schema.add_operator("Hue", "hue", 1, 2,
                    1, hue_params, mpp.hueParams, media_hpu_ops, dt.UINT8)
# TODO: enable rotate once synapse has the fix for default constructor
# schema.add_operator("ImageRotate", 'image_rotate',
#                    1, 1, 1, image_rotate_params, mpp.mediaRotateParams, media_hpu_ops, dt.UINT8)

schema.add_operator("FrameRateReduction", "frame_rate_reduction", 1, 1,
                    1, frr_params, mpp.FrameRateReductionParams, media_hpu_ops, dt.UINT8)
