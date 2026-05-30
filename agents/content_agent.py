import logging
from groq import Groq
import config
from sheets.reader import get_client
from sheets.writer import write_to_sheet

logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

client = Groq(api_key=config.GROQ_API_KEY)

def read_analysis():
    gc = get_client()
    sheet = gc.open_by_key(config.SPREADSHEET_ID)
    worksheet = sheet.worksheet(config.SHEET_ANALYSIS)
    rows = worksheet.get_all_records()
    return rows

def run_content(row: dict) -> dict:
    topic = row.get("Topic", "")
    product = row.get("Product", "")
    target_audience = row.get("Target Audience", "")
    analysis_output = row.get("Analysis Output", "")

    logger.info(f"Generating content for: {topic}")

    prompt = f"""You are an expert marketing copywriter.

Based on the analysis below, create a complete marketing content package:

ANALYSIS:
{analysis_output}

Topic: {topic}
Product: {product}
Target Audience: {target_audience}

Generate the following:

1. EMAIL SUBJECT LINE (3 options)
2. EMAIL BODY (150-200 words, professional tone)
3. LINKEDIN POST (100-150 words)
4. TWITTER/X THREAD (5 tweets, each under 280 chars)
5. AD HEADLINE (5 options, under 60 chars each)
6. AD DESCRIPTION (2 options, under 90 chars each)
7. CALL TO ACTION (3 options)

Make it compelling, specific, and tailored to {target_audience}."""

    response = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=2048,
    )

    content_output = response.choices[0].message.content

    return {
        "Topic": topic,
        "Product": product,
        "Target Audience": target_audience,
        "Analysis Output": analysis_output,
        "Content Output": content_output,
        "Status": "Content Ready"
    }

def run():
    logger.info("Starting Content Agent...")
    rows = read_analysis()

    if not rows:
        logger.warning("No analysis rows found.")
        return

    results = []
    for row in rows:
        try:
            result = run_content(row)
            results.append(result)
            logger.info(f"Content generated for: {row.get('Topic')}")
        except Exception as e:
            logger.error(f"Error processing row {row}: {e}")

    write_to_sheet(config.SHEET_CONTENT, results)
    logger.info(f"Content Agent done. {len(results)} rows written.")

if __name__ == "__main__":
    run()