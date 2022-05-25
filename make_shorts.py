import sys
sys.path.append('./Face_Recognition')
sys.path.append('./Laughter')
sys.path.append('./utils')
import config
from laughter_detector import LaughterDetector
from face_recog import FaceRecognizer
from final_timeline import make_final_timeline

##### load config #####
cfg = config.CONFIG

##### laughter detetcion #####
detector = LaughterDetector(video_path=cfg['file_path']['mp4_path'],
    wav_path=cfg['file_path']['wav_path'],
    model_cfg=cfg['laughter_detection']['resnet_with_augmentation'])

# save wav from mp4
detector.mp4_to_wav()

# find laughter interval
laugh_output, length = detector.get_output()

# make timeline and add features for interest
laughter_timeline = detector.make_laugh_timeline(laugh_output,length)

# calculate interest and make laughter timeline
final_laughter_timeline = detector.calculate_interest(laughter_timeline)


##### face recognition #####
recognizer = FaceRecognizer(video_path=cfg['file_path']['mp4_path'],
    target_path=cfg['file_path']['target_img_path'],
    model_cfg=cfg['face_recognition'])

# save frame numbers from video
output_frames = recognizer.recognize_faces()

# make timeline from output frames per each person
people_timeline = recognizer.make_people_timeline(output_frames)


##### make shorts #####
shorts = []

for target_person_timeline in people_timeline:
    final_timeline = make_final_timeline(final_laughter_timeline,target_person_timeline)
    shorts.append(final_timeline)

print('Finished!')
print(shorts)