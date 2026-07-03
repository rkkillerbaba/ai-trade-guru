import os
import requests
import json

# 💎 Frontend dropdown se match karte huye 5 best curated models ki mapping
VALID_MODELS = {
    "google/gemma-4-26b-a4b-it:free": "Gemma-4 Reasoning 26B",
    "qwen/qwen3-next-80b-instruct:free": "Qwen-3 Next 80B Instruct",
    "openai/gpt-oss-120b:free": "OpenAI GPT-OSS 120B",
    "qwen/qwen3-coder-480b-a35b:free": "Qwen-3 Coder 480B",
    "nvidia/nemotron-3-ultra:free": "NVIDIA Nemotron 3 Ultra"
}

def generate_trader_insights(messages_history, model_id="google/gemma-4-26b-a4b-it:free"):
    """
    OpenRouter API Wrapper supporting dynamic model synchronization.
    Accepts model_id directly passed from frontend payload.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    if not api_key:
        return {
            "success": False,
            "error": "Missing OPENROUTER_API_KEY environment variable on Render."
        }

    # Safety Layer: Agar frontend se galat/khali ID aaye toh Gemma fallback activate hoga
    if model_id not in VALID_MODELS:
        model_id = "google/gemma-4-26b-a4b-it:free"

    # Restructure conversation history logs securely
    formatted_messages = []
    for msg in messages_history:
        item = {
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        }
        # OpenRouter rules: pass back reasoning_details unmodified for history tracking
        if msg.get("reasoning_details"):
            item["reasoning_details"] = msg.get("reasoning_details")
        formatted_messages.append(item)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 🚀 Dynamic Model Selection Layer
    payload = {
        "model": model_id,             # Frontend dropdown ka model yahan live inject hoga
        "messages": formatted_messages,
        "reasoning": {"enabled": True}  # Reasoning models ke thinking tokens active rakhega
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"OpenRouter Gateway Error {response.status_code}: {response.text}"
            }
            
        response_json = response.json()
        
        if 'choices' in response_json and len(response_json['choices']) > 0:
            message_obj = response_json['choices'][0]['message']
            
            ai_content = message_obj.get('content', '')
            ai_reasoning = message_obj.get('reasoning_details', None)
            
            return {
                "success": True,
                "content": ai_content,
                "reasoning_details": ai_reasoning,
                "active_model": VALID_MODELS[model_id] # Client verification check track karega
            }
        else:
            return {
                "success": False,
                "error": f"Unexpected response format structure: {json.dumps(response_json)}"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Internal pipeline generation exception: {str(e)}"
        }
