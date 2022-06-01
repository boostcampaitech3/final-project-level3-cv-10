from face_extractor.face_extractor import FaceExtractor
import face_recognition
from utils import load_json

'''
This module is config-based: Modify config.json for different experiments
'''

# Load config
cfg = load_json('config.json')

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
