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
    Ultra-resilient OpenRouter API Wrapper with Multi-Account API Key Rotation.
    Automatically switches to backup keys if daily free limits are exhausted (Status 429/422).
    """
    url = "https://openrouter.ai/api/v1/chat/completions"

    # 📡 Gather all potential rotation keys from Render Environment Setup
    api_keys_pool = [
        os.getenv("OPENROUTER_API_KEY_1"),
        os.getenv("OPENROUTER_API_KEY_2"),
        os.getenv("OPENROUTER_API_KEY_3"),
        os.getenv("OPENROUTER_API_KE")  # Default fallback standard variable
    ]
    
    # Filter out empty or unconfigured keys to get a pristine active list
    active_keys = [key for key in api_keys_pool if key and str(key).strip()]
    
    if not active_keys:
        return {
            "success": False, 
            "error": "Missing OPENROUTER_API_KEY configuration cluster parameters on Render."
        }

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

    last_gateway_error = "No engine execution logs."

    # 🔄 RE-ENGINEERING LOOP: Try keys one after another if limits are hit
    for index, current_api_key in enumerate(active_keys):
        headers = {
            "Authorization": f"Bearer {current_api_key.strip()}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-trade-guru.vercel.app",
            "X-OpenRouter-Title": "AI Trade Guru"
        }

        # 🚀 FIX: Removed strict provider fallback to let Python code handle rotation smoothly
        payload = {
            "model": model_id,
            "messages": formatted_messages
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
            
            # ⚠️ If specific key hits daily limit (429) or token limits (422), log it and move to next key
            if response.status_code in [429, 422, 402]:
                print(f"⚠️ OpenRouter Cluster Notice: Key Index [{index + 1}] exhausted with status {response.status_code}. Rotating to backup...")
                last_gateway_error = f"Key-{index + 1} Error ({response.status_code}): {response.text}"
                continue
                
            # For other non-200 unexpected errors, log and check if backup key can save the request
            if response.status_code != 200:
                last_gateway_error = f"Key-{index + 1} Gateway Status {response.status_code}: {response.text}"
                continue
                
            # 🎉 SUCCESS: Request passed safely, parse response data matrix
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
                last_gateway_error = f"Key-{index + 1} Empty response structure: {json.dumps(response_json)}"
                continue

        except Exception as e:
            print(f"❌ Exception on Key Index [{index + 1}]: {str(e)}")
            last_gateway_error = f"Key-{index + 1} Connection error: {str(e)}"
            continue

    # 🛑 CRITICAL BREAKDOWN: If the loop ends, it means ALL keys in the pool failed or exhausted
    return {
        "success": False, 
        "error": f"All API Keys in cluster pool exhausted or returned failure routing logs. Trace: {last_gateway_error}"
    }
