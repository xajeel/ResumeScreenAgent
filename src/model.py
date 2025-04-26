import google.generativeai as genai
from dotenv import load_dotenv
import os
import re

from utils.prompt import model_prompt

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

def extract_candidate_info(job_description, cv_data):
    genai.configure(api_key=api_key)
    prompt = model_prompt(job_description, cv_data)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    clean_response = re.sub(r"```json|```", "", response.text).strip()
    return clean_response