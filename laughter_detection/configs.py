import models, audio_utils
from functools import partial

CONFIG = {}

CONFIG['laughter_detector'] = {
    'resnet_with_augmentation':{
    'model_path': '/opt/ml/project/laughter/checkpoints/in_use/resnet_with_augmentation',
    'model': models.ResNetBigger,
    'feature_fn': partial(audio_utils.featurize_melspec, hop_length=186),
    'linear_layer_size': 128,
    'filter_sizes': [128,64,32,32],
    'expand_channel_dim': True,
    'threshold': 0.75,
    'min_length': 1
    }
    
}

CONFIG['file_path'] = {
    'mp4_path': '/opt/ml/project/input_dir/video/testvideo_2.mp4',
    'wav_path': '/opt/ml/project/input_dir/wav/testwav_7'
}