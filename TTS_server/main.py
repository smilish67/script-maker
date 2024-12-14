import os
from fastapi import FastAPI, HTTPException
from fastapi.requests import Request
from fastapi.responses import FileResponse
from model_controller import ModelController
import torch, torchaudio


mctrl = ModelController()
model = mctrl.get_model()

app = FastAPI()


@app.post("/tts", response_class=FileResponse)
async def tts(data: dict):
    try:
        actor = data['actor']
        text = data['dialog']

        # TTS 모델에서 필요한 latent 벡터를 가져오기
        gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
            audio_path=f"./actor/{actor}/h/sample_happy.wav",
            gpt_cond_len=30,
            max_ref_length=60,
            sound_norm_refs=True
        )

        print("Generating TTS output...")
        # TTS 모델로 음성 합성하기
        outputs = model.inference(
            text=text,
            language="ko",
            gpt_cond_latent=gpt_cond_latent,
            speaker_embedding=speaker_embedding,
            temperature=0.8,
            length_penalty=0.8,
            repetition_penalty=2.0,
            top_k=60,
            top_p=0.9,
        )
        
        # WAV 파일 저장
        wav_path = "xtts.wav"
        torchaudio.save(wav_path, torch.tensor(outputs["wav"]).unsqueeze(0), 24000)
        
        # WAV 파일 반환
        return FileResponse(wav_path, media_type="audio/wav", filename="xtts.wav")

    except Exception as e:
        print(f"Error generating TTS: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating TTS: {str(e)}")