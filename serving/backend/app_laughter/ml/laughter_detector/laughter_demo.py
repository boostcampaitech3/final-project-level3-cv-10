import sys
sys.path.append('./utils')
sys.path.append('./laughter_detector')
import configs_laugh
from laughter_detector import LaughterDetector


cfg = configs_laugh.CONFIG

detector = LaughterDetector(video_path=cfg['file_path']['mp4_path'],
    wav_path=cfg['file_path']['wav_path'],
    model_cfg=cfg['laughter_detector']['resnet_with_augmentation'])

# save wav from mp4
detector.mp4_to_wav()

# find laughter interval
laugh_output, length = detector.get_output()

# make timeline and add features for interest
laughter_timeline = detector.make_laugh_timeline(laugh_output,length)

# calculate interest and make final timeline
final_laughter_timeline = detector.calculate_interest(laughter_timeline)
print(final_laughter_timeline)
