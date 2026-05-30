import logging
from groq import Groq
import config
from sheets.reader import read_inputs
from sheets.writer import write_to_sheet

logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

client = Groq(api_key=config.GROQ_API_KEY)

def run_research(row: dict) -> dict:
    topic = row.get("Topic", "")
    product = row.get("Product", "")
    target_audience = row.get("Target Audience", "")

    logger.info(f"Researching: {topic} for {product}")

    prompt = f"""You are a marketing research expert.

Research the following and provide a structured report:
- Topic: {topic}
- Product/Service: {product}
- Target Audience: {target_audience}

Provide:
1. Market Overview (2-3 sentences)
2. Key Trends (3 bullet points)
3. Competitor Landscape (2-3 sentences)
4. Target Audience Insights (2-3 sentences)
5. Key Opportunities (3 bullet points)

Be concise and data-driven."""

    response = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1024,
    )

    research_output = response.choices[0].message.content

    return {
        "Topic": topic,
        "Product": product,
        "Target Audience": target_audience,
        "Research Output": research_output,
        "Status": "Researched"
    }

def run():
    logger.info("Starting Research Agent...")
    rows = read_inputs()

    if not rows:
        logger.warning("No input rows found.")
        return

    results = []
    for row in rows:
        try:
            result = run_research(row)
            results.append(result)
            logger.info(f"Research complete for: {row.get('Topic')}")
        except Exception as e:
            logger.error(f"Error processing row {row}: {e}")

    write_to_sheet(config.SHEET_RESEARCH, results)
    logger.info(f"Research Agent done. {len(results)} rows written.")

if __name__ == "__main__":
    run()