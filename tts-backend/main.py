from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from io import BytesIO
import edge_tts

app = FastAPI(title="Census 2027 Hindi Voice API", version="1.0.0")

# GitHub Pages origin will be allowed. For public deployment, tighten this to your Pages URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1500)
    voice: str = "hi-IN-SwaraNeural"

@app.get("/")
def root():
    return {"service": "Census 2027 Hindi TTS", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/tts")
async def create_tts(payload: TTSRequest):
    try:
        communicate = edge_tts.Communicate(
            text=payload.text,
            voice=payload.voice,
            rate="-5%",
            pitch="+0Hz",
            volume="+0%",
        )
        output = BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                output.write(chunk["data"])
        data = output.getvalue()
        if not data:
            raise RuntimeError("TTS service returned empty audio")
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="audio/mpeg",
            headers={"Content-Disposition": 'inline; filename="census-2027-voice.mp3"'},
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Hindi voice generation failed: {exc}")
