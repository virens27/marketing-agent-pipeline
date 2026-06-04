import os
from dotenv import load_dotenv

load_dotenv()

# ==================================================
# GROQ CONFIGURATION
# ==================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

# ==================================================
# GOOGLE SHEETS CONFIGURATION
# ==================================================

GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv(
    "GOOGLE_SHEETS_CREDENTIALS_FILE",
    "credentials.json"
)

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# ==================================================
# SHEET NAMES (MENTOR REDESIGN)
# ==================================================

SHEET_ACCOUNTS = "ACCOUNTS"
SHEET_CONTACTS = "CONTACTS"
SHEET_RESEARCH_CACHE = "RESEARCH CACHE"
SHEET_CHALLENGE_MAP = "CHALLENGE MAP"
SHEET_DRAFT_CONTENT = "DRAFT CONTENT"
SHEET_REVIEW_QUEUE = "REVIEW QUEUE"
SHEET_CAMPAIGN_TRACKER = "CAMPAIGN TRACKER"
SHEET_PROMPT_LIBRARY = "PROMPT LIBRARY"
SHEET_LEARNING_LIBRARY = "LEARNING LIBRARY"

# ==================================================
# APP CONFIGURATION
# ==================================================

APP_ENV = os.getenv("APP_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")