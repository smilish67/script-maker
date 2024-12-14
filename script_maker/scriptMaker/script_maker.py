# batch_characterDB_speech.py
# 결과물에 Elevenlabs API 적용
import base64
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
import json
from scriptMaker.get_prompt import get_prompt
from typing import List
from openai import OpenAI
from elevenlabs import ElevenLabs, VoiceSettings
import uuid

load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ElevenLabs 클라이언트 초기화
elevenlabs_client = ElevenLabs(
    api_key=os.getenv("ELEVEN_API_KEY"),
)

class Appearance(BaseModel):
    hair_style: str
    eye_color: str
    etc: str

class Character(BaseModel):
    id: str
    gender: str
    appearance: Appearance
    voice_id: str
    default_emotion: str
    age: int

class Dialogue(BaseModel):
    speaker_id: str
    text: str
    emotion: str
    tone: str

class WebtoonScript(BaseModel):
    scene_id: str
    characters: List[Character]
    scene_characters: List[str]
    dialogue: List[Dialogue]
    max_characters_per_scene: int

class WebtoonScriptGenerator:
    def __init__(self, image_list):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.image_list = image_list
        self.image_folder = r"./scriptMaker/webtoon/merged_images"
        self.output_file_path = r"./scriptMaker/webtoon/webtoon_script.json"
        # 캐릭터 데이터베이스 단순화
        self.character_database = {}
        
        # 사용 가능한 voice ID 풀
        self.available_voice_ids = [
            "v1jVu1Ky28piIPEJqRrm"
        ]
        
        # voice ID 매핑 저장
        self.voice_id_mapping = {}
        
        # voice ID 사용 현황 추적
        self.used_voice_ids = set()

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def update_character_database(self, new_characters: List[Character]):
        """
        새로운 캐릭터 정보를 데이터베이스에 추가/업데이트
        """
        print(f"\n=== 캐릭터 데이터베이스 업데이트 중 ===")
        for char in new_characters:
            char_dict = char.dict()  # Pydantic 모델을 딕셔너리로 변환
            char_id = char_dict['id']
            
            if char_id not in self.character_database:
                print(f"새 캐릭터 추가: {char_dict['id']}")
                self.character_database[char_id] = char_dict
            else:
                print(f"기존 캐릭터 업데이트: {char_dict['id']}")
                # 기존 캐릭터 정보 업데이트
                existing_char = self.character_database[char_id]
                for key, value in char_dict.items():
                    if value is not None and value != '':
                        existing_char[key] = value

    def send_images_to_api(self, images, previous_context=""):
        # 먼저 existing_characters_str과 modified_prompt 정의
        existing_characters_str = json.dumps(
            list(self.character_database.values()), 
            indent=2, 
            ensure_ascii=False
        )
        
        modified_prompt = get_prompt.replace(
            "{{PREVIOUS_CONTEXT}}", 
            f"Existing Characters:\n{existing_characters_str}\n\nPrevious Context:\n{previous_context}"
        )

        print("\n=== API 요청 시작 ===")
        try:
            response = openai_client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": modified_prompt},
                        ] + [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{self.encode_image(os.path.join(self.image_folder, img))}"
                                }
                            } for img in images
                        ]
                    }
                ],
                max_tokens=5000,
                response_format=WebtoonScript
            )
            
            print("\n=== API 응답 수신 ===")
            print(f"응답 타입: {type(response)}")
            print(f"응답 내용: {response}")
            
            try:
                # choices[0].message.parsed에서 WebtoonScript 객체 가져오기
                if response.choices and response.choices[0].message.parsed:
                    script = response.choices[0].message.parsed
                    print(f"WebtoonScript 파싱 성공")
                    print(f"발견된 캐릭터 수: {len(script.characters)}")
                    
                    if script.characters:
                        self.update_character_database(script.characters)
                    
                    return {
                        "script": script.dict(),  # Pydantic 모델을 딕셔너리로 변환
                        "characters": list(self.character_database.values())
                    }
                else:
                    print("파싱된 WebtoonScript를 찾을 수 없습니다")
                    return {"error": "WebtoonScript 없음"}
            except Exception as e:
                print(f"응답 처리 중 오류: {e}")
                print(f"응답 상세 내용: {response}")
                return {"error": str(e)}
        except Exception as e:
            print(f"API 호출 중 오류: {e}")
            return {"error": str(e)}

    def process_webtoon(self, batch_size=5):
        print("\n=== 웹툰 처리 시작 ===")
        image_files = sorted(
            [f for f in os.listdir(self.image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))], 
            key=lambda x: int(x.split('_')[1].split('.')[0])
        )
        print(f"처리할 이미지 수: {len(image_files)}")

        os.makedirs(os.path.dirname(self.output_file_path), exist_ok=True)
        previous_context_all = {}
        result = []
        for i in range(0, len(image_files), batch_size):
            print(f"\n=== Batch {i // batch_size + 1} 처리 중 ===")
            batch_images = image_files[i:i + batch_size]
            print(f"현재 배치 이미지: {batch_images}")
        
            previous_context = previous_context_all.get(i-1, "")
            tmp_result = self.send_images_to_api(batch_images, previous_context)
            result.append(tmp_result)
            
            previous_context_all[i] = {
                # give last 2 conversation
                "previous_context": tmp_result["script"]["dialogue"][-2:],
            }

        return result
