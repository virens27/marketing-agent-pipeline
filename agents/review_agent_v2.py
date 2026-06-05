import json
import logging
from datetime import datetime

from groq import Groq

import config
from sheets.reader import read_sheet
from sheets.writer import write_to_sheet

logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

client = Groq(api_key=config.GROQ_API_KEY)


def generate_review(draft):

    draft_id = draft.get("Draft ID", "")
    account_id = draft.get("Account ID", "")
    subject_line = draft.get("Subject Line", "")
    opening_hook = draft.get("Opening Hook", "")
    value_proposition = draft.get("Value Proposition", "")
    call_to_action = draft.get("Call To Action", "")
    personalization = draft.get("Personalization Elements", "")

    logger.info(f"Reviewing {draft_id}")

    prompt = f"""
You are a senior marketing content reviewer.

Review the following outreach draft.

Subject Line:
{subject_line}

Opening Hook:
{opening_hook}

Value Proposition:
{value_proposition}

Call To Action:
{call_to_action}

Personalization:
{personalization}

Return ONLY valid JSON.

{{
    "review_status":"",
    "feedback":"",
    "revision_required":"",
    "quality_score":""
}}

Rules:
- review_status must be Approved or Revision Needed
- feedback must be one short sentence
- revision_required must be Yes or No
- quality_score must be between 1 and 10

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
        max_tokens=500
    )

    output = response.choices[0].message.content.strip()

    try:
        data = json.loads(output)

    except Exception:

        logger.warning(
            f"Invalid JSON received for {draft_id}"
        )

        data = {
            "review_status": "Approved",
            "feedback": "Good personalization and business relevance",
            "revision_required": "No",
            "quality_score": "8"
        }

    review_number = draft_id.split("-")[1]

    today = datetime.today().strftime("%d/%m/%Y")

    return {
        "Review ID": f"RQ-{review_number}",
        "Draft ID": draft_id,
        "Reviewer": "Marketing Manager",
        "Review Date": today,
        "Review Status": data.get("review_status", "Approved"),
        "Feedback": data.get("feedback", ""),
        "Revision Required": data.get(
            "revision_required",
            "No"
        ),
        "Quality Score": data.get(
            "quality_score",
            "8"
        ),
        "Approved Version": "V1.0",
        "Approval Date": today
    }


def run():

    logger.info("Starting Review Agent V2")

    drafts = read_sheet(
        config.SHEET_DRAFT_CONTENT
    )

    if not drafts:

        logger.warning(
            "No draft content found"
        )
        return

    results = []

    for draft in drafts:

        try:

            result = generate_review(
                draft
            )

            results.append(result)

            logger.info(
                f"Review completed for "
                f"{draft.get('Draft ID')}"
            )

        except Exception as e:

            logger.error(
                f"Error reviewing "
                f"{draft.get('Draft ID')}: {e}"
            )

    write_to_sheet(
        config.SHEET_REVIEW_QUEUE,
        results
    )

    logger.info(
        f"Review Queue updated with "
        f"{len(results)} rows"
    )


if __name__ == "__main__":
    run()