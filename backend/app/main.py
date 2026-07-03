from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.ai_analysis import generate_trader_insights

app = FastAPI(title="AI Trade Guru Backend")

# ================= CORS CONFIGURATION (MOST IMPORTANT) =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production me security ke liye yahan sirf apna Vercel URL bhi daal sakte hain
    allow_credentials=True,
    allow_methods=["*"],  # Saare methods (POST, GET, etc.) allowed hain
    allow_headers=["*"],  # Saare headers allowed hain
)
# ======================================================================

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
    # Pydantic models ko standard python dictionary list mein convert karein
    formatted_history = []
    for msg in payload.messages:
        item = {"role": msg.role}
        if msg.content:
            item["content"] = msg.content
        if msg.reasoning_details:
            item["reasoning_details"] = msg.reasoning_details
        formatted_history.append(item)
        
    result = generate_trader_insights(formatted_history)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
        
    return result
