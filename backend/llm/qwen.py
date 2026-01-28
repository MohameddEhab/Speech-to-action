import json
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"

print("Loading Qwen model...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_ID,
    trust_remote_code=True
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    device_map="auto",
    torch_dtype=torch.float16,
    trust_remote_code=True
)

model.eval()

print(f"Qwen model loaded on {model.device}")


def extract_intent(text: str, current_time: str = None, current_date: str = None) -> dict:
    
    context = ""
    if current_time or current_date:
        context_parts = []
        if current_date:
            context_parts.append(f"Today is {current_date}")
        if current_time:
            context_parts.append(f"Current time is {current_time}")
        context = " | ".join(context_parts) + " | "
    
    prompt = f"""
You are "Aura", a friendly AI voice assistant.

CONTEXT: {context}Use this for time/date. NEVER make up times.

RULES:
- Output ONLY valid JSON. No other text.
- Use ONE intent:
  • "time": For time/date questions.
  • "open_app": To open websites/apps. Include "target" (lowercase).
  • "search": To play/search content. Include "query".
  • "respond": For everything else. Include warm "text" (max 15 words).

CRITICAL:
- For time/date: ALWAYS use "time" intent.
- For weather: Use "respond" with "I don't have live weather access yet."
- Keep responses short for voice.

EXAMPLES:
User: what time is it
{{"intent":"time"}}

User: open netflix
{{"intent":"open_app","target":"netflix"}}

User: play bad guy
{{"intent":"search","query":"bad guy"}}

User: how are you
{{"intent":"respond","text":"Feeling great! Ready to help "}}

User: weather
{{"intent":"respond","text":"I don't have live weather access yet."}}

User: {text}

JSON:
"""

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=50,  
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )

    input_length = inputs.input_ids.shape[1]
    generated_tokens = output[0][input_length:]
    decoded = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

    match = re.search(r"\{[^{}]*\}", decoded)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    print(f"️ Failed to parse intent. Raw model output: '{decoded}'")
    return {
        "intent": "respond",
        "text": "I'm here to help! What would you like to do?"
    }