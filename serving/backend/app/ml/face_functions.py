from ml.face_extractor.face_extractor import FaceExtractor
from ml.face_extractor.person_db import Person

from ml.face_recognizer.face_recog import FaceRecognizer

from ml.final_shorts.final_timeline import make_final_timeline
from ml.final_shorts.make_shorts import make_shorts

from ml.utils import load_json

import numpy as np
import os

'''
This module is config-based: Modify config.json for different experiments
'''

########## Face Clustering ############
def FaceClustering(video_path: str = "", save_dir:str = ""):
    # Load config
    # cfg = load_json('./ml/config.json')

    # Initialize Face Extractor
    extractor = FaceExtractor(
        video_path=video_path,
        data_dir=None,
        result_dir=save_dir,
        threshold=0.63,
        face_cnt=250
    )

    # Extract Faces
    final_clusters = extractor.cluster_video()

    np.save(os.path.join(save_dir, 'result.npy'), final_clusters)

    # Show results
    extractor.summarize_results()



########## Face Recognition ############
def FaceRecognition(video_path: str="", target_people: list=[], result_path: str=""):

    result_data = np.load(result_path, allow_pickle=True).item()
    target_encoding = [result_data[person]['repr_encoding'] for person in target_people]

    # Initialize Face Recognizor
    recognizer = FaceRecognizer(video_path, target_encoding=target_encoding)
    
    # save frame numbers from video
    timelines, output_frames = recognizer.recognize_faces()

    # make timeline from output frames per each person
    people_timeline = recognizer.make_people_timeline(timelines, output_frames, target_people)

    return people_timeline



########## Final Timeline ############
def FinalTimeline(laugh_timeline : list, people_timeline : dict, id : str):
    # shorts = []

    shorts = []
    for target_person in iter(people_timeline.keys()):
        print(target_person)
        print(people_timeline[target_person])
        if people_timeline[target_person] == [[]]:
            continue
        final_timeline, total_length = make_final_timeline(laugh_timeline, people_timeline[target_person])
        
        target_person_shorts = make_shorts(final_timeline, total_length, id, target_person)

        if len(target_person_shorts) > 0:
            for target_person_short in target_person_shorts:
                shorts.append(target_person_short)
            
    return shorts

    # return shorts