from moviepy.editor import *
import ffmpeg

from google.cloud import storage
storage_client = storage.Client()
bucket_name = 'snowman-bucket'
bucket = storage_client.bucket(bucket_name)

import os

def make_shorts(final_highlights, total_length, id, target_person):
    print("Making Shorts....")
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    FILE_DIR = os.path.join(BASE_DIR, 'files/')

    SHORTS_DIR = os.path.join(FILE_DIR, id, 'shorts')
    SHORTS_STORAGE_DIR = os.path.join(id, 'shorts')
    os.makedirs(SHORTS_DIR, exist_ok=True)
    

    VIDEO_DIR = os.path.join(FILE_DIR, id, "original.mp4")
    print(VIDEO_DIR)

    CURRENT_DIR = os.getcwd()

    in_file = ffmpeg.input(VIDEO_DIR)

    target_person_shorts = []
    for idx, (start, end, interest, during) in enumerate(final_highlights):
        print("Making Clips...")
        HIGHLIGHT_PATH = os.path.join(SHORTS_DIR, f"short_{target_person}_{idx}.mp4")

        # save to gcs
        HIGHLISHT_STORAGE_DIR = os.path.join(SHORTS_STORAGE_DIR, f"short_{target_person}_{idx}.mp4")
        blob = bucket.blob(HIGHLISHT_STORAGE_DIR)

        vid = (
            in_file.video
            .trim(start=start, end=end)
            .setpts('PTS-STARTPTS')
        )
        aud = (
            in_file.audio
            .filter_('atrim', start=start, end=end)
            .filter_('asetpts', 'PTS-STARTPTS')
        )
        joined = ffmpeg.concat(vid, aud, v=1, a=1).node
        output = ffmpeg.output(joined[0], joined[1], HIGHLIGHT_PATH)
        output.run()

        # clip = VideoFileClip(VIDEO_DIR).subclip(start,end).fx(vfx.fadein,1).fx(vfx.fadeout,1)        
        
        # os.chdir(SHORTS_DIR) # for saving [video-name]TEMP_MPY_wvf_snd.mp3 file in files/[uuid]/shorts
        # clip.write_videofile(HIGHLIGHT_PATH)
        # os.chdir(CURRENT_DIR) # come back to original directory

        blob.upload_from_filename(HIGHLIGHT_PATH)

        target_person_shorts.append([target_person, HIGHLISHT_STORAGE_DIR, during, interest])

    return target_person_shorts