import config as configs_laugh
from laughter_detector.laughter_detector import LaughterDetector
import os


def LaughterDetection(video_path: str = "", wav_path: str = "", ml_path: str = ""):

    cfg = configs_laugh.CONFIG

    cfg['laughter_detection']['resnet_with_augmentation']['model_path'] \
        = os.path.join(ml_path, cfg['laughter_detection']['resnet_with_augmentation']['model_path'])

    detector = LaughterDetector(video_path=video_path,
        wav_path=wav_path,
        model_cfg=cfg['laughter_detection']['resnet_with_augmentation'])

    # save wav from mp4
    detector.mp4_to_wav()

    # find laughter interval
    laugh_output, length = detector.get_output()

    # make timeline and add features for interest
    laughter_timeline = detector.make_laugh_timeline(laugh_output,length)

    # calculate interest and make final timeline
    final_laughter_timeline = detector.calculate_interest(laughter_timeline)

    return final_laughter_timeline
