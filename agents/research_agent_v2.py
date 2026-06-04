import logging
from datetime import datetime

from groq import Groq

import config
from sheets.reader import read_sheet
from sheets.writer import write_to_sheet

logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

client = Groq(api_key=config.GROQ_API_KEY)


def generate_research(account):

    account_id = account.get("Account ID", "")
    company_name = account.get("Account Name", "")
    website = account.get("Website", "")
    industry = account.get("Industry", "")
    country = account.get("Country", "")
    trigger_event = account.get("Trigger Event", "")

    logger.info(f"Researching {company_name}")

    prompt = f"""
You are a B2B Account Research Analyst.

Research this company:

Company Name: {company_name}
Website: {website}
Industry: {industry}
Country: {country}
Trigger Event: {trigger_event}

Generate:

1. Research Summary (3-5 lines)

2. Key Findings
(3-5 concise findings)

3. Competitors
(top competitors)

4. Industry Trends
(relevant trends)

5. Determine if findings are Fact or Hypothesis

Return ONLY in this format:

Research Summary:
...

Key Findings:
...

Competitors:
...

Industry Trends:
...

Fact/Hypothesis:
Fact

Confidence Score:
9
"""

    response = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=1000
    )

    output = response.choices[0].message.content

    research_summary = output
    key_findings = output
    competitors = output
    industry_trends = output

    fact_hypothesis = "Fact"
    confidence_score = 9

    return {
        "Research ID": f"RES-{account_id.split('-')[1]}",
        "Account ID": account_id,
        "Source URL": website,
        "Source Type": "Company Website",
        "Research Date": datetime.today().strftime("%d/%m/%Y"),
        "Research Summary": research_summary,
        "Key Findings": key_findings,
        "Competitors": competitors,
        "Industry Trends": industry_trends,
        "Fact / Hypothesis": fact_hypothesis,
        "Confidence Score": confidence_score
    }


def run():

    logger.info("Starting Research Agent V2")

    accounts = read_sheet(config.SHEET_ACCOUNTS)

    if not accounts:
        logger.warning("No accounts found")
        return

    results = []

    for account in accounts:

        try:

            result = generate_research(account)

            results.append(result)

            logger.info(
                f"Research completed for {account.get('Account Name')}"
            )

        except Exception as e:

            logger.error(
                f"Error processing {account.get('Account Name')}: {e}"
            )

    write_to_sheet(
        config.SHEET_RESEARCH_CACHE,
        results
    )

    logger.info(
        f"Research Cache updated with {len(results)} rows"
    )


if __name__ == "__main__":
    run()