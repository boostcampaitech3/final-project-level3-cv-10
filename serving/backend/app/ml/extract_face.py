from ml.face_extractor.face_extractor import FaceExtractor
import face_recognition
from ml.utils import load_json

import os

'''
This module is config-based: Modify config.json for different experiments
'''

def execute_face_extractor(dir_path, uuid):

    # Load config
    cfg = load_json(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
, 'ml', 'config.json'))
    video_dir = os.path.join(dir_path, uuid)
    cfg['data_dir'] = video_dir
    result_dir = os.path.join(video_dir, 'result')
    os.makedirs(result_dir)
    cfg['face_extractor']['save_dir'] = result_dir
    for f in os.listdir(video_dir):
        file_name = os.path.splitext(f)[0]
        if file_name == 'original':
            cfg['input_video_path'] = os.path.join(video_dir, f)
            break

    # Initialize Face Extractor
    extractor = FaceExtractor(
        video_path=cfg['input_video_path'],
        data_dir=cfg['data_dir'],
        **cfg['face_extractor']
    )

    # Extract Faces
    pdb = extractor.extract_faces()

    # Show results
    extractor.summarize_results()

    # Use pdb for further applications !
    # You can see how to get encoding/name/etc from summarize_results() above
