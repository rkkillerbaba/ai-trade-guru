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
    content: Optional[str] = ""  # Safe string default value to prevent validation failure
    reasoning_details: Optional[str] = None

class AnalysisRequest(BaseModel):
    messages: List[ChatMessage]
    engine_id: Optional[str] = "google/gemma-4-26b-a4b-it:free"

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/analyze")
def analyze_trades(payload: AnalysisRequest):
    system_instruction = (
        "Aap AI Trade Guru ke advanced behavioral coach hain. F&O traders ke behavioral mistakes ko deeply analyze kijiye.\n"
        "STRICT RESPOND RULES:\n"
        "1. Response ekdam short, crisp aur core insights par hona chahiye (Max 2-3 brief points/paragraphs).\n"
        "2. Agar trader koi PDF document, trading log file, ya spreadsheet raw text upload kare, toh usme se loss patterns, emotional loops (revenge trading, FOMO, panic exit) dhoondhein aur short blunt professional feedback dein.\n"
        "3. Response strictly Hinglish language me point-to-point bina kisi lambe introduction ke bhein.\n"
        "4. Key metrics aur specific problem terms ko highlight karne ke liye double asterisks (**text**) ka use karein."
    )
    
    formatted_history = [{"role": "system", "content": system_instruction}]
    
    for msg in payload.messages:
        if msg.role != "system":
            item = {"role": msg.role}
            # Clean string parsing and default fallbacks for raw background file objects
            cleaned_content = str(msg.content or "").strip()
            item["content"] = cleaned_content if cleaned_content else "User shared data context ledger matrix below."
            
            if msg.reasoning_details:
                item["reasoning_details"] = msg.reasoning_details
            formatted_history.append(item)
        
    result = generate_trader_insights(formatted_history, model_id=payload.engine_id)
    
    # 🌟 PREMIUM RE-ENGINEERING: All ugly raw traces are parsed into a single professional sentence block
    if not result.get("success"):
        server_error = str(result.get("error", "")).lower()
        
        # Smart detection for different routing bottleneck cases
        if any(err in server_error for err in ["429", "rate-limited", "exhausted", "limit"]):
            user_friendly_msg = "Free AI Engines par abhi traffic thoda zyada hai ya server temporary busy chal raha hai."
        else:
            user_friendly_msg = "AI Network pipeline communication nodes temporary refresh ho rahe hain."

        return {
            "success": True, 
            "content": (
                f"### ⚠️ Server Busy\n"
                f"{user_friendly_msg}\n\n"
                f"👉 Please 10-15 seconds ruk kar **Send Button** par fir se click karein ya dropdown menu se koi doosra model (jaise **GPT Pro**) select karke try karein."
            )
        }
        
    return result
