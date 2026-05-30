from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import config
from sheets.reader import get_client
from sheets.writer import write_to_sheet

app = FastAPI(title="Marketing Agent Review UI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def read_sheet(sheet_name: str):
    gc = get_client()
    sheet = gc.open_by_key(config.SPREADSHEET_ID)
    worksheet = sheet.worksheet(sheet_name)
    return worksheet.get_all_records()

@app.get("/api/content")
def get_content():
    rows = read_sheet(config.SHEET_CONTENT)
    return {"rows": rows}

@app.post("/api/approve/{index}")
def approve(index: int):
    rows = read_sheet(config.SHEET_CONTENT)
    if index >= len(rows):
        return {"error": "Index out of range"}
    rows[index]["Review Status"] = "Approved"
    write_to_sheet(config.SHEET_REVIEW, rows)
    return {"status": "approved", "topic": rows[index].get("Topic")}

@app.post("/api/reject/{index}")
def reject(index: int):
    rows = read_sheet(config.SHEET_CONTENT)
    if index >= len(rows):
        return {"error": "Index out of range"}
    rows[index]["Review Status"] = "Rejected"
    write_to_sheet(config.SHEET_REVIEW, rows)
    return {"status": "rejected", "topic": rows[index].get("Topic")}

@app.get("/", response_class=HTMLResponse)
def review_ui():
    with open("ui/review.html", "r", encoding="utf-8") as f:
        return f.read()