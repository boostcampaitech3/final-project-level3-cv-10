import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

import os
# gcs server
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= os.path.join(os.path.dirname(os.path.abspath(__file__)), 'feisty-flow-350613-adcfd8ba2d54.json')


from api import video, face, highlight
import os

app = FastAPI()

app.include_router(video.router)
app.include_router(face.router)
app.include_router(highlight.router)

origins = [
    "http://34.64.107.58:30002",
    "34.64.107.58:30002",
    "http://34.64.208.21:30002",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def read_root() -> dict:
    return {"message": "Welcome to SNOWMAN :')"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=30001, reload=True)
