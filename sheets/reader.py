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


def read_sheet(sheet_name):
    """
    Generic sheet reader.

    Example:
        read_sheet(config.SHEET_ACCOUNTS)
        read_sheet(config.SHEET_CONTACTS)
    """

    client = get_client()

    spreadsheet = client.open_by_key(
        config.SPREADSHEET_ID
    )

    worksheet = spreadsheet.worksheet(
        sheet_name
    )

    return worksheet.get_all_records()