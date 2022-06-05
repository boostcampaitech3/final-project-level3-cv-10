import os

def convert(video_path,wav_path):
    os.system('ffmpeg -i {} -acodec pcm_s16le -ar 16000 {}.wav'.format(video_path, wav_path))