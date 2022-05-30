from moviepy.editor import *
import os

def make_shorts(final_highlights, total_length, id):
    print("Making Shorts....")
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    FILE_DIR = os.path.join(BASE_DIR, 'files/')

    SHORTS_DIR = os.path.join(FILE_DIR, id, 'shorts')
    os.mkdir(SHORTS_DIR)

    VIDEO_DIR = os.path.join(FILE_DIR, id, "original.mp4")
    print(VIDEO_DIR)

    for idx, (start, end, interest, _) in enumerate(final_highlights):
        print("Making Clips...")
        HIGHLIGHT_PATH = os.path.join(SHORTS_DIR, f"short_{idx}.mp4")
        clip = VideoFileClip(VIDEO_DIR).subclip(start,end).fx(vfx.fadein,1).fx(vfx.fadeout,1)
        clip.write_videofile(HIGHLIGHT_PATH)

    return