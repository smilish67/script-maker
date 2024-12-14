import os, json
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import FileResponse
import requests, io

from scriptMaker.utils.webtoon_loader import WebtoonLoader
from scriptMaker.script_maker import WebtoonScriptGenerator


templates = Jinja2Templates(directory="templates") 
router = APIRouter()

@router.get("/tool", response_class=HTMLResponse) 
async def read_item(request: Request): 
        #image list
        w_loader = WebtoonLoader(request.url)
        image_list = w_loader.load_webtoon("webtoon")
        #script list
        # script_maker = WebtoonScriptGenerator(image_list)
        # script_list = script_maker.process_webtoon()

        #voice list
        path = r"./scriptMaker/voice/voice_info.json"
        with open(path, "r") as f:
            voice_info = json.load(f)
        
        with open(r"./temp/webtoon_script.json", "r", encoding='utf-8') as f:
            script_list = json.load(f)
            
        #temporal save list
        # with open(r"./temp/webtoon_script.json", "w", encoding='utf-8') as f:
        #     json.dump(script_list, f, ensure_ascii=False, indent=4)
        

        return templates.TemplateResponse("tool.html", {"script_list": script_list, "image_list": image_list, "voice_info": voice_info, "request": request})

@router.post("/audioMaker", response_class=JSONResponse)
async def audio_maker(data: Request):
    try:
        # Request 객체에서 JSON 본문을 추출
        json_data = await data.json()
        
        # TTS 서버로 요청 전송
        response = requests.post("http://127.0.0.1:3004/tts", json=json_data)

        webtoonName = json_data['webtoon']
        batch = json_data['fileName']

        #mkdir
        os.makedirs(os.path.join("static/wavs", webtoonName), exist_ok=True)
        file_path = os.path.join("static/wavs", webtoonName, batch + ".wav")

        # TTS 서버에서 WAV 파일을 반환하는지 확인
        if response.status_code == 200:
            # WAV 파일 응답 처리 후 반환
            with open(file_path, "wb") as f:
                f.write(response.content)
            rel_path = f"wavs/{webtoonName}/{batch}.wav"
            # 저장된 파일의 URL 반환
            return {"file_url": rel_path}
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to generate WAV from TTS server")
    
    except requests.exceptions.RequestException as e:
        # TTS 서버와의 연결 문제 처리
        print(f"Error contacting TTS server: {str(e)}")
        raise HTTPException(status_code=500, detail="Error contacting TTS server: " + str(e))
