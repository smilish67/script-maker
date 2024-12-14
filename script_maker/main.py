import os
from fastapi import FastAPI
from web_api import user_router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(user_router.router)


app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="scriptMaker/webtoon/merged_images"), name="iamges")
app.mount("/voices", StaticFiles(directory="scriptMaker/voice/actor"), name="voices")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://112.133.88.222:5866"],  # 허용할 클라이언트 URL
    allow_credentials=True,
    allow_methods=["*"],  # 허용할 HTTP 메서드
    allow_headers=["*"],  # 허용할 HTTP 헤더
)