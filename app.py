from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv() # Load keys from .env file
GEMINI_MODEL = "gemini-2.0-flash-lite"
GROQ_MODEL = "llama-3.3-70b-versatile"

print(f"DEBUG: Gemini Model: {GEMINI_MODEL}")
print(f"DEBUG: Gemini Key: {os.environ.get('GEMINI_API_KEY', 'NOT FOUND')[:6]}...")
print(f"DEBUG: Groq Key: {os.environ.get('GROQ_API_KEY', 'NOT FOUND')[:6]}...")

app = FastAPI(title="NagarSeva AI Predictor")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ComplaintInput(BaseModel):
    category: str
    title: str
    description: str

@app.post("/predict")
def predict_complaint(data: ComplaintInput):
    api_key_gemini = os.environ.get("GEMINI_API_KEY")
    api_key_groq = os.environ.get("GROQ_API_KEY")

    prompt = f"""You are an advanced text classifier for the NagarSeva municipal CRM system.
Analyze the following citizen complaint and output a pure JSON object categorizing it.
Do NOT use markdown block wrappers (like ```json), output strictly the JSON object.

Allowed Departments:
Allowed Departments:
- Roads & Pothole Maintenance
- Street Lighting & Electricals
- Piped Water Supply & Tankers
- Underground Sewerage & Drainage
- Open Drains & Culvert Cleaning
- Solid Waste Management (Waste Collection)
- Street Sweeping & Sanitation
- Public Toilets Maintenance
- Parks, Playgrounds & Open Spaces
- Property Tax & Revenue
- Birth, Death & Marriage Registration
- Building Plan & Construction Approval
- Encroachment Removal (Public Land)
- Illegal Construction Control
- Stray Dog & Animal Menace
- Vector Control (Mosquitoes/Dengue/Malaria)
- Public Health & Vaccination Centers
- Trade Licenses (Shops & Establishments)
- Horticulture & Tree Cutting
- Traffic Signals & Road Signage
- Municipal Building Maintenance
- Slum Development & Urban Poverty Alleviation
- Advertising (Hoardings & Signboards)
- Disaster Management (Fire & Flooding)
- Markets & Street Vending Zones
- Community Halls & Libraries
- Crematoriums & Burial Grounds
- Municipal Schools & Education
- Estate & Land Records
- Heritage Conservation
- IT & E-Governance Services
- Law & Legal Department
- Citizen Service Centers (CSC/Jan Seva)
- Department of Telecommunications
- Department of Posts (India Post)
- CBIC (GST & Customs)
- Department of Financial Services (Banking & Insurance)
- Ministry of Railways
- Ministry of Road Transport and Highways
- Ministry of Power
- Ministry of Housing and Urban Affairs
- Ministry of Civil Aviation
- Ministry of Petroleum and Natural Gas
- Ministry of Education
- Ministry of Health and Family Welfare
- Ministry of Women and Child Development
- Ministry of Social Justice and Empowerment
- Ministry of Labour and Employment
- DARPG (CPGRAMS Nodal)
- Ministry of Personnel, Public Grievances and Pensions
- Ministry of Home Affairs
- Ministry of External Affairs
- Department of Atomic Energy
- Department of Space (ISRO)
- Ministry of AYUSH
- Ministry of Environment, Forest and Climate Change
- General Administration

Allowed Priorities: Very Low, Low, Medium, High, Severe (Immediate Action)

Complaint Title: {data.title}
Complaint Category Selected: {data.category}
Complaint Description: {data.description}

You must respond with ONLY a JSON object exactly matching this schema:
{{
  "ai_department": "<one of the Allowed Departments>",
  "ai_priority": "<Very Low, Low, Medium, High, or Severe (Immediate Action) based on urgency and public impact>",
  "ai_summary": "<A 1-sentence professional summary of the issue>",
  "raw_severity_score": <A float between 1.0 (least severe) and 10.0 (catastrophic safety hazard)>
}}"""

    # 1. Try Groq first if key exists (much more reliable free tier)
    if api_key_groq:
        try:
            print("DEBUG: Attempting classification via Groq...")
            url_groq = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key_groq}", "Content-Type": "application/json"}
            payload = {
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }
            resp = requests.post(url_groq, json=payload, headers=headers)
            resp.raise_for_status()
            parsed = resp.json()['choices'][0]['message']['content']
            res = json.loads(parsed)
            return {
                "ai_category": data.category,
                "ai_department": res.get("ai_department", "General Administration"),
                "ai_priority": res.get("ai_priority", "Medium"),
                "ai_summary": res.get("ai_summary", "Analyzed by Groq AI."),
                "raw_severity_score": float(res.get("raw_severity_score", 5.0))
            }
        except Exception as ge:
            print(f"Groq failed: {ge}")
            if not api_key_gemini: return {"error": f"Groq Error: {str(ge)}"}

    # 2. Fallback to Gemini
    if not api_key_gemini:
        return {"error": "No API keys (Gemini or Groq) found in your .env file."}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={api_key_gemini}"
    try:
        response = requests.post(url, json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 300}
        }, headers={"Content-Type": "application/json"})
        
        response.raise_for_status()
        resp_data = response.json()
        
        text = None
        if "candidates" in resp_data and len(resp_data["candidates"]) > 0:
             if "content" in resp_data["candidates"][0] and "parts" in resp_data["candidates"][0]["content"]:
                  text = resp_data["candidates"][0]["content"]["parts"][0].get("text")
                      
        if not text: return {"error": "Empty sentiment from Gemini."}
            
        text = text.strip()
        if text.startswith("```json"): text = text[7:]
        if text.startswith("```"): text = text[3:]
        if text.endswith("```"): text = text[:-3]
        text = text.strip()
        parsed_result = json.loads(text)
        
        return {
            "ai_category": data.category,
            "ai_department": parsed_result.get("ai_department", "General Administration"),
            "ai_priority": parsed_result.get("ai_priority", "Medium"),
            "ai_summary": parsed_result.get("ai_summary", "Analyzed by Gemini AI."),
            "raw_severity_score": float(parsed_result.get("raw_severity_score", 5.0))
        }

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        print(f"Gemini API Error {status_code}: {e.response.text}")
        if status_code == 429:
             return {"error": "Gemini Rate Limit Exceeded. Tip: Get a free key from console.groq.com and add GROQ_API_KEY to your .env for a much higher limit."}
        return {"error": f"Gemini API Error: {str(e)}"}
