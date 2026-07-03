import os
import requests
import json

VALID_MODELS = {
    "google/gemma-4-26b-a4b-it:free": "Gemini Pro",
    "meta-llama/llama-3.3-70b-instruct:free": "Meta Pro",
    "openai/gpt-oss-120b:free": "GPT Pro",
    "nousresearch/hermes-3-llama-3.1-405b:free": "Hermes Pro",
    "nvidia/nemotron-3-ultra-550b-a55b:free": "Pro"
}

def generate_trader_insights(messages_history, model_id="google/gemma-4-26b-a4b-it:free"):
    api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    if not api_key:
        return {"success": False, "error": "Missing OPENROUTER_API_KEY on Render Environment Variables."}

    if model_id not in VALID_MODELS:
        model_id = "google/gemma-4-26b-a4b-it:free"

    # 🚀 STEP 1: Basic & foolproof structural validation for OpenRouter
    formatted_messages = []
    for msg in messages_history:
        if isinstance(msg, dict):
            role = str(msg.get("role", "user")).strip()
            content = str(msg.get("content", "")).strip()
            if content:  # Strict check: OpenRouter rejects blank contents completely
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
        "messages": formatted_messages
    }

    try:
        # Timeout rakha hai 30 seconds
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        
        # 🚀 STEP 2: CRITICAL DEBUG LAYER (Backend crash nahi hoga, exact error bataega)
        if response.status_code != 200:
            return {
                "success": False, 
                "error": f"OpenRouter Rejected Request (Status {response.status_code}). Server Response: {response.text}"
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
                "content": ai_content.strip() if ai_content else "Processed, but content node was empty.",
                "reasoning_details": ai_reasoning,
                "active_model": VALID_MODELS[model_id]
            }
        else:
            # OpenRouter agar success 200 de par choices na bheje (jaise rate limit/credit error par hota hai)
            return {
                "success": False, 
                "error": f"OpenRouter returned 200 but empty choices body. Full JSON: {json.dumps(response_json)}"
            }

    except Exception as e:
        return {
            "success": False, 
            "error": f"Python requests level exception caught: {str(e)}"
        }
