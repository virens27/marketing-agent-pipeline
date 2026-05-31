from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
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

def update_review_sheet(index: int, status: str):
    gc = get_client()
    sheet = gc.open_by_key(config.SPREADSHEET_ID)

    # Read content sheet
    content_ws = sheet.worksheet(config.SHEET_CONTENT)
    rows = content_ws.get_all_records()

    if index >= len(rows):
        return None

    row = rows[index]
    row["Review Status"] = status
    row["Reviewed At"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Write to Review sheet — append or update
    try:
        review_ws = sheet.worksheet(config.SHEET_REVIEW)
    except:
        review_ws = sheet.add_worksheet(title=config.SHEET_REVIEW, rows=100, cols=20)

    # Get existing review rows
    existing = review_ws.get_all_records()

    # Check if this topic already exists — update it
    topic = row.get("Topic", "")
    updated = False
    for i, r in enumerate(existing):
        if r.get("Topic") == topic:
            existing[i] = row
            updated = True
            break

    if not updated:
        existing.append(row)

    # Rewrite the full review sheet
    if existing:
        headers = list(existing[0].keys())
        values = [headers] + [[str(r.get(h, "")) for h in headers] for r in existing]
        review_ws.clear()
        review_ws.update(values, "A1")

    return row

@app.get("/api/content")
def get_content():
    rows = read_sheet(config.SHEET_CONTENT)
    # Merge with review status if exists
    try:
        review_rows = read_sheet(config.SHEET_REVIEW)
        review_map = {r.get("Topic"): r.get("Review Status", "") for r in review_rows}
        for row in rows:
            topic = row.get("Topic", "")
            if topic in review_map:
                row["Review Status"] = review_map[topic]
    except:
        pass
    return {"rows": rows}

@app.post("/api/approve/{index}")
def approve(index: int):
    row = update_review_sheet(index, "Approved")
    if not row:
        return {"error": "Index out of range"}
    return {"status": "approved", "topic": row.get("Topic")}

@app.post("/api/reject/{index}")
def reject(index: int):
    row = update_review_sheet(index, "Rejected")
    if not row:
        return {"error": "Index out of range"}
    return {"status": "rejected", "topic": row.get("Topic")}

@app.get("/", response_class=HTMLResponse)
def review_ui():
    with open("ui/review.html", "r", encoding="utf-8") as f:
        return f.read()