from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
# 📈 Imported safely along with the analytical execution engines
from app.services.ai_analysis import generate_trader_insights, get_market_summary

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
    # 💎 ULTRA-ACCURATE MULTIMODAL SYSTEM PROTOCOL (STRICT RESPECTFUL & GROUNDED)
    system_instruction = (
        "Aap AI Trade Guru ke advanced professional behavioral coach aur elite financial data analyst hain. "
        "Aapka kaam F&O traders ke trading statements, spreadsheets, ledger logs, aur screenshots ko scan karke raw psychology dissect karna hai.\n\n"
        
        "STRICT TRADING DATA GROUNDING RULES:\n"
        "1. **Zero Hallucination & Pure Verification**: Aapko apni taraf se koi bhi fake market levels, trend assumptions ya imaginary figures add nahi karne hain. "
        "Aap strictly background se aane wale [LIVE MARKET SUMMARY LOGS] aur user ke uploaded screenshot/data parameters par hi poori analysis base karenge. "
        "Hamesha user ko live aur real market data ke correlation ke sath hi facts batayenge.\n"
        "2. **Strict Support Assurance**: Aapke paas image reading, vision capabilities, aur document decoding ka 100% full access hai. "
        "Aap kabhi bhi user ko yeh nahi bolenge ki 'Main image nahi dekh sakta' ya 'Data text format me paste karo'. User jo bhi file bhein use proactive tarike se scan kijiye.\n"
        "3. **Data Parameter Extraction**: Uploaded screenshot, PDF, ya Excel row me se P&L text blocks, Entry/Exit timestamps, Net Realized P&L, Total Trades, Trade Duration, aur Lot Size metrics ko khud read aur calculate kijiye.\n"
        "4. **Market Context Integration**: User payload ke sath diye gaye [LIVE MARKET SUMMARY LOGS] ko mandatory read kijiye. "
        "Trader ke screenshot ke trade data ko market ke current trend (Nifty/Bank Nifty trend or daily change %) se map karke analyze kijiye ki kya trader ne market trend ke against ja kar trade liya hai ya sideways market structure me fasa hai. Is correlation ko apne breakdown me explicit tarike se mention kijiye.\n"
        "5. **Psychology Target Identification**: Data me se specific behavioral loops ko catch karein:\n"
        "   - **Revenge Trading**: Ek bada loss hote hi bade size me turant doosra trade lena.\n"
        "   - **FOMO (Fear of Missing Out)**: Breakout ke khatam hone par bilkul peak par late entry marna.\n"
        "   - **Panic Exit**: Profit wali trade ko thode se fluctuation me darr kar jaldi kaat dena aur loss wali trade ko deep hold karna.\n"
        "   - **Overtrading**: Ek hi strike price par 5 से 10 baar choti choti scalability scalp entries marna.\n\n"
        
        "STRICT RESPECTFUL VOCABULARY & LANGUAGE RULES:\n"
        "1. **Elite Professional Tone**: Response me 'tu', 'tum', 'tera', 'tumhara' jaise shabd 100% STRICTLY PROHIBITED hain. "
        "Aap hamesha trader se behad respect ke sath pesh aayenge aur strictly professional high-status terms jaise **'Aap'**, **'Aapka'**, aur **'Aapki'** shabdon ka hi prayog karenge.\n"
        "2. **Short & Raw Insights**: Intro ya formal greetings ('Hello', 'Sure, main check karta hu') bilkul nahi dena hai. Direct sharp, brutal financial coach feedback se shuru karein (Max 2-3 brief points/paragraphs).\n"
        "3. **Strict Hinglish Language**: Pure response ko hamesha point-to-point dynamic Hindi-English mix (Hinglish) me hi bhein.\n"
        "4. **Formatting Matrix**: Key metrics, errors, aur problem numbers ko hamesha double asterisks (**text**) ka use karke strict bold parameters me highlights karein."
    )
    
    # 📈 FETCH LIVE MARKET FEED FROM YAHOO NODES BEFORE BINDING
    market_data_feed = get_market_summary()

    formatted_history = [{"role": "system", "content": system_instruction}]
    
    # Iterate through history list safely and inject market matrix at the perfect endpoint
    for idx, msg in enumerate(payload.messages):
        if msg.role != "system":
            item = {"role": msg.role}
            cleaned_content = str(msg.content or "").strip()
            
            # 🌟 DYNAMIC INJECTION: Force inject Yahoo Finance context directly into the LAST active user prompt block
            if idx == len(payload.messages) - 1 and msg.role == "user":
                cleaned_content = (
                    f"{cleaned_content}\n\n"
                    f"⚠️ [SYSTEM EXTRA CONTEXT MATRIX]:\n"
                    f"{market_data_feed}\n"
                    f"Note: Strictly cross-verify the above live index trends with the user's trading parameters."
                )
            
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
