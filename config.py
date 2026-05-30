import os
from dotenv import load_dotenv

load_dotenv()

# Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "credentials.json")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# Sheet names
SHEET_INPUT = "Inputs"
SHEET_RESEARCH = "Research"
SHEET_ANALYSIS = "Analysis"
SHEET_CONTENT = "Content"
SHEET_REVIEW = "Review"
SHEET_EXECUTION = "Execution"

# App
APP_ENV = os.getenv("APP_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
