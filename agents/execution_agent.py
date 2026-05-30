import logging
from groq import Groq
from datetime import datetime
import config
from sheets.reader import get_client
from sheets.writer import write_to_sheet

logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

client = Groq(api_key=config.GROQ_API_KEY)

def read_approved():
    gc = get_client()
    sheet = gc.open_by_key(config.SPREADSHEET_ID)
    worksheet = sheet.worksheet(config.SHEET_REVIEW)
    rows = worksheet.get_all_records()
    approved = [r for r in rows if r.get("Review Status") == "Approved"]
    return approved

def run_execution(row: dict) -> dict:
    topic = row.get("Topic", "")
    product = row.get("Product", "")
    target_audience = row.get("Target Audience", "")
    content_output = row.get("Content Output", "")

    logger.info(f"Creating execution plan for: {topic}")

    prompt = f"""You are a marketing campaign manager.

Create a detailed execution plan for this approved campaign:

Topic: {topic}
Product: {product}
Target Audience: {target_audience}

APPROVED CONTENT:
{content_output}

Provide:
1. CAMPAIGN TIMELINE (Week 1-4 breakdown)
2. CHANNEL EXECUTION PLAN (specific actions per channel)
3. BUDGET BREAKDOWN (specific $ amounts, assume $5000 total budget)
4. SUCCESS METRICS (specific targets for each KPI)
5. LAUNCH CHECKLIST (10 items)
6. RISK MITIGATION (3 potential risks + solutions)

Be specific with dates, numbers, and actionable steps."""

    response = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2048,
    )

    execution_output = response.choices[0].message.content

    return {
        "Topic": topic,
        "Product": product,
        "Target Audience": target_audience,
        "Content Output": content_output,
        "Execution Plan": execution_output,
        "Campaign Status": "Ready to Launch",
        "Created At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def run():
    logger.info("Starting Execution Agent...")
    rows = read_approved()

    if not rows:
        logger.warning("No approved campaigns found.")
        return

    logger.info(f"Found {len(rows)} approved campaign(s).")
    results = []
    for row in rows:
        try:
            result = run_execution(row)
            results.append(result)
            logger.info(f"Execution plan created for: {row.get('Topic')}")
        except Exception as e:
            logger.error(f"Error processing row {row}: {e}")

    write_to_sheet(config.SHEET_EXECUTION, results)
    logger.info(f"Execution Agent done. {len(results)} rows written.")

if __name__ == "__main__":
    run()