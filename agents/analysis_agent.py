import logging
from groq import Groq
import config
from sheets.reader import get_client
from sheets.writer import write_to_sheet

logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

client = Groq(api_key=config.GROQ_API_KEY)

def read_research():
    gc = get_client()
    sheet = gc.open_by_key(config.SPREADSHEET_ID)
    worksheet = sheet.worksheet(config.SHEET_RESEARCH)
    rows = worksheet.get_all_records()
    return rows

def run_analysis(row: dict) -> dict:
    topic = row.get("Topic", "")
    product = row.get("Product", "")
    target_audience = row.get("Target Audience", "")
    research_output = row.get("Research Output", "")

    logger.info(f"Analysing: {topic}")

    prompt = f"""You are a senior marketing strategist.

Based on the research below, provide a strategic analysis:

RESEARCH:
{research_output}

Topic: {topic}
Product: {product}
Target Audience: {target_audience}

Provide:
1. SWOT Analysis (Strengths, Weaknesses, Opportunities, Threats - 2 points each)
2. Top 3 Marketing Channels to focus on (with reasoning)
3. Recommended Campaign Angle (1 paragraph)
4. KPIs to track (5 metrics)
5. Budget Allocation Recommendation (% split across channels)

Be specific and actionable."""

    response = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1024,
    )

    analysis_output = response.choices[0].message.content

    return {
        "Topic": topic,
        "Product": product,
        "Target Audience": target_audience,
        "Research Output": research_output,
        "Analysis Output": analysis_output,
        "Status": "Analysed"
    }

def run():
    logger.info("Starting Analysis Agent...")
    rows = read_research()

    if not rows:
        logger.warning("No research rows found.")
        return

    results = []
    for row in rows:
        try:
            result = run_analysis(row)
            results.append(result)
            logger.info(f"Analysis complete for: {row.get('Topic')}")
        except Exception as e:
            logger.error(f"Error processing row {row}: {e}")

    write_to_sheet(config.SHEET_ANALYSIS, results)
    logger.info(f"Analysis Agent done. {len(results)} rows written.")

if __name__ == "__main__":
    run()