from .laughter_detector import models
from .utils import audio_utils
from functools import partial

CONFIG = {}

CONFIG['laughter_detection'] = {
    'resnet_with_augmentation':{
    'model_path': 'laughter_detector/checkpoints/in_use/resnet_with_augmentation',
    'model': models.ResNetBigger,
    'feature_fn': partial(audio_utils.featurize_melspec, hop_length=186),
    'linear_layer_size': 128,
    'filter_sizes': [128,64,32,32],
    'expand_channel_dim': True,
    'threshold': 0.75,
    'min_length': 1
    }
}
