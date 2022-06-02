import os.path as osp
import os
import sys
sys.path.append('./laughter')
from laughter_detection import LaughterDetection
from face_extractor.face_extractor import FaceExtractor
from recognition.face_recog import FaceRecognizer
from final_shorts import final_timeline, make_shorts
from moviepy.editor import *

# assgin file path
VIDEO_PATH = '/opt/ml/project/input_dir/video/testvideo_3_1.mp4'
WAV_PATH = '/opt/ml/project/input_dir/wav/testwav_3_1'
LAUGHTER_MODEL_PATH = '/opt/ml/project/model/laughter'
CLUSTER_IMG_SAVE_PATH = '/opt/ml/project/output_dir/cluster/testwav_3_1'
SHORTS_SAVE_PATH = '/opt/ml/project/output_dir/shorts/'
SHORTS_NAME = 'RadioStar_EP00_'


# laughter detection
shorts_timeline = LaughterDetection(video_path=VIDEO_PATH, wav_path=WAV_PATH, ml_path=LAUGHTER_MODEL_PATH)


# clustering
extractor = FaceExtractor(VIDEO_PATH,None,CLUSTER_IMG_SAVE_PATH,threshold=0.57,face_cnt=200)

fingerprints = extractor.extract_fingerprints()
clusters = extractor.cluster_fingerprints(fingerprints)
merged_clusters = extractor.merge_clusters(clusters,fingerprints)
final_cluster_results = extractor.get_final_dict()


# recognition
target_people = ['person_0', 'person_1']
target_encoding = [final_cluster_results[person]['repr_encoding'] for person in target_people]

recognizer = FaceRecognizer(VIDEO_PATH, target_encoding=target_encoding)
timelines, output_frames = recognizer.recognize_faces()
people_timeline = recognizer.make_people_timeline(timelines, output_frames)


# make final shorts timeline
shorts = []
for target_person_timeline in people_timeline:
    final_shorts_timeline = make_final_timeline(shorts_timeline,target_person_timeline)
    shorts.append(final_shorts_timeline)
    
    
# save shorts
if not osp.isdir(SHORTS_SAVE_PATH):
    os.makedirs(SHORTS_SAVE_PATH)

for short in shorts:
    if short[1] > 0:
        for ind,(start,end,_,_) in enumerate(short[0]):
            SHORTS_PATH = SHORTS_SAVE_PATH + SHORTS_NAME + str(ind) + '.mp4'
            video = VideoFileClip(VIDEO_PATH).subclip(start,end).fx(vfx.fadein,1).fx(vfx.fadeout,1)
            video.write_videofile(SHORTS_PATH)