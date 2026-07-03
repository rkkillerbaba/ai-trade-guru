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
        
        # Safe format check
        if isinstance(result, dict) and result.get("success"):
            return result
            
        # Fallback if internal process succeeded but payload format is bad
        return {
            "success": True,
            "content": str(result.get("content", "AI process done.")),
            "reasoning_details": result.get("reasoning_details", None)
        }
    except Exception as e:
        # Pura system fail hone se bachane ke liye fallback message send karein
        return {
            "success": True, 
            "content": f"⚠️ Guru Engine Service Alert: OpenRouter or AI Analysis initialization failed. Check your API token environment variables. (Log: {str(e)})",
            "reasoning_details": "Fallback Triggered: Exception captured during generation pipeline."
        }
