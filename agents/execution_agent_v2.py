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


def generate_campaign(review):

    review_id = review.get("Review ID", "")
    draft_id = review.get("Draft ID", "")
    review_status = review.get("Review Status", "")
    quality_score = review.get("Quality Score", "")

    logger.info(f"Executing campaign for {draft_id}")

    prompt = f"""
You are a campaign execution analyst.

Review Status:
{review_status}

Quality Score:
{quality_score}

Return ONLY valid JSON.

{{
    "campaign_status":"",
    "engagement_score":"",
    "response_rate":"",
    "opportunity_status":"",
    "next_action":""
}}

Rules:
- campaign_status must be Sent
- engagement_score between 70 and 100
- response_rate between 5% and 25%
- opportunity_status must be one of:
  In Discussion,
  Qualified Lead,
  Follow-up Scheduled
- next_action must be one of:
  Follow-up Call,
  Product Demo,
  Discovery Meeting

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
        temperature=0.4,
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
            "campaign_status": "Sent",
            "engagement_score": "85",
            "response_rate": "12%",
            "opportunity_status": "In Discussion",
            "next_action": "Follow-up Call"
        }

    campaign_number = draft_id.split("-")[1]

    launch_date = datetime.today().strftime("%d/%m/%Y")

    account_id = f"ACC-{campaign_number}"

    campaign_names = {
        "001": "Pratt & Whitney PLM Modernization Outreach",
        "002": "Lockheed Martin Digital Engineering Outreach",
        "003": "Parker Aerospace Manufacturing Digitalization Outreach"
    }

    audiences = {
        "001": "PLM Owner",
        "002": "IT Leader",
        "003": "IT Leader"
    }

    return {
        "Campaign ID": f"CMP-{campaign_number}",
        "Account ID": account_id,
        "Draft ID": draft_id,
        "Campaign Name": campaign_names.get(
            campaign_number,
            "Industry Outreach Campaign"
        ),
        "Campaign Type": "Email Campaign",
        "Launch Date": launch_date,
        "Campaign Status": data.get(
            "campaign_status",
            "Sent"
        ),
        "Target Audience": audiences.get(
            campaign_number,
            "Decision Maker"
        ),
        "Channel": "Email",
        "Engagement Score": data.get(
            "engagement_score",
            "85"
        ),
        "Response Rate": data.get(
            "response_rate",
            "12%"
        ),
        "Opportunity Status": data.get(
            "opportunity_status",
            "In Discussion"
        ),
        "Next Action": data.get(
            "next_action",
            "Follow-up Call"
        )
    }


def run():

    logger.info("Starting Execution Agent V2")

    reviews = read_sheet(
        config.SHEET_REVIEW_QUEUE
    )

    if not reviews:

        logger.warning(
            "No review records found"
        )
        return

    results = []

    for review in reviews:

        try:

            if review.get(
                "Review Status",
                ""
            ) != "Approved":

                continue

            result = generate_campaign(
                review
            )

            results.append(result)

            logger.info(
                f"Campaign created for "
                f"{review.get('Draft ID')}"
            )

        except Exception as e:

            logger.error(
                f"Error processing "
                f"{review.get('Draft ID')}: {e}"
            )

    write_to_sheet(
        config.SHEET_CAMPAIGN_TRACKER,
        results
    )

    logger.info(
        f"Campaign Tracker updated with "
        f"{len(results)} rows"
    )


if __name__ == "__main__":
    run()