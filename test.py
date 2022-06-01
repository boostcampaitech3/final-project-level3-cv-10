from face_extractor.face_extractor_2 import FaceExtractor

extractor = FaceExtractor(
    '/opt/ml/input/final-project-level3-cv-10/data/sample1_0-300s.mp4',
    '/opt/ml/input/final-project-level3-cv-10/data/',
    '/opt/ml/input/final-project-level3-cv-10/result'
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
print(fingerprints)
#  clusters = extractor.cluster_fingerprints(fingerprints)
#  print(clusters)
