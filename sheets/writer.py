import gspread
from google.oauth2.service_account import Credentials
import config
from sheets.reader import get_client


def write_to_sheet(sheet_name: str, rows: list):
    client = get_client()
    sheet = client.open_by_key(config.SPREADSHEET_ID)

    try:
        worksheet = sheet.worksheet(sheet_name)
        worksheet.clear()

    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(
            title=sheet_name,
            rows=100,
            cols=20
        )

    if not rows:
        return

    headers = list(rows[0].keys())

    values = [headers] + [
        [str(row.get(h, "")) for h in headers]
        for row in rows
    ]

    worksheet.update(values, "A1")