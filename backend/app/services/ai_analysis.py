import requests
import json
from typing import List, Dict, Any
from app.config import settings

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def generate_trader_insights(chat_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    OpenRouter Gemma-4 Free model ka use karke reasoning context ko 
    preserve karte hue multi-turn analysis return karta hai.
    """
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": "google/gemma-4-31b-it:free",
        "messages": chat_history,
        "reasoning": {"enabled": True}
    }
    
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(payload), timeout=30)
        response.raise_for_status()
        response_json = response.json()
        
        assistant_message = response_json['choices'][0]['message']
        
        return {
            "success": True,
            "content": assistant_message.get('content'),
            "reasoning_details": assistant_message.get('reasoning_details')
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
