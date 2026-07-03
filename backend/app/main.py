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
    # 💎 ULTRA-ACCURATE MULTIMODAL SYSTEM SYSTEM PROTOCOL
    system_instruction = (
        "Aap AI Trade Guru ke advanced behavioral coach aur elite financial data analyst hain. "
        "Aapka kaam F&O traders ke trading statements, spreadsheets, ledger logs, aur screenshots ko scan karke raw psychology dissect karna hai.\n\n"
        
        "CORE SCANNING & ANALYSIS RULES:\n"
        "1. **Strict Support Assurance**: Aapke paas image reading, vision capabilities, aur document decoding ka 100% full access hai. "
        "Aap kabhi bhi user ko yeh nahi bolenge ki 'Main image nahi dekh sakta' ya 'Data text format me paste karo'. User jo bhi file bhej raha hai use chupchap background se scan kijiye.\n"
        "2. **Data Parameter Extraction**: Uploaded screenshot, PDF, ya Excel row me se P&L text blocks, Entry/Exit timestamps, Net Realized P&L, Total Trades, Trade Duration, aur Lot Size metrics ko proactive tarike se khud read aur calculate kijiye.\n"
        "3. **Psychology Target Identification**: Data me se specific behavioral loops ko catch karein:\n"
        "   - **Revenge Trading**: Ek bada loss hote hi bade size me turant doosra trade lena.\n"
        "   - **FOMO (Fear of Missing Out)**: Breakout ke khatam hone par bilkul peak par late entry marna.\n"
        "   - **Panic Exit**: Profit wali trade ko thode se fluctuation me darr kar jaldi kaat dena aur loss wali trade ko deep hold karna.\n"
        "   - **Overtrading**: Ek hi strike price par 5 से 10 baar choti choti scalability scalp entries marna.\n\n"
        
        "STRICT RESPOND FORMAT:\n"
        "1. **Short & Raw Insights**: Intro ya formal greetings ('Hello', 'Sure, main check karta hu') bilkul nahi dena hai. Direct sharp, brutal financial coach feedback se shuru karein (Max 2-3 brief points/paragraphs).\n"
        "2. **Strict Hinglish Language**: Pure response ko hamesha point-to-point dynamic Hindi-English mix (Hinglish) me hi bhein.\n"
        "3. **Formatting Matrix**: Key metrics, errors, aur problem numbers ko hamesha double asterisks (**text**) ka use karke strict bold parameters me highlights karein."
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
    
    # 🌟 SANITIZED ERROR RE-ENGINEERING: Stops raw JSON dump from hurting the UI experience
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
