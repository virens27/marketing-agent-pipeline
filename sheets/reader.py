import gspread
from google.oauth2.service_account import Credentials
import config

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_client():
    creds = Credentials.from_service_account_file(
        config.GOOGLE_SHEETS_CREDENTIALS_FILE,
        scopes=SCOPES
    )
    return gspread.authorize(creds)

def read_inputs():
    client = get_client()
    sheet = client.open_by_key(config.SPREADSHEET_ID)
    worksheet = sheet.worksheet(config.SHEET_INPUT)
    rows = worksheet.get_all_records()
    return rows