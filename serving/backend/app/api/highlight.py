from fastapi import FastAPI, APIRouter
from ml.final_timeline import make_final_timeline

router = APIRouter(tags=["highlight"])

@router.post("/timeline-highlight", description="최종 하이라이트에 해당하는 타임라인을 생성합니다.")
async def read_highlight(timelines: dict):
    print(timelines)
    face_timeline = timelines['face']
    laugh_timeline = timelines['laugh']

    final_timeline = make_final_timeline(laugh_timeline, face_timeline)

    return {"id" : id , "timeline" : final_timeline}