import os
import re
import tempfile
import torch
import shutil
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from asr.whisper_asr import transcribe_audio
from llm.qwen import extract_intent
from actions.router import handle_action
from tts.tts_engine import speak

torch.set_num_threads(4)

app = FastAPI(title="Aura Voice Assistant API")

def cleanup_file(path: str):
    """Safely delete a file in background task"""
    try:
        if path and os.path.exists(path):
            os.unlink(path)
            print(f"Cleaned up: {path}")
    except Exception as e:
        print(f"️ Cleanup warning for {path}: {e}")

def get_intent_from_rules(text: str) -> dict | None:
    """
    Ultra-fast rule-based intent matching for common commands.
    Bypasses slow LLM for 80% of requests!
    """
    t = text.lower().strip()
    if not t:
        return None
    
    if re.search(r"\b(time|clock|what time|date|today's date|what day|day is it)\b", t):
        return {"intent": "time"}
    
    app_map = {
        "youtube": ["youtube", "you tube", "you.tube"],
        "netflix": ["netflix"],
        "spotify": ["spotify"],
        "google": ["google"],
        "gmail": ["gmail", "google mail"],
        "facebook": ["facebook", "fb"],
        "instagram": ["instagram", "insta"],
        "twitter": ["twitter", "x.com", "tweet"],
        "tiktok": ["tiktok", "tik tok", "tik-tok"],
        "amazon": ["amazon"]
    }

    weather_match = re.search(r"\b(weather|forecast|temperature|how (hot|cold)|degrees)\b", t)
    if weather_match:
        location = None
        loc_match = re.search(r"(?:in|at|for)\s+([a-z\s]+)", t)
        if loc_match:
            location = loc_match.group(1).strip()
            location = re.sub(r'\s+(today|tomorrow|now)$', '', location).strip()
        return {"intent": "weather", "location": location}

    open_match = re.search(r"open\s+([a-z0-9\s]+)", t)
    if open_match:
        app_input = open_match.group(1).strip()
        for target, aliases in app_map.items():
            if app_input in aliases or app_input == target:
                return {"intent": "open_app", "target": target}
            
        return {"intent": "open_app", "target": app_input}
    
    play_match = re.search(r"(?:play|search|find|look for)\s+(.+)", t)
    if play_match:
        query = play_match.group(1).strip()

        query = re.sub(r"\b(me|for|a|the|some)\b", "", query).strip()
        return {"intent": "search", "query": query}
    
    responses = {
        r"\b(hi|hello|hey|hey there)\b": "Hi! I'm Aura How can I help?",
        r"\bhow are you\b": "Feeling great! Ready to help ",
        r"\bthank": "You're welcome!",
        r"\bjoke\b": "Why don't scientists trust atoms? They make up everything!",
        r"\bweather\b": "I don't have live weather access yet, but I'd love to help soon!",
        r"\bhelp\b": "I can open apps, play music, tell time, or just chat!",
        r"\byour name\b": "I'm Aura, your AI assistant! ",
        r"\bwho are you\b": "I'm Aura, your AI assistant! "
    }
    
    for pattern, resp in responses.items():
        if re.search(pattern, t):
            return {"intent": "respond", "text": resp}
    
    return None  


@app.post("/process")
async def process_voice(
    audio: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    tmp_input = None
    tmp_output = None
    
    try:
        # Save uploaded audio to TEMP file
        suffix = ".webm" if audio.content_type == "audio/webm" else ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(audio.file, tmp)
            tmp_input = tmp.name

        #ASR: Speech → Text
        user_text = transcribe_audio(tmp_input).strip()
        if not user_text:
            raise HTTPException(status_code=400, detail="No speech detected")
        print(f"ASR: '{user_text}'")

        #RULE-BASED INTENT MATCHING 
        intent = get_intent_from_rules(user_text)
        
        if intent is None:
            #LLM FALLBACK 
            current_time = datetime.now().strftime("%I:%M %p")
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            intent = extract_intent(user_text, current_time=current_time, current_date=current_date)
            print("LLM Fallback:", intent)
        else:
            print("RULES MATCH:", intent)

        #Action Router
        response_text = handle_action(intent)
        print("RESPONSE:", response_text)

        #TTS → Save to UNIQUE temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_out:
            tmp_output = tmp_out.name
        
        # Generate TTS to temp file
        speak(response_text, output_path=tmp_output)

        # Schedule cleanup AFTER response is fully sent
        if tmp_input:
            background_tasks.add_task(cleanup_file, tmp_input)
        if tmp_output:
            background_tasks.add_task(cleanup_file, tmp_output)

        return FileResponse(
            tmp_output,
            media_type="audio/wav",
            headers={"X-Transcript": user_text},
            filename="response.wav"
        )

    except HTTPException:
        # Immediate cleanup on validation errors
        if tmp_input and os.path.exists(tmp_input):
            os.unlink(tmp_input)
        raise
        
    except Exception as e:
        print(f"Processing error: {str(e)}")
        # Fallback error audio
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_err:
                tmp_output = tmp_err.name
            speak("Sorry, I had trouble understanding that.", output_path=tmp_output)
            
            if tmp_input:
                background_tasks.add_task(cleanup_file, tmp_input)
            if tmp_output:
                background_tasks.add_task(cleanup_file, tmp_output)
                
            return FileResponse(
                tmp_output,
                media_type="audio/wav",
                headers={"X-Transcript": "Error processing request"}
            )
        except Exception as tts_err:
            print(f"TTS fallback failed: {tts_err}")
            if tmp_input and os.path.exists(tmp_input):
                os.unlink(tmp_input)
            raise HTTPException(status_code=500, detail="Audio generation failed")

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
else:
    @app.get("/")
    async def root():
        return {
            "message": "Aura API running",
            "frontend_missing": str(FRONTEND_DIR)
        }