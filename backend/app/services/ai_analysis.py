import os
import requests
import json

def generate_trader_insights(messages_history):
    """
    OpenRouter API Wrapper tailored specifically for google/gemma-4-26b-a4b-it:free
    Preserves and outputs deep reasoning paths.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    if not api_key:
        return {
            "success": False,
            "error": "Missing OPENROUTER_API_KEY environment variable on Render."
        }

    # Format incoming payload to strictly ensure correct key references
    formatted_messages = []
    for msg in messages_history:
        item = {
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        }
        # OpenRouter documentation says pass back reasoning_details unmodified
        if msg.get("reasoning_details"):
            item["reasoning_details"] = msg.get("reasoning_details")
        formatted_messages.append(item)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "google/gemma-4-26b-a4b-it:free",
        "messages": formatted_messages,
        "reasoning": {"enabled": True}  # Enforces active thinking logs
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"OpenRouter Gateway Error {response.status_code}: {response.text}"
            }
            
        response_json = response.json()
        
        # OpenRouter response object extraction
        if 'choices' in response_json and len(response_json['choices']) > 0:
            message_obj = response_json['choices'][0]['message']
            
            ai_content = message_obj.get('content', '')
            ai_reasoning = message_obj.get('reasoning_details', None)
            
            return {
                "success": True,
                "content": ai_content,
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
