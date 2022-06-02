from face_extractor.face_extractor import FaceExtractor
import os
import os.path as osp

if not osp.isdir('/opt/ml/input/final-project-level3-cv-10/scene_detection_imgs'):
    os.makedirs('/opt/ml/input/final-project-level3-cv-10/scene_detection_imgs')

extractor = FaceExtractor(
    '/opt/ml/input/final-project-level3-cv-10/data/sample1_0-300s.mp4',
    '/opt/ml/input/final-project-level3-cv-10/data/',
    '/opt/ml/input/final-project-level3-cv-10/result',
    threshold=0.57,
    face_cnt=200
)

import face_recognition

def check_use_gpu(TARGET_IMG_PATH):
    image = face_recognition.load_image_file(TARGET_IMG_PATH)
    face_locations = face_recognition.face_locations(image,model='cnn')
    if len(face_locations) > 0:
        print('Using GPU')
    else:
        print('***Not using GPU***')

TARGET_IMG_PATH = "/opt/ml/input/final-project-level3-cv-10/data/img1.png"
check_use_gpu(TARGET_IMG_PATH)


fingerprints = extractor.extract_fingerprints()
clusters = extractor.cluster_fingerprints(fingerprints)
print(clusters)
