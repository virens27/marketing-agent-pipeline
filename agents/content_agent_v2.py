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

client = Groq(
    api_key=config.GROQ_API_KEY
)


def get_contact_for_persona(
    account_id,
    stakeholder_persona,
    contacts
):
    """
    Maps challenge persona to contact.
    """

    if stakeholder_persona == "PLM Owner":
        target_title = "PLM Manager"

    elif stakeholder_persona == "IT Leader":
        target_title = "Director IT"

    else:
        target_title = "VP Engineering"

    for contact in contacts:

        if (
            contact.get("Account ID") == account_id
            and contact.get("Title") == target_title
        ):
            return contact

    return None


def generate_content(
    challenge,
    account,
    contact,
    draft_number
):

    company_name = account.get(
        "Account Name",
        ""
    )

    challenge_category = challenge.get(
        "Challenge Category",
        ""
    )

    challenge_description = challenge.get(
        "Challenge Description",
        ""
    )

    business_impact = challenge.get(
        "Business Impact",
        ""
    )

    solution = challenge.get(
        "Recommended Solution",
        ""
    )

    contact_title = contact.get(
        "Title",
        ""
    )

    prompt = f"""
You are a B2B Account Based Marketing expert.

Generate ONLY valid JSON.

Company:
{company_name}

Contact Title:
{contact_title}

Challenge:
{challenge_description}

Business Impact:
{business_impact}

Recommended Solution:
{solution}

Return JSON:

{{
    "subject_line":"",
    "opening_hook":"",
    "value_proposition":"",
    "call_to_action":"",
    "personalization_elements":"",
    "quality_score":""
}}

Rules:

- Subject line under 10 words.
- Opening hook 2 sentences.
- Value proposition 2 sentences.
- CTA 1 sentence.
- Personalization elements comma separated.
- Quality score between 1 and 10.

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
        max_tokens=800
    )

    output = response.choices[0].message.content

    try:
        data = json.loads(output)

    except Exception:

        logger.warning(
            "JSON parsing failed. Using fallback."
        )

        data = {
            "subject_line":
                f"Improving {challenge_category} at {company_name}",
            "opening_hook":
                challenge_description,
            "value_proposition":
                solution,
            "call_to_action":
                "Would you be open to a short discussion?",
            "personalization_elements":
                company_name,
            "quality_score":
                8
        }

    return {
        "Draft ID":
            f"DR-{draft_number:03}",

        "Account ID":
            account.get("Account ID"),

        "Contact ID":
            contact.get("Contact ID"),

        "Challenge ID":
            challenge.get("Challenge ID"),

        "Content Type":
            "Email",

        "Subject Line":
            data.get("subject_line", ""),

        "Opening Hook":
            data.get("opening_hook", ""),

        "Value Proposition":
            data.get("value_proposition", ""),

        "Call To Action":
            data.get("call_to_action", ""),

        "Personalization Elements":
            data.get(
                "personalization_elements",
                ""
            ),

        "Draft Status":
            "Draft",

        "Quality Score":
            data.get(
                "quality_score",
                8
            ),

        "Approval Status":
            "Pending Review"
    }


def run():

    logger.info(
        "Starting Content Agent V2"
    )

    accounts = read_sheet(
        config.SHEET_ACCOUNTS
    )

    contacts = read_sheet(
        config.SHEET_CONTACTS
    )

    challenges = read_sheet(
        config.SHEET_CHALLENGE_MAP
    )

    account_lookup = {
        row["Account ID"]: row
        for row in accounts
    }

    results = []

    draft_counter = 1

    for challenge in challenges:

        try:

            account_id = challenge.get(
                "Account ID"
            )

            stakeholder_persona = challenge.get(
                "Stakeholder Persona",
                ""
            )

            account = account_lookup.get(
                account_id
            )

            if not account:
                continue

            contact = get_contact_for_persona(
                account_id,
                stakeholder_persona,
                contacts
            )

            if not contact:
                logger.warning(
                    f"No contact found for {account_id}"
                )
                continue

            result = generate_content(
                challenge,
                account,
                contact,
                draft_counter
            )

            results.append(result)

            logger.info(
                f"Draft created for {account_id}"
            )

            draft_counter += 1

        except Exception as e:

            logger.error(
                f"Error processing challenge: {e}"
            )

    write_to_sheet(
        config.SHEET_DRAFT_CONTENT,
        results
    )

    logger.info(
        f"Draft Content updated with {len(results)} rows"
    )


if __name__ == "__main__":
    run()