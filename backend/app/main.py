from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.ai_analysis import generate_trader_insights

app = FastAPI(title="AI Trade Guru Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str
    content: Optional[str] = None
    reasoning_details: Optional[str] = None

class AnalysisRequest(BaseModel):
    messages: List[ChatMessage]

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/analyze")
def analyze_trades(payload: AnalysisRequest):
    formatted_history = []
    for msg in payload.messages:
        item = {"role": msg.role}
        if msg.content:
            item["content"] = msg.content
        if msg.reasoning_details:
            item["reasoning_details"] = msg.reasoning_details
        formatted_history.append(item)
        
    try:
        result = generate_trader_insights(formatted_history)
        
        if isinstance(result, dict) and result.get("success"):
            # Check if AI actually generated content
            if not result.get("content"):
                return {
                    "success": True,
                    "content": "⚠️ OpenRouter returned an empty message. Please check if your model settings are correct or try a different prompt.",
                    "reasoning_details": "Response verified but payload content was empty."
                }
            return result
            
        return {
            "success": True,
            "content": str(result.get("content", "⚠️ AI response parsing format anomaly.")),
            "reasoning_details": result.get("reasoning_details", None)
        }
    except Exception as e:
        # Pura precise error block UI par return karein taaki breakdown pata chale
        return {
            "success": True, 
            "content": f"🚨 OpenRouter Pipeline Alert: {str(e)}. Please check your API credits or token validity.",
            "reasoning_details": "Pipeline Exception Captured Safely."
        }
