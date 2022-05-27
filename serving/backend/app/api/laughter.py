from fastapi import FastAPI, File, UploadFile, APIRouter, HTTPException

import os
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime

router = APIRouter(tags=["timeline"])

# TODO: /timeline-laughter (laughter detection을 통해 웃음 구간의 timeline 추출하기)
