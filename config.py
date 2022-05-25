import models, audio_utils
from functools import partial

CONFIG = {}

CONFIG['file_path'] = {
    'wav_path': '/opt/ml/project/input_dir/wav/testwav_7',
    'mp4_path': '/opt/ml/project/input_dir/video/testvideo_2.mp4',
    'target_img_path': ['/opt/ml/project/input_dir/face/dongmin.png','/opt/ml/project/input_dir/face/seyun.jpg']
}

CONFIG['face_recognition'] = {
    'check_frame': 16,
    'batch_size': 16
}

CONFIG['laughter_detection'] = {
    'resnet_with_augmentation':{
    'model_path': '/opt/ml/project/Laughter/checkpoints/in_use/resnet_with_augmentation',
    'model': models.ResNetBigger,
    'feature_fn': partial(audio_utils.featurize_melspec, hop_length=186),
    'linear_layer_size': 128,
    'filter_sizes': [128,64,32,32],
    'expand_channel_dim': True,
    'threshold': 0.75,
    'min_length': 1
    }
}