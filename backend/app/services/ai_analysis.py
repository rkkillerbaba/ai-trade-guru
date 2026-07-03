import os
import requests
import json
import re

# Fallback sequence agar primary model fail ho jaye
MODEL_FALLBACK_SEQUENCE = [
    "google/gemma-4-26b-a4b-it:free",  # Primary: Gemini Pro
    "openai/gpt-oss-120b:free",        # Backup 1: GPT Pro
    "nvidia/nemotron-3-ultra-550b-a55b:free", # Backup 2: Nemotron Ultra
    "openai/gpt-oss-20b:free"          # Backup 3: GPT Lite
]

VALID_MODELS = {
    "google/gemma-4-26b-a4b-it:free": "Gemini Pro",
    "openai/gpt-oss-120b:free": "GPT Pro",
    "openai/gpt-oss-20b:free": "GPT Lite",
    "nvidia/nemotron-3-ultra-550b-a55b:free": "Nemotron Ultra"
}

def generate_trader_insights(messages_history, model_id="google/gemma-4-26b-a4b-it:free"):
    """
    Advanced Multi-Model Failover API wrapper. Agar selected model fail hota hai, 
    to yeh automatic doosre working models par switch kar jata hai bina user ko error dikhaye.
    """
    url = "https://openrouter.ai/api/v1/chat/completions"

    # Gather API keys pool
    api_keys_pool = [
        os.getenv("OPENROUTER_API_KEY_1"),
        os.getenv("OPENROUTER_API_KEY_2"),
        os.getenv("OPENROUTER_API_KEY_3"),
        os.getenv("OPENROUTER_API_KEY")
    ]
    active_keys = [key for key in api_keys_pool if key and str(key).strip()]
    
    if not active_keys:
        return {"success": False, "error": "Configuration Error: No active OpenRouter API keys found."}

    # Prepare dynamic models list: requested model will be tried first
    models_to_try = [model_id] + [m for m in MODEL_FALLBACK_SEQUENCE if m != model_id]

    # Parse and format multimodal layout safely
    formatted_messages = []
    for msg in messages_history:
        if isinstance(msg, dict):
            role = str(msg.get("role", "user")).strip()
            content_str = str(msg.get("content", "")).strip()
            
            if not content_str:
                continue

            # Target Supabase storage URLs for images
            image_match = re.search(r'(https://[^\s)]+\.(?:jpg|jpeg|png|webp|gif))', content_str, re.IGNORECASE)
            
            if image_match:
                image_url = image_match.group(1)
                clean_text = content_str.replace(f"[Asset Reference Ledger Data: {image_url}]", "").replace(image_url, "").strip()
                if not clean_text:
                    clean_text = "Analyze this trading dashboard screenshot carefully for cognitive biases and sizing errors."

                formatted_messages.append({
                    "role": role,
                    "content": [
                        {"type": "text", "text": clean_text},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                })
            else:
                formatted_messages.append({
                    "role": role,
                    "content": content_str
                })

    last_gateway_error = "Initialization log"

    # Loop 1: Models sequence try karega (Gemini -> GPT Pro -> Nemotron)
    for current_model in models_to_try:
        # Loop 2: Har model ke liye keys rotate karega agar key block ho
        for index, current_api_key in enumerate(active_keys):
            headers = {
                "Authorization": f"Bearer {current_api_key.strip()}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://ai-trade-guru.vercel.app",
                "X-OpenRouter-Title": "AI Trade Guru Professional"
            }

            payload = {
                "model": current_model,
                "messages": formatted_messages,
                "temperature": 0.4,
                "max_tokens": 1500
            }

            try:
                # 30 seconds timeout to prevent endless hanging logs
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
                
                # Check for rate limiting or busy nodes
                if response.status_code in [429, 503, 502, 408]:
                    last_gateway_error = f"Model {current_model} via Key-{index+1} busy (Status {response.status_code})"
                    continue # Key rotate karo, ya agle model par jao

                if response.status_code != 200:
                    last_gateway_error = f"Error {response.status_code} on {current_model}: {response.text}"
                    continue

                response_json = response.json()
                if 'choices' in response_json and len(response_json['choices']) > 0:
                    choice_item = response_json['choices'][0]
                    message_node = choice_item.get('message', {})
                    ai_content = message_node.get('content', '')
                    ai_reasoning = message_node.get('reasoning_details', None) or message_node.get('reasoning', None)

                    # Success! Return insights immediately
                    return {
                        "success": True,
                        "content": ai_content.strip(),
                        "reasoning_details": ai_reasoning,
                        "active_model": VALID_MODELS.get(current_model, "AI Core Engine")
                    }
                
            except requests.exceptions.Timeout:
                last_gateway_error = f"Timeout on model {current_model} using Key-{index+1}"
                continue
            except Exception as e:
                last_gateway_error = f"Exception error on cluster: {str(e)}"
                continue

    # Agar saare models aur saari keys exhaust ho jayein tabhi error dega
    return {
        "success": False, 
        "error": f"All AI engine nodes are currently unresponsive. Details: {last_gateway_error}"
    }
