from fastapi import FastAPI, File, UploadFile, APIRouter, HTTPException

import os
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
import shutil

from ml.extract_face import execute_face_extractor


router = APIRouter(tags=["video"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_DIR = os.path.join(BASE_DIR, 'files/')


class Video(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    file_name: str
    created_at : datetime = Field(default_factory=datetime.now)
    

@router.post("/upload-video", description="비디오를 업로드합니다.")
async def create_video_file(file: UploadFile = File(...)):
    # download the uploaded video
    new_video = Video(file_name=file.filename)
    os.makedirs(os.path.join(FILE_DIR, str(new_video.id)))
    server_path = os.path.join(FILE_DIR, str(new_video.id), ('original' + os.path.splitext(file.filename)[1]))
    with open(server_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # execute face clustering
    execute_face_extractor(FILE_DIR, str(new_video.id))

    return new_video


# TODO: /upload-video (비디오를 서버에 업로드하는 과정)
# TODO: /select-highlight (생성된 쇼츠를 다운로드 하는 과정)
