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
        
    result = generate_trader_insights(formatted_history)
    
    # Check explicitly if integration failed
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Internal Server Error"))
        
    return result
