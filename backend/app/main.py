from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
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

# 🚀 Request Schema Updated to accept model name dynamically from frontend
class AnalysisRequest(BaseModel):
    messages: List[ChatMessage]
    model_name: Optional[str] = "google/gemma-4-26b-a4b-it:free" # Fallback if missing

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/analyze")
def analyze_trades(payload: AnalysisRequest):
    # System Instruction handling for both file texts and text messages
    system_instruction = (
        "Aap AI Trade Guru ke advanced behavioral coach hain. F&O traders ke behavioral mistakes ko deeply analyze kijiye.\n"
        "STRICT RESPOND RULES:\n"
        "1. Response ekdam short, crisp aur core insights par hona chahiye (Max 2-3 brief points/paragraphs).\n"
        "2. Agar trader koi log file ya spreadsheet raw text upload kare, toh usme se loss patterns, emotional loops (revenge, FOMO, panic) dhoondhein aur short blunt feedback dein.\n"
        "3. Response strictly Hinglish language me point-to-point bina kisi lambe introduction ke bhein."
    )
    
    formatted_history = [{"role": "system", "content": system_instruction}]
    
    for msg in payload.messages:
        if msg.role != "system":
            item = {"role": msg.role}
            if msg.content:
                item["content"] = msg.content
            if msg.reasoning_details:
                item["reasoning_details"] = msg.reasoning_details
            formatted_history.append(item)
        
    # 🔄 Frontend se aaya hua selected model name yahan service function me pass ho raha hai
    result = generate_trader_insights(formatted_history, model_id=payload.model_name)
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Internal Server Error"))
        
    return result
