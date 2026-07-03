import os
import requests
import json
import re

VALID_MODELS = {
    "google/gemma-4-26b-a4b-it:free": "Gemini Pro",
    "openai/gpt-oss-120b:free": "GPT Pro",
    "openai/gpt-oss-20b:free": "GPT Lite",
    "nvidia/nemotron-3-ultra-550b-a55b:free": "Nemotron Ultra"
}

def generate_trader_insights(messages_history, model_id="google/gemma-4-26b-a4b-it:free"):
    """
    Ultra-resilient OpenRouter API Wrapper with Multi-Account Key Rotation & Vision/OCR Capability.
    """
    url = "https://openrouter.ai/api/v1/chat/completions"

    api_keys_pool = [
        os.getenv("OPENROUTER_API_KEY_1"),
        os.getenv("OPENROUTER_API_KEY_2"),
        os.getenv("OPENROUTER_API_KEY_3"),
        os.getenv("OPENROUTER_API_KEY")
    ]
    
    active_keys = [key for key in api_keys_pool if key and str(key).strip()]
    
    if not active_keys:
        return {"success": False, "error": "Missing OPENROUTER_API_KEY configuration cluster."}

    if model_id not in VALID_MODELS:
        model_id = "google/gemma-4-26b-a4b-it:free"

    # 👁️ VISION & MULTIMODAL CONVERSION LAYERS
    formatted_messages = []
    for msg in messages_history:
        if isinstance(msg, dict):
            role = str(msg.get("role", "user")).strip()
            content_str = str(msg.get("content", "")).strip()
            
            if not content_str:
                continue

            # Check if content has a Supabase storage asset image link inside it
            # Regex to search for public/trader-logs uploads containing image extensions
            image_match = re.search(r'(https://[^\s)]+\.(?:jpg|jpeg|png|webp|gif))', content_str, re.IGNORECASE)
            
            if image_match:
                image_url = image_match.group(1)
                # Clean out the raw link from text description so prompt stays clean
                clean_text = content_str.replace(f"[Asset Reference Ledger Data: {image_url}]", "").replace(image_url, "").strip()
                if not clean_text:
                    clean_text = "Analyze this uploaded trading sheet snapshot dashboard deeply for behavioral flaws."

                # OpenRouter Standard Multimodal Input Structure
                formatted_messages.append({
                    "role": role,
                    "content": [
                        {
                            "type": "text",
                            "text": clean_text
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                })
            else:
                # Regular text/PDF/Excel row parsing
                formatted_messages.append({
                    "role": role,
                    "content": content_str
                })

    last_gateway_error = "No engine execution logs."

    for index, current_api_key in enumerate(active_keys):
        headers = {
            "Authorization": f"Bearer {current_api_key.strip()}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-trade-guru.vercel.app",
            "X-OpenRouter-Title": "AI Trade Guru"
        }

        payload = {
            "model": model_id,
            "messages": formatted_messages
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
            
            if response.status_code in [429, 422, 402]:
                last_gateway_error = f"Key-{index + 1} Error ({response.status_code}): {response.text}"
                continue
                
            if response.status_code != 200:
                last_gateway_error = f"Key-{index + 1} Status {response.status_code}: {response.text}"
                continue
                
            response_json = response.json()
            if 'choices' in response_json and len(response_json['choices']) > 0:
                choice_item = response_json['choices'][0]
                message_node = choice_item.get('message', {})
                ai_content = message_node.get('content', '')
                ai_reasoning = message_node.get('reasoning_details', None) or message_node.get('reasoning', None)

                return {
                    "success": True,
                    "content": ai_content.strip() if ai_content else "Insight processed successfully.",
                    "reasoning_details": ai_reasoning,
                    "active_model": VALID_MODELS[model_id]
                }
            else:
                last_gateway_error = f"Key-{index + 1} Empty choices structure."
                continue

        except Exception as e:
            last_gateway_error = f"Key-{index + 1} Connection error: {str(e)}"
            continue

    return {
        "success": False, 
        "error": f"Cluster execution fallback trace logs. Context: {last_gateway_error}"
    }
