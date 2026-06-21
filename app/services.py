# import os
# import google.generativeai as genai
# from dotenv import load_dotenv

# load_dotenv()

# def generate_health_remarks(glucose: float, haemoglobin: float, cholesterol: float) -> str:
#     api_key = os.getenv("GEMINI_API_KEY")
#     if not api_key:
#         return "AI analysis unavailable: Missing API Key."

#     try:
#         # Configuration setup for google-generativeai core
#         genai.configure(api_key=api_key)
        
#         prompt = (
#             f"Analyze these patient blood test results: Glucose: {glucose} mg/dL, "
#             f"Haemoglobin: {haemoglobin} g/dL, Cholesterol: {cholesterol} mg/dL. "
#             f"Provide a concise, professional 1-to-2 sentence health observation and risk notice. "
#             f"Do not format with markdown, headers, or bullet points."
#         )

#         model = genai.GenerativeModel('gemini-1.5-flash')
#         response = model.generate_content(prompt)
#         return response.text.strip()
        
#     except Exception as e:
#         return f"AI Generation skipped due to an error: {str(e)}"


# import os
# import google.generativeai as genai

# def generate_health_remarks(glucose: float, haemoglobin: float, cholesterol: float) -> str:
#     # 1. Safely pull the API Key from the environment
#     api_key = os.getenv("GEMINI_API_KEY")
#     if not api_key:
#         return "AI analysis unavailable: Missing API Key."
        
#     try:
#         # 2. Configure the library using your environment key
#         genai.configure(api_key=api_key)
        
#         # 3. Initialize the model structure safely
#         model = genai.GenerativeModel('gemini-pro')
        
#         prompt = (
#             f"Analyze these patient clinical numbers and write a short, 2-sentence medical remark: "
#             f"Glucose: {glucose} mg/dL, Haemoglobin: {haemoglobin} g/dL, Cholesterol: {cholesterol} mg/dL."
#         )
        
#         # 4. Generate content using standard legacy syntax
#         response = model.generate_content(prompt)
        
#         return response.text if response.text else "AI could not generate remarks."
        
#     except Exception as e:
#         return f"AI Generation skipped due to an error: {str(e)}"



# import os
# import http.client
# import json

# def generate_health_remarks(glucose: float, haemoglobin: float, cholesterol: float) -> str:
#     # 1. Safely pull the API Key from the environment
#     api_key = os.getenv("GEMINI_API_KEY")
#     if not api_key:
#         return "AI analysis unavailable: Missing API Key."
        
#     try:
#         # 2. Build our medical analytics instruction payload
#         prompt = (
#             f"Analyze these patient clinical numbers and write a short, 2-sentence medical remark: "
#             f"Glucose: {glucose} mg/dL, Haemoglobin: {haemoglobin} g/dL, Cholesterol: {cholesterol} mg/dL."
#         )
        
#         payload = {
#             "contents": [{
#                 "parts": [{"text": prompt}]
#             }]
#         }
        
#         # 3. Direct secure HTTP call bypasses local SDK package version blocks
#         conn = http.client.HTTPSConnection("generativelanguage.googleapis.com")
#         headers = {'Content-Type': 'application/json'}
        
#         # Accessing the standard flash model endpoint
#         endpoint = f"/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
#         conn.request("POST", endpoint, body=json.dumps(payload), headers=headers)
#         res = conn.getresponse()
#         data = res.read()
        
#         # 4. Parse response back out
#         response_json = json.loads(data.decode("utf-8"))
        
#         if res.status != 200:
#             error_msg = response_json.get("error", {}).get("message", "Unknown API authorization error.")
#             return f"AI Error ({res.status}): {error_msg}"
            
#         # Extract the text string response safely from the JSON tree
#         remarks = response_json['candidates'][0]['content']['parts'][0]['text']
#         return remarks.strip()
        
#     except Exception as e:
#         return f"AI Generation skipped due to an error: {str(e)}"

import os
import requests

def generate_health_remarks(glucose: float, haemoglobin: float, cholesterol: float) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "AI analysis unavailable: Missing API Key."
        
    # Clean up the key string to ensure no trailing returns or whitespaces exist
    api_key = api_key.strip()
        
    # FIXED: Updated URL path to use v1beta alongside the active gemini-2.5-flash production tier
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    prompt = (
        f"Analyze these patient clinical numbers and write a short, 2-sentence medical remark: "
        f"Glucose: {glucose} mg/dL, Haemoglobin: {haemoglobin} g/dL, Cholesterol: {cholesterol} mg/dL."
    )
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        # Deliver the diagnostic payload securely to the Google API cluster
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        # Catch key verification blocks
        if response.status_code in [400, 403]:
            return f"AI Error: Invalid API Key authentication (Status {response.status_code}). Please double-check your key."
            
        if response.status_code != 200:
            return f"AI Error (Status {response.status_code}): {response.text[:100]}"
            
        response_json = response.json()
        remarks = response_json['candidates'][0]['content']['parts'][0]['text']
        return remarks.strip()
        
    except requests.exceptions.Timeout:
        return "AI Error: The request timed out. Please check your internet connection."
    except Exception as e:
        return f"AI Generation skipped due to an error: {str(e)}"