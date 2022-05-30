from ml.face_extractor.face_extractor import FaceExtractor
from ml.face_extractor.person_db import Person

from ml.face_recognizer.face_recog import FaceRecognizer

from ml.final_shorts.final_timeline import make_final_timeline
from ml.final_shorts.make_shorts import make_shorts

from ml.utils import load_json

'''
This module is config-based: Modify config.json for different experiments
'''

########## Face Clustering ############
def FaceClustering(video_path: str = "", data_dir:str = "", save_dir:str = ""):
    # Load config
    cfg = load_json('./ml/config.json')

    # Initialize Face Extractor
    extractor = FaceExtractor(
        video_path=video_path,
        data_dir=data_dir,
        save_dir=save_dir,
        **cfg['face_extractor']
    )

    # Extract Faces
    pdb = extractor.extract_faces()

    # Show results
    extractor.summarize_results()


########## Face Recognition ############
def FaceRecognition(video_path: str="", target_path: str=""):
    # Load config
    cfg = load_json('./ml/config.json')

    # Initialize Face Recognizor
    recognizer = FaceRecognizer(video_path=video_path,
    target_path=target_path,
    model_cfg=cfg['face_recognition'])

    # save frame numbers from video
    output_frames = recognizer.recognize_faces()

    # make timeline from output frames per each person
    people_timeline = recognizer.make_people_timeline(output_frames)

    return people_timeline



########## Final Timeline ############
def FinalTimeline(laugh_timeline, people_timeline, id):
    # shorts = []

    for target_person_timeline in people_timeline:
        final_timeline, total_length = make_final_timeline(laugh_timeline, target_person_timeline)
        # print("final_timeline : ")
        # print(final_timeline)
        # print(total_length)
        # shorts.append(final_timeline)
        make_shorts(final_timeline, total_length, id)

    return "Done"

    # return shorts