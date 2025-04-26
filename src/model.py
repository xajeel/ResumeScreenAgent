from google.generativeai import genai 
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)