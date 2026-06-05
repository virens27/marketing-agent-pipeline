import json
import logging

from groq import Groq

import config
from sheets.reader import read_sheet
from sheets.writer import write_to_sheet

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL)
)

logger = logging.getLogger(__name__)

client = Groq(api_key=config.GROQ_API_KEY)


def generate_challenge(research):

    account_id = research.get("Account ID", "")
    research_id = research.get("Research ID", "")

    research_summary = research.get(
        "Research Summary",
        ""
    )

    key_findings = research.get(
        "Key Findings",
        ""
    )

    logger.info(
        f"Analyzing account {account_id}"
    )

    prompt = f"""
You are a B2B Account Intelligence Analyst.

Research Summary:
{research_summary}

Key Findings:
{key_findings}

Generate ONLY valid JSON.

Format:

{{
  "challenge_category":"",
  "challenge_description":"",
  "impact_level":"",
  "stakeholder_persona":"",
  "business_impact":"",
  "hypothesis_strength":"",
  "recommended_solution":"",
  "priority_score":""
}}

Rules:

- challenge_category should be short.
- impact_level must be High, Medium or Low.
- stakeholder_persona must be relevant buyer.
- hypothesis_strength must be Strong, Medium or Weak.
- priority_score between 1 and 10.

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

    output = response.choices[0].message.content

    try:

        output = output.replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        ).strip()

        data = json.loads(output)

    except Exception:

        logger.warning(
            f"JSON parsing failed for {account_id}"
        )

        data = {
            "challenge_category":
                "Digital Transformation",

            "challenge_description":
                "Need modernization initiative",

            "impact_level":
                "Medium",

            "stakeholder_persona":
                "IT Leader",

            "business_impact":
                "Operational inefficiencies",

            "hypothesis_strength":
                "Medium",

            "recommended_solution":
                "Digital engineering platform",

            "priority_score":
                "7"
        }

    challenge_number = account_id.split("-")[1]

    return {

        "Challenge ID":
            f"CH-{challenge_number}",

        "Account ID":
            account_id,

        "Challenge Category":
            data.get(
                "challenge_category",
                ""
            ),

        "Challenge Description":
            data.get(
                "challenge_description",
                ""
            ),

        "Impact Level":
            data.get(
                "impact_level",
                ""
            ),

        "Evidence Source":
            research_id,

        "Stakeholder Persona":
            data.get(
                "stakeholder_persona",
                ""
            ),

        "Business Impact":
            data.get(
                "business_impact",
                ""
            ),

        "Hypothesis Strength":
            data.get(
                "hypothesis_strength",
                ""
            ),

        "Recommended Solution":
            data.get(
                "recommended_solution",
                ""
            ),

        "Priority Score":
            data.get(
                "priority_score",
                ""
            )
    }


def run():

    logger.info(
        "Starting Analysis Agent V2"
    )

    research_rows = read_sheet(
        config.SHEET_RESEARCH_CACHE
    )

    if not research_rows:

        logger.warning(
            "No research data found"
        )

        return

    results = []

    for research in research_rows:

        try:

            result = generate_challenge(
                research
            )

            results.append(result)

            logger.info(
                f"Challenge created for "
                f"{research.get('Account ID')}"
            )

        except Exception as e:

            logger.error(
                f"Error: {e}"
            )

    write_to_sheet(
        config.SHEET_CHALLENGE_MAP,
        results
    )

    logger.info(
        f"Challenge Map updated "
        f"with {len(results)} rows"
    )


if __name__ == "__main__":
    run()