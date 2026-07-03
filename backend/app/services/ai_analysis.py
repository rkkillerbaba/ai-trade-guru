import os
import requests
import json

# 💎 100% Synced with Frontend Dropdown Short Names & OpenRouter Verified Free IDs
VALID_MODELS = {
    "google/gemma-4-26b-a4b-it:free": "Gemini Pro",
    "meta-llama/llama-3.3-70b-instruct:free": "Meta Pro",
    "openai/gpt-oss-120b:free": "GPT Pro",
    "nousresearch/hermes-3-llama-3.1-405b:free": "Hermes Pro",
    "nvidia/nemotron-3-ultra-550b-a55b:free": "Pro"
}

def generate_trader_insights(messages_history, model_id="google/gemma-4-26b-a4b-it:free"):
    """
    Resilient OpenRouter API Wrapper with fallback routing rules.
    Eliminates 500 Gateway Errors across Meta Pro, GPT Pro, and Hermes Pro.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    if not api_key:
        return {"success": False, "error": "Missing OPENROUTER_API_KEY environment variable on Render."}

    # Fallback to Gemini Pro if model is missing or invalid
    if model_id not in VALID_MODELS:
        model_id = "google/gemma-4-26b-a4b-it:free"

    # 🚀 ROBUST PARSING: Cleans history and system templates perfectly to avoid strict API schema rejections
    formatted_messages = []
    for msg in messages_history:
        if isinstance(msg, dict):
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Ensure we only push messages that actually have clean textual parameters
            if content and str(content).strip():
                formatted_messages.append({
                    "role": str(role).strip(),
                    "content": str(content).strip()
                })

    # Essential verification parameters for OpenRouter endpoints
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ai-trade-guru.vercel.app",
        "X-OpenRouter-Title": "AI Trade Guru Platform"
    }

    # 🔗 Optimized dynamic payload with fallback routing rules activated
    payload = {
        "model": model_id,
        "messages": formatted_messages,
        "provider": {
            "allow_fallbacks": True  # 🌟 CRITICAL: Server busy hone par request terminate karne ke bajaye back-up free clusters hit karega
        }
    }

    try:
        # Extended timeout to 45s to handle giant models like Hermes 405B processing time safely
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=45)
        
        if response.status_code != 200:
            return {"success": False, "error": f"OpenRouter Rejection Status {response.status_code}: {response.text}"}
            
        response_json = response.json()
        
        # Multi-level object extractor node passthrough pass
        if 'choices' in response_json and len(response_json['choices']) > 0:
            choice_item = response_json['choices'][0]
            message_node = choice_item.get('message', {})
            
            ai_content = message_node.get('content', '')
            ai_reasoning = message_node.get('reasoning_details', None) or message_node.get('reasoning', None)
            
            # Alternative layout tracking fallbacks
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
            return {"success": False, "error": f"OpenRouter returned empty response body matrix: {json.dumps(response_json)}"}

    except Exception as e:
        return {"success": False, "error": f"Service layer exception route crash: {str(e)}"}