class AdminLogin(BaseModel):
    username: str
    password: str

@app.post("/admin/login")
def admin_login(data: AdminLogin):
    env_user = os.environ.get("ADMIN_USERNAME", "admin")
    env_pass = os.environ.get("ADMIN_PASSWORD", "nagarseva2026")
    
    if data.username == env_user and data.password == env_pass:
        return {"success": True}
    return {"success": False, "error": "Invalid credentials"}

class LetterRequest(BaseModel):
    id: str
    full_name: str
    category: str
    title: str
    description: str
    ai_department: str
    ai_priority: str
    status: str

@app.post("/generate_letter")
def generate_response_letter(data: LetterRequest):
    api_key_gemini = os.environ.get("GEMINI_API_KEY")
    api_key_groq = os.environ.get("GROQ_API_KEY")

    prompt = f"""You are a senior official at NagarSeva Municipal Corporation.
Write a formal, professional, and empathetic official response letter to this citizen complaint.
Include: acknowledgement, department handling it, realistic timeline, polite reassurance, official sign-off.

Complaint ID: {data.id}
Citizen Name: {data.full_name}
Category: {data.category}
Title: {data.title}
Description: {data.description}
Department Assigned: {data.ai_department}
Priority: {data.ai_priority}
Current Status: {data.status}

Write only the letter text. No extra commentary."""

    # Try Groq first for letter generation
    if api_key_groq:
        try:
            print("DEBUG: Generating letter via Groq...")
            url_groq = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key_groq}", "Content-Type": "application/json"}
            payload = {
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.4,
                "max_tokens": 1000
            }
            resp = requests.post(url_groq, json=payload, headers=headers)
            resp.raise_for_status()
            text = resp.json()['choices'][0]['message']['content']
            return {"letter": text}
        except Exception as ge:
            print(f"Groq letter failed: {ge}")
            if not api_key_gemini: return {"error": f"Groq Error: {str(ge)}"}

    # Fallback to Gemini
    if not api_key_gemini:
        return {"error": "No API keys configured."}
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={api_key_gemini}"
    try:
        response = requests.post(url, json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 700}
        }, headers={"Content-Type": "application/json"})
        
        response.raise_for_status()
        resp_data = response.json()
        text = resp_data["candidates"][0]["content"]["parts"][0].get("text")
        if not text: return {"error": "Empty Gemini response."}
        return {"letter": text}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
