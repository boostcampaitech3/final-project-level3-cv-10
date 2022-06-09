from fastapi import FastAPI, File, UploadFile, APIRouter, HTTPException

import os
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
import shutil
from typing import List, Tuple, Optional
from pytube import YouTube

from ml.laughter_detection import LaughterDetection


router = APIRouter(tags=["timeline"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_DIR = os.path.join(BASE_DIR, 'files/')
ML_DIR = os.path.join(BASE_DIR, 'ml/')


class Video(BaseModel):
    id_laughter: UUID = Field(default_factory=uuid4)
    file_name: str
    created_at : datetime = Field(default_factory=datetime.now)


class VideoTimeline(BaseModel):
    id: UUID
    # file_name: str
    laugh: Optional[List[Tuple]]
    # created_at : datetime


@router.post("/laughter-detection", description="laughter timeline을 추출하는 전과정을 수행합니다.")
def laughter_detection(file: UploadFile = File(...)):
    """Upload된 영상을 통하여 laughter timeline을 추출하는 전 과정을 수행합니다.

    Args:
        file (UploadFile, optional): formData로 보내진 video data. Defaults to File(...).

    Returns:
        VideoTimeline (BaseModel): 
            id (UUID): 영상을 구분할 수 있는 구분자.
            laugh (List[Tuple], optional): 전체 영상에 대하여 웃음에 해당하는 timeline.
    """
    # download the uploaded video
    new_video = Video(file_name=file.filename)
    os.makedirs(os.path.join(FILE_DIR, str(new_video.id_laughter)))
    video_path = os.path.join(FILE_DIR, str(new_video.id_laughter), ('original' + os.path.splitext(file.filename)[1]))
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # extract laughter timeline
    new_video_timeline = VideoTimeline(id=new_video.id_laughter)

    # execute laughter detection    
    wav_path = os.path.join(FILE_DIR, str(new_video.id_laughter), 'for_laughter_detection')

    laughter_timeline = LaughterDetection(video_path, wav_path, ML_DIR)
    new_video_timeline.laugh = laughter_timeline

    # remove folder (laughter detection 서버에서는 일회성이므로)
    shutil.rmtree(os.path.join(FILE_DIR, str(new_video_timeline.id)))
    return new_video_timeline


@router.post("/laughter-detection-youtube", description="유튜브 URL을 이용하여 laughter timeline을 추출하는 전과정을 수행합니다.")
def laughter_detection_from_youtube(info: dict):
    """유튜브 URL을 이용하여 laughter timeline을 추출하는 전 과정을 수행합니다.

    Args:
        info (dict):
            url (str): 유튜브 영상 url

    Returns:
        VideoTimeline: 
            id (UUID): 영상을 구분할 수 있는 구분자.
            laugh (List[Tuple], optional): 전체 영상에 대하여 웃음에 해당하는 timeline.
    """
    yt_video = YouTube(info['url'])
    new_video = Video(file_name=yt_video.title + '.mp4')

    stream = yt_video.streams.filter(progressive=True, subtype="mp4", resolution="720p").first()
    if stream:
        os.makedirs(os.path.join(FILE_DIR, str(new_video.id_laughter)))
        id_path = os.path.join(FILE_DIR, str(new_video.id_laughter))
        video_path = os.path.join(id_path, ('original.mp4'))

        stream.download(output_path=id_path, filename='original.mp4')

        # extract laughter timeline
        new_video_timeline = VideoTimeline(id=new_video.id_laughter)

        # execute laughter detection    
        wav_path = os.path.join(id_path, 'for_laughter_detection')

        laughter_timeline = LaughterDetection(video_path, wav_path, ML_DIR)
        new_video_timeline.laugh = laughter_timeline

        # remove folder (laughter detection 서버에서는 일회성이므로)
        shutil.rmtree(os.path.join(FILE_DIR, str(new_video_timeline.id)))
        return new_video_timeline

    else:
        return {"message": "720p를 지원하는 영상이 아닙니다."}
