# Aura Voice Assistant

An end-to-end **AI-powered voice assistant** for handling everyday commands like checking the time, opening apps, searching content, and more. Aura provides a seamless local pipeline that takes **voice input from a web interface** and outputs **spoken responses**, with no external services required beyond installed libraries.

---

## Overview

**Aura** is a friendly AI voice assistant designed to make human–computer interaction natural and efficient. It combines:

- Speech recognition
- Intent understanding via a lightweight language model
- Action routing
- Text-to-speech synthesis

All components are integrated into an automated workflow exposed through a **FastAPI backend** and a **vanilla HTML/CSS/JS frontend**. The system is optimized for **fast response times**, **CPU-friendly execution**, and **clean modular design**, making it ideal for personal assistants, experiments, or embedded systems.

---

## Key Features

- Voice command recognition using **faster-whisper**
- Intent extraction with a compact **Qwen (1.5B)** language model
- Built-in actions (time queries, app opening, content search, etc.)
- Natural voice responses using **Coqui TTS**
- Simple web interface for recording and playback
- Fully local execution (no cloud APIs)
- Clean separation of processing stages for maintainability

---

## Tech Stack

- **Python**
- **FastAPI**
- **faster-whisper** (speech-to-text)
- **Hugging Face Transformers** (Qwen LLM)
- **Coqui TTS** (text-to-speech)
- **Webbrowser** (system-level action handling)
- **HTML / CSS / JavaScript** (frontend)

---

## Pipeline Overview

1. Voice input captured via the web frontend
2. Audio file uploaded to the FastAPI backend
3. Speech-to-text transcription using **faster-whisper**
4. Intent extraction and context-aware processing via **Qwen LLM**
5. Action routing to determine the correct system response
6. Text-to-speech synthesis using **Coqui TTS**
7. Audio response returned to the frontend for playback

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/aura-voice-assistant.git
cd aura-voice-assistant
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

> **Linux / macOS**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

### Run the FastAPI backend

```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Open the application

- Navigate to: **[http://localhost:8000](http://localhost:8000)**
- Allow microphone access
- Speak a command such as:
  - _"What time is it?"_
  - _"Open YouTube"_

- Listen to the spoken response

---

## Project Structure

```text
├── backend/
│   ├── actions/
│   │   └── router.py        # Maps intents to actions
│   ├── asr/
│   │   └── whisper_asr.py   # Speech-to-text (faster-whisper)
│   ├── llm/
│   │   └── qwen.py          # Intent extraction using Qwen LLM
│   ├── tts/
│   │   └── tts_engine.py    # Text-to-speech with Coqui TTS
│   └── app.py               # FastAPI entry point
│
├── frontend/
│   ├── index.html           # Web UI
│   ├── script.js            # Client-side logic
│   └── style.css            # Styling
│
├── requirements.txt
└── README.md
```

---

## Performance Considerations

- Models are **loaded at startup** to minimize first-request latency
- CPU-optimized configurations:
  - Whisper: **int8**
  - Qwen: **float16** (when supported)

- Temporary audio files are managed and cleaned automatically
- Modular processing stages allow easy scaling and optimization


---

## License

This project is open-source and available under the **MIT License**.

---

## Future Improvements

- Expanded intent support for additional actions
- Multilingual speech recognition and responses
- Desktop notification integration
- Mobile-friendly frontend enhancements
- Containerization (Docker) for easier deployment

---

Feel free to fork, experiment, and extend Aura
