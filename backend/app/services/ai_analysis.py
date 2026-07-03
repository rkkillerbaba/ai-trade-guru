import os
import requests
import json

# 💎 Pure Active, Fast, and Synced Free Models List (Venice Pro Removed)
VALID_MODELS = {
    "google/gemma-4-26b-a4b-it:free": "Gemini Pro",
    "openai/gpt-oss-120b:free": "GPT Pro",
    "openai/gpt-oss-20b:free": "GPT Lite",
    "nvidia/nemotron-3-ultra-550b-a55b:free": "Nemotron Ultra"
}

def generate_trader_insights(messages_history, model_id="google/gemma-4-26b-a4b-it:free"):
    """
    Ultra-resilient OpenRouter API Wrapper.
    Prevents empty parameters and filters structural data smoothly.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    if not api_key:
        return {"success": False, "error": "Missing OPENROUTER_API_KEY environment variable on Render."}

    if model_id not in VALID_MODELS:
        model_id = "google/gemma-4-26b-a4b-it:free"

    # Cleaning payload strings to pass strict content specifications
    formatted_messages = []
    for msg in messages_history:
        if isinstance(msg, dict):
            role = str(msg.get("role", "user")).strip()
            content = str(msg.get("content", "")).strip()
            if content:
                formatted_messages.append({
                    "role": role,
                    "content": content
                })

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ai-trade-guru.vercel.app",
        "X-OpenRouter-Title": "AI Trade Guru"
    }

    payload = {
        "model": model_id,
        "messages": formatted_messages,
        "provider": {
            "allow_fallbacks": True
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        
        if response.status_code != 200:
            return {
                "success": False, 
                "error": f"OpenRouter Gateway Status {response.status_code}: {response.text}"
            }
            
        response_json = response.json()
        
        if 'choices' in response_json and len(response_json['choices']) > 0:
            choice_item = response_json['choices'][0]
            message_node = choice_item.get('message', {})
            
            ai_content = message_node.get('content', '')
            ai_reasoning = message_node.get('reasoning_details', None) or message_node.get('reasoning', None)
            
            if not ai_content and 'text' in message_node:
                ai_content = message_node.get('text', '')
            if not ai_content and 'text' in choice_item:
                ai_content = choice_item.get('text', '')

            return {
                "success": True,
                "content": ai_content.strip() if ai_content else "Insight processed successfully.",
                "reasoning_details": ai_reasoning,
                "active_model": VALID_MODELS[model_id]
            }
        else:
            return {"success": False, "error": f"Empty response structure: {json.dumps(response_json)}"}

    except Exception as e:
        return {"success": False, "error": f"Pipeline connection error: {str(e)}"}
