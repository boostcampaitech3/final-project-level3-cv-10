from ml.face_extractor.face_extractor import FaceExtractor
import face_recognition
from ml.face_extractor.person_db import Person
from ml.utils import load_json

'''
This module is config-based: Modify config.json for different experiments
'''

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

    # 초기화
    # Person._last_id = 0