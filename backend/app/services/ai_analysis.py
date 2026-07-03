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
        return {"success": False, "error": "Missing OPENROUTER_API_KEY env block."}

    if model_id not in VALID_MODELS:
        model_id = "google/gemma-4-26b-a4b-it:free"

    formatted_messages = []
    for msg in messages_history:
        formatted_messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ai-trade-guru.vercel.app",
        "X-OpenRouter-Title": "AI Trade Guru"
    }

    # Tight schema execution pass
    payload = {
        "model": model_id,
        "messages": formatted_messages,
        "stream": False
    }

    try:
        # Increased timeout to 45s because 405b models can take a bit to spin up initially on free clusters
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=45)
        
        if response.status_code != 200:
            return {"success": False, "error": f"OpenRouter status code {response.status_code}: {response.text}"}
            
        response_json = response.json()
        
        # 🧠 Super Flexible Deep Choice Extractor to guarantee extraction across Llama, Hermes, and OpenAI formats
        if 'choices' in response_json and len(response_json['choices']) > 0:
            choice_item = response_json['choices'][0]
            message_node = choice_item.get('message', {})
            
            ai_content = message_node.get('content', '')
            ai_reasoning = message_node.get('reasoning_details', None) or message_node.get('reasoning', None)
            
            # Sub-node alternative checks
            if not ai_content and 'text' in message_node:
                ai_content = message_node.get('text', '')
            if not ai_content and 'text' in choice_item:
                ai_content = choice_item.get('text', '')

            return {
                "success": True,
                "content": ai_content.strip() if ai_content else "Insight execution processed structural layout safely.",
                "reasoning_details": ai_reasoning
            }
        
        return {"success": False, "error": f"Payload processing parsing empty nodes: {json.dumps(response_json)}"}

    except Exception as e:
        return {"success": False, "error": f"Pipeline service level exception: {str(e)}"}
