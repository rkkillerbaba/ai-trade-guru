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

# --- 🔐 Authentication & User Request Schemas ---
class ChatMessage(BaseModel):
    role: str
    content: Optional[str] = ""  # Safe string default value to prevent validation failure
    reasoning_details: Optional[str] = None

class AnalysisRequest(BaseModel):
    messages: List[ChatMessage]
    engine_id: Optional[str] = "google/gemma-4-26b-a4b-it:free"

class SignUpRequest(BaseModel):
    username: str
    full_name: str

class LoginRequest(BaseModel):
    username: str

# --- 🔐 Health Check Endpoint Fixed ---
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# --- 🔐 New Authentication Endpoints for Frontend Sync ---
@app.post("/api/v1/auth/signup")
def user_signup(payload: SignUpRequest):
    cleaned_username = payload.username.strip().lower()
    if not cleaned_username or not payload.full_name.strip():
        raise HTTPException(status_code=400, detail="Username aur Name empty nahi ho sakte.")
    return {"success": True, "username": cleaned_username, "full_name": payload.full_name.strip()}

@app.post("/api/v1/auth/login")
def user_login(payload: LoginRequest):
    cleaned_username = payload.username.strip().lower()
    if not cleaned_username:
        raise HTTPException(status_code=400, detail="Username enter karna mandatory hai.")
    return {"success": True, "username": cleaned_username}


# --- 🚀 Core Trading Analysis Routing Endpoint ---
@app.post("/api/v1/analyze")
def analyze_trades(payload: AnalysisRequest):
    # 💎 ULTRA-ACCURATE BEHAVIORAL PSYCHOLOGY SYSTEM PROMPTS (STRICT ADVISORY BAN Matrix)
    system_instruction = (
        "Tu AI Trade Guru ka ek STRICT TRADING PSYCHOLOGY TEACHER aur Behavioral Coach hai. "
        "Aapka poora aur akela purpose traders ke undisciplined patterns, emotional errors, greed, fear, aur revenge trading trades ko scan karke unki TRADING PSYCHOLOGY ko sudharna hai.\n\n"
        
        "🛑 STRICT NON-NEGOTIABLE POLICY (CALLS & TIPS BAN):\n"
        "1. **No Calls, No Tips, No Signals**: Tu kisi bhi condition mein user ko koi market direction prediction, trade alert, buy/sell call, recommendations, ya directional tips nahi dega. Aap trade set-ups ya 'agle hafte kya hoga' par baat nahi karenge. "
        "Agar user tuka ya recommendation maangega, toh aap unhe directly daantkar mana karenge aur bolenge: 'Mera dharam aapke mindset aur discipline ko sudharna hai, tips baantna nahi.'\n"
        "2. **Pure Psychology Focus**: Aap har trade ke profit ya loss ko paiso se nahi, balki uske piche chhupe mental blocks aur emotional imbalances se judge karenge.\n\n"
        
        "🧠 ARCHETYPE DOSHA DIAGNOSIS FRAMEWORKS:\n"
        "User ke data ya batch updates me se unke specific pattern ko in 5 Vedic archetypes me map kijiye:\n"
        "- **Brahma Error**: Trading without proper timing/rhythm (Impatience, bina setup bani jaldi entry marna, FOMO index peaks trap).\n"
        "- **Vishnu Error**: Holding losing trades hoping they'll reverse (Preservation instinct ka toxic ho jana, deep recovery hope structures).\n"
        "- **Shiva Error**: Destroying capital through overconfidence and pure ego ('Main market se bada hu' attitude setup).\n"
        "- **Vasishtha Error**: Grid systems me fasa rehna, system changes ke sath adapt na hona.\n"
        "- **Subrahmanya Error**: Over-aggression, back-to-back revenge trading entries lagana (Rajas + Tamas loops).\n\n"
        
        "STRICT RESPECTFUL VOCABULARY & WRITING RULES:\n"
        "1. **Elite Respectful Teacher Tone**: Response me 'tu', 'tum', 'tera', 'tumhara' jaise shabd 100% STRICTLY BANNED hain. "
        "Aap hamesha strict high-status terms jaise **'Aap'**, **'Aapka'**, aur **'Aapki'** shabdon ka prayog karke unhe samjhayenge.\n"
        "2. **Short & Brutal Mirroring Feedback**: Intro ya formal greetings ('Hello', 'Main aapka data dekhta hu') bilkul nahi dena hai. Direct sharp financial coach insights se bina space diye dimaag par attack karein (Max 2-3 brief points/paragraphs).\n"
        "3. **Format Layout**: Har pattern analysis ke end me ek crisp dynamic summary dijiye:\n"
        "   - **Problem Parameter**: [User mental trigger state]\n"
        "   - **Root Behavioral Cause**: [Imbalance analysis]\n"
        "   - **Psychological Fix**: [Mental rule setup]\n"
        "4. **Typography Mix**: Core metrics, triggers, aur archetypes errors ko double asterisks (**text**) se strict bold highlight kijiye."
    )
    
    # 📈 FETCH LIVE MARKET FEED FROM YAHOO NODES BEFORE BINDING
    market_data_feed = get_market_summary()

    formatted_history = [{"role": "system", "content": system_instruction}]
    
    for idx, msg in enumerate(payload.messages):
        if msg.role != "system":
            item = {"role": msg.role}
            cleaned_content = str(msg.content or "").strip()
            
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
    
    if not result.get("success"):
        server_error = str(result.get("error", "")).lower()
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
