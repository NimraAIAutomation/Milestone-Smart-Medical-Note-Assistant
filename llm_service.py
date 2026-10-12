import os
import logging
from dotenv import load_dotenv
from groq import Groq
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Load API configuration
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY is missing. Check your .env file."
    )

client = Groq(api_key=api_key, timeout=30)

MODEL_NAME = "qwen/qwen3.8-27b"



SYSTEM_PROMPT = """
You are a friendly, professional medical note-taking assistant.
Your job is to collect and organize information, not diagnose
conditions or prescribe treatment.

CONVERSATION STYLE:
- Ask exactly ONE clear question per response.
- Keep responses brief, natural, and conversational.
- Avoid repetitive phrases such as "Thank you for sharing that"
  or "To help me understand better".
- Acknowledge the user's answer briefly only when useful.
- Ask the next most relevant question based on the information
  already provided.
- Never ask the user to repeat information already given.
- Avoid long lists of possible symptoms.
- Use simple language that is easy to understand.
- Do not sound like a questionnaire or repeatedly explain your role.

INFORMATION COLLECTION:
- Main concern and symptom onset
- Location, severity, duration, and pattern
- Relevant associated symptoms
- Relevant medical history
- Current medications and allergies
- Relevant vital signs, one at a time
- Record missing information as "Not provided".
- Never invent measurements, symptoms, or medical history.

SAFETY:
- If the user reports a potentially serious combination of symptoms,
  prioritize appropriate urgent medical guidance over routine
  information gathering.
- A severe headache with new vision changes may require emergency
  assessment. Advise the user to seek urgent medical care now,
  especially if symptoms are sudden, worsening, or accompanied
  by weakness, confusion, or difficulty speaking.
- Do not delay urgent care to complete the conversation.
- Do not diagnose the user.

MEDICAL NOTE GENERATION:
- Generate a note only when the user requests or agrees to it.
- Use concise bullet points under clear headings.
- Include only information provided in the conversation.
- Separate patient-reported information from measured vital signs.
- Mark missing information as "Not provided".
- Do not invent diagnoses, findings, or treatment plans.

Always follow these rules while responding to the conversation.
"""


def get_assistant_response(messages):
    """
    Send conversation messages to the LLM
    and return the assistant's text response.
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system","content": SYSTEM_PROMPT},
                *messages
            ],
            temperature=0.2,
            max_completion_tokens=300,
            reasoning_effort="none",
            timeout=30
        )

        if not response.choices:
            raise ValueError("The API returned no choices.")

        content = response.choices[0].message.content

        if not content or not content.strip():
            raise ValueError("The API returned an empty response.")

        logger.info("LLM response received successfully.")

        return content.strip()

    except Exception:
        logger.exception("Failed to generate assistant response.")
        raise

# Generate and validate a structured medical note
def generate_medical_note(messages):
    """
    Generate and validate a structured medical note.
    """

    note_prompt = """
    Create a structured medical note from the conversation below.

    Return ONLY a valid JSON object with these exact fields:
    {
        "chief_complaint": "string",
        "symptoms": ["string"],
        "vital_signs": {
            "blood_pressure": "string",
            "heart_rate": "string",
            "temperature": "string",
            "blood_glucose": "string"
        },
        "medical_history": "string",
        "medications": "string",
        "allergies": "string",
        "missing_information": ["string"]
    }

    Rules:
    - Use only information explicitly provided in the conversation.
    - Never invent symptoms, measurements, or medical history.
    - Use "Not provided" for missing values.
    - Include only reported symptoms in the symptoms list.
    - Do not diagnose or recommend treatment.
    - Include missing vital signs in missing_information.
    - Return JSON only, without Markdown code fences.
    """

    note_messages = [
        {"role": "system", "content": note_prompt},
        *messages,
        {
            "role": "user",
            "content": "Generate the structured medical note now."
        }
    ]

    raw_response = get_assistant_response(note_messages)

    try:
        note_data = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        logger.exception("The model returned invalid JSON.")
        raise ValueError(
            "The model returned invalid JSON. Please try again."
        ) from exc

    required_fields = {
        "chief_complaint",
        "symptoms",
        "vital_signs",
        "medical_history",
        "medications",
        "allergies",
        "missing_information"
    }

    if not isinstance(note_data, dict):
        raise ValueError("The medical note must be a JSON object.")

    if not required_fields.issubset(note_data.keys()):
        raise ValueError("The medical note is missing required fields.")

    if not isinstance(note_data["symptoms"], list):
        raise ValueError("'symptoms' must be a list.")

    if not isinstance(note_data["missing_information"], list):
        raise ValueError("'missing_information' must be a list.")

    vital_fields = {
        "blood_pressure",
        "heart_rate",
        "temperature",
        "blood_glucose"
    }

    vitals = note_data["vital_signs"]

    if not isinstance(vitals, dict) or not vital_fields.issubset(vitals.keys()):
        raise ValueError("The vital_signs object is incomplete.")

    logger.info("Structured medical note validated successfully.")

    for field in required_fields:
        if not isinstance(note_data[field], (str, list, dict)):
            raise ValueError(
                f"Invalid data type for field: {field}"
            )
        
    return note_data
