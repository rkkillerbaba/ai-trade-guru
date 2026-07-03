import os
import requests
import json

# 💎 Updated strictly allowed premium models list (Removed Qwen, Added Meta & Hermes)
VALID_MODELS = {
    "google/gemma-4-26b-a4b-it:free": "Gemini Pro",
    "meta-llama/llama-3.3-70b-instruct:free": "Meta Pro",
    "openai/gpt-oss-120b:free": "GPT Pro",
    "nousresearch/hermes-3-llama-3.1-405b:free": "Hermes-3 405B",
    "nvidia/nemotron-3-ultra-550b-a55b:free": "Nvidia"
}

def generate_trader_insights(messages_history, model_id="google/gemma-4-26b-a4b-it:free"):
    """
    OpenRouter API Wrapper supporting dynamic model synchronization.
    Fully updated for Meta Llama and Hermes models payload extraction.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    if not api_key:
        return {
            "success": False,
            "error": "Missing OPENROUTER_API_KEY environment variable on Render."
        }

    # Safety Layer: Fallback to Gemini Pro if model is missing or invalid
    if model_id not in VALID_MODELS:
        model_id = "google/gemma-4-26b-a4b-it:free"

    # Restructure conversation history logs securely
    formatted_messages = []
    for msg in messages_history:
        item = {
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        }
        if msg.get("reasoning_details"):
            item["reasoning_details"] = msg.get("reasoning_details")
        formatted_messages.append(item)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Dynamic Payload Configuration
    payload = {
        "model": model_id,
        "messages": formatted_messages,
        "reasoning": {"enabled": True}  # Reasoning tokens open rakhega for supported models
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
            message_obj = response_json['choices'][0].get('message', {})
            
            ai_content = message_obj.get('content', '')
            ai_reasoning = message_obj.get('reasoning_details', None)
            
            if not ai_content and 'text' in message_obj:
                ai_content = message_obj.get('text', '')
            
            return {
                "success": True,
                "content": ai_content if ai_content else "Data processed successfully.",
                "reasoning_details": ai_reasoning
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
