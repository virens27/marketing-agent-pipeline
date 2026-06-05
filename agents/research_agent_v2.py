import json
import logging
from datetime import datetime

from groq import Groq

import config
from sheets.reader import read_sheet
from sheets.writer import write_to_sheet

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL)
)

logger = logging.getLogger(__name__)

client = Groq(
    api_key=config.GROQ_API_KEY
)


def generate_research(account):

    account_id = account.get("Account ID", "")
    company_name = account.get("Account Name", "")
    website = account.get("Website", "")
    industry = account.get("Industry", "")
    country = account.get("Country", "")
    trigger_event = account.get("Trigger Event", "")

    logger.info(f"Researching {company_name}")

    prompt = f"""
You are an Account Intelligence Research Agent.

Company Name:
{company_name}

Website:
{website}

Industry:
{industry}

Country:
{country}

Trigger Event:
{trigger_event}

Generate ONLY valid JSON.

Return EXACTLY in this format:

{{
    "research_summary": "",
    "key_findings": "",
    "competitors": "",
    "industry_trends": "",
    "fact_hypothesis": "Fact",
    "confidence_score": 9
}}

Rules:

- research_summary = 2-3 concise sentences
- key_findings = 3 short findings separated by commas
- competitors = comma separated competitor names
- industry_trends = comma separated trends
- fact_hypothesis = Fact or Hypothesis
- confidence_score = number between 1 and 10

Return JSON only.
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
        max_tokens=800
    )

    output = response.choices[0].message.content.strip()

    try:

        if output.startswith("```json"):
            output = output.replace("```json", "")
            output = output.replace("```", "")
            output = output.strip()

        data = json.loads(output)

    except Exception as e:

        logger.error(
            f"JSON Parsing Error for {company_name}: {e}"
        )

        logger.error(output)

        data = {
            "research_summary": output[:500],
            "key_findings": "",
            "competitors": "",
            "industry_trends": "",
            "fact_hypothesis": "Fact",
            "confidence_score": 5
        }

    return {

        "Research ID": f"RES-{account_id.split('-')[1]}",

        "Account ID": account_id,

        "Source URL": website,

        "Source Type": "Company Website",

        "Research Date": datetime.today().strftime(
            "%d/%m/%Y"
        ),

        "Research Summary":
            data.get(
                "research_summary",
                ""
            ),

        "Key Findings":
            data.get(
                "key_findings",
                ""
            ),

        "Competitors":
            data.get(
                "competitors",
                ""
            ),

        "Industry Trends":
            data.get(
                "industry_trends",
                ""
            ),

        "Fact / Hypothesis":
            data.get(
                "fact_hypothesis",
                "Fact"
            ),

        "Confidence Score":
            data.get(
                "confidence_score",
                8
            )
    }


def run():

    logger.info(
        "Starting Research Agent V2"
    )

    accounts = read_sheet(
        config.SHEET_ACCOUNTS
    )

    if not accounts:

        logger.warning(
            "No accounts found"
        )

        return

    results = []

    for account in accounts:

        try:

            result = generate_research(
                account
            )

            results.append(
                result
            )

            logger.info(
                f"Research completed for "
                f"{account.get('Account Name')}"
            )

        except Exception as e:

            logger.error(
                f"Error processing "
                f"{account.get('Account Name')}: "
                f"{e}"
            )

    write_to_sheet(
        config.SHEET_RESEARCH_CACHE,
        results
    )

    logger.info(
        f"Research Cache updated with "
        f"{len(results)} rows"
    )


if __name__ == "__main__":
    run()