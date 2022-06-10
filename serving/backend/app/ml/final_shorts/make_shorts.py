from moviepy.editor import *

from google.cloud import storage
storage_client = storage.Client()
bucket_name = 'snowman-bucket'
bucket = storage_client.bucket(bucket_name)

import os
import ffmpeg

def make_shorts(final_highlights, total_length, id, target_person):
    print("Making Shorts....")
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    FILE_DIR = os.path.join(BASE_DIR, 'files/')

    SHORTS_DIR = os.path.join(FILE_DIR, id, 'shorts')
    SHORTS_STORAGE_DIR = os.path.join(id, 'shorts')
    os.makedirs(SHORTS_DIR, exist_ok=True)
    
    VIDEO_DIR = os.path.join(FILE_DIR, id, "original.mp4")

    in_file = ffmpeg.input(VIDEO_DIR)

    target_person_shorts = []
    for idx, (start, end, interest, ratio, during) in enumerate(final_highlights):
        HIGHLIGHT_PATH = os.path.join(SHORTS_DIR, f"short_{target_person}_{idx}.mp4")

        # save to gcs
        HIGHLIGHT_STORAGE_DIR = os.path.join(SHORTS_STORAGE_DIR, f"short_{target_person}_{idx}.mp4")
        blob = bucket.blob(HIGHLIGHT_STORAGE_DIR)

        vid = (
            in_file.video
            .trim(start=start, end=end)
            .fade(type="in", start_time=start, duration=1)
            .fade(type="out", start_time=end-1, duration=1)
            .setpts('PTS-STARTPTS')
        )
        aud = (
            in_file.audio
            .filter_('atrim', start=start, end=end)
            .filter_('afade', type='in', start_time=start, duration=1)
            .filter_('afade', type='out', start_time=end-1, duration=1)
            .filter_('asetpts', 'PTS-STARTPTS')
        )
        joined = ffmpeg.concat(vid, aud, v=1, a=1).node
        output = ffmpeg.output(joined[0], joined[1], HIGHLIGHT_PATH)
        output.run()

        blob.upload_from_filename(HIGHLIGHT_PATH)

        target_person_shorts.append([target_person, HIGHLIGHT_STORAGE_DIR, during, interest])

    return target_person_shorts
