import webbrowser
import urllib.parse
from datetime import datetime
import re

def handle_action(intent: dict) -> str:
    if not isinstance(intent, dict):
        return "I had trouble understanding that request."

    intent_type = intent.get("intent")

    #TIME INTENT
    if intent_type == "time":
        now = datetime.now()
        current_time = now.strftime("%I:%M %p")
        current_date = now.strftime("%A, %B %d")
        return f"It's {current_time} on {current_date}."

    # WEATHER INTENT 
    if intent_type == "weather":
        location = intent.get("location", "").strip().lower()
        if location:
            location = re.sub(r'^(in|at|for|the)\s+', '', location).strip()
            query = f"weather in {location}"
            webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(query)}", new=2)
            return f"Showing weather for {location.title()}"
        else:
            webbrowser.open("https://www.google.com/search?q=weather", new=2)
            return "Showing current weather forecast"

    #  OPEN APP INTENT
    if intent_type == "open_app":
        target = intent.get("target", "").strip().lower()
        if target:
            target = re.sub(r'\s+(website|app|application|site|page|dot com)$', '', target).strip()
        if target:
            domain_map = {
                "youtube": "youtube.com",
                "netflix": "netflix.com",
                "spotify": "open.spotify.com",
                "google": "google.com",
                "gmail": "mail.google.com",
                "facebook": "facebook.com",
                "instagram": "instagram.com",
                "twitter": "twitter.com",
                "tiktok": "tiktok.com",
                "amazon": "amazon.com"
            }
            domain = domain_map.get(target, f"{target}.com")
            webbrowser.open(f"https://{domain}")
            return f"Opening {target.title()}" if target in domain_map else f"Opening {target}"
        return "Which app would you like me to open?"

    # ️ SEARCH/PLAY INTENT
    if intent_type == "search":
        query = intent.get("query", "").strip()
        if query:
            safe_query = urllib.parse.quote(query)
            webbrowser.open(f"https://www.youtube.com/results?search_query={safe_query}")
            return f"Playing {query} on YouTube"
        return "What would you like me to search for?"

    #RESPONSE
    if intent_type == "respond":
        return intent.get("text", "Okay.")

    # UNKNOWN INTENT
    return "I'm still learning! I can't handle that request yet."