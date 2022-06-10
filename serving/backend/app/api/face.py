from fastapi import FastAPI, File, UploadFile, APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Dict, List
from PIL import Image
import base64
import io
import numpy as np

from ml.face_functions import FaceRecognition

from google.cloud import storage
storage_client = storage.Client()
bucket_name = 'snowman-bucket'
bucket = storage_client.bucket(bucket_name)

router = APIRouter(tags=["timeline"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_DIR = os.path.join(BASE_DIR, 'files/')


class People(BaseModel):
    id: UUID 
    people_img: Dict[str, bytes]
    file_name: str
    message: Optional[str]


class ItemValue(BaseModel):
    id: str
    person: str


# get으로 바꾸어 사진 보여주기
@router.get("/show-people", description="face clustering으로 추출한 인물의 사진을 보여줍니다.")
def show_people(id: UUID):
    """face clustering으로 추출한 인물의 사진을 보여주는 api

    Args:
        id (UUID): clustering 결과에 접근하기 위한, 식별자

    Returns:
        Response(dict):
            id (str) : 영상을 구분할 수 있는 구분자.
            people_img (dict) : 인물의 대표이미지를 gcs에 올린 후, gcs에 접근할 수 있는 url을 제공
    """

    people_img = {}
    result_path = os.path.join(FILE_DIR, str(id), 'result', 'result.npy')
    result_data = np.load(result_path, allow_pickle=True).item()
    
    for person in result_data.keys():
        img_path = result_data[person]['repr_img_path']
        
        blob_dir = os.path.join(str(id), 'people', person)
        blob = bucket.blob(blob_dir)
        blob.upload_from_filename(img_path)
        people_img[person] = blob_dir
    
    return {"id": id, "people_img": people_img}


@router.post("/timeline-face", description="face recognition을 통해 인물의 timeline을 추출한다.")
def get_timeline_face(info: dict):
    """face recognition을 통하여 인물의 timeline을 추출한다.

    Args:
        info (dict): request body
            id (str) : 영상을 구분할 수 있는 영상 고유의 UUID
            face (list) : face recognition을 진행할 사람들에 해당하는 list ex) ["person_00", "person_02"]


    Returns:
        Response (dict) : 영상에 대한 UUID와 인물에 대한 timeline을 제공
            id (str) : 영상을 구분할 수 있는 영상 고유의 UUID
            face_timelines (dict) : 특정 인물들에 대한 timeline을 list형태로 제공 ex) face_timelines : {"person_00" : [[]], "person_03" : [[]]}
    """
    
    video_path = os.path.join(FILE_DIR, info['id'])
    video = os.path.join(video_path, 'original.mp4')

    # recognition
    target_people = info['face']
    result_path = os.path.join(FILE_DIR, info['id'], 'result', 'result.npy')

    timelines = FaceRecognition(video, target_people, result_path)
    
    save_path = os.path.join(FILE_DIR, info['id'], 'face_timelines.npy')
    np.save(save_path, timelines)

    return {"id" : info['id']}
