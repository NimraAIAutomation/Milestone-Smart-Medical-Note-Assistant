# Smart Medical Note Assistant

A Streamlit application that uses a Groq-hosted language model to
collect patient-reported information conversationally and organize it
into a structured medical-note draft.

> **Safety notice:** This project is for learning and demonstration with
> synthetic data. It is not a diagnostic tool and must not replace
> clinical judgment. Generated notes require review by a qualified
> healthcare professional. Do not enter identifiable or confidential
> patient information.

## Features

-   Conversational interface that asks one question at a time.
-   Collects patient-reported symptoms and relevant history.
-   Generates a structured clinical-note draft on request.
-   Organizes the output into fields:
    -   Chief complaint
    -   Symptoms
    -   Vital signs
    -   Medical history
    -   Medications
    -   Allergies
    -   Missing information
-   Parses and validates the model's JSON response.
-   Displays the note in the Streamlit interface.
-   Downloads the structured note as a JSON file.
-   Starts a new patient session and clears the prior conversation and
    generated note.
-   Handles API failures with user-friendly error messages.
-   Loads the Groq API key from an environment variable.

## Technology

-   Python
-   Streamlit
-   Groq Python SDK
-   python-dotenv
-   JSON and Python logging

## Project structure

``` text
smart_medical_note_assistant/
├── app.py
├── llm_service.py
├── .env                 # Local secret
├── .gitignore
├── requirements.txt
└── README.md
```
## Setup

### 1. Create and activate a virtual environment

Windows PowerShell:

``` powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If you use Command Prompt instead:

``` bat
venv\Scripts\activate
```

### 2. Install dependencies

``` bash
pip install -r requirements.txt
```

### 3. Configure the API key

Create a `.env` file in the project root:

``` text
GROQ_API_KEY=your_groq_api_key_here
```

Replace the placeholder with your own key. Never share the key or commit
`.env` to GitHub.

### 4. Run the app

``` bash
streamlit run app.py
```

Streamlit will print a local URL in the terminal. Open that URL in your
browser.

## How to use

1.  Start the app and enter synthetic patient information in the chat.
2.  Answer the assistant's questions as appropriate.
3.  Select **Generate Medical Note** to create a structured draft.
4.  Review the fields and the missing-information list.
5.  Use the JSON download option to save the draft.
6.  Select **Start New Patient** before beginning another test session.

## Error handling

The app catches failures during API calls and note generation.
Connection errors are presented with a more specific message; other
failures receive a general message. The JSON generation function checks
that the response can be parsed and that required fields and basic data
types are present.

These checks validate the output's structure, not the truth or clinical
accuracy of the content. Always review the note manually.

## Safety and limitations

-   The assistant documents information; it should not diagnose
    conditions or prescribe treatment.
-   Model-generated summaries can omit, misinterpret, or fabricate
    information despite prompt instructions and validation.
-   Missing values should remain marked as not provided rather than
    guessed.
-   A red-flag symptom may require urgent medical assessment; users
    should not delay care to finish the chat.
-   The app's JSON checks do not establish clinical correctness,
    completeness, or regulatory compliance.
-   Use synthetic data for demos and testing. Do not submit real patient
    identifiers or protected health information to an external API
    unless you have appropriate authorization, safeguards, and
    compliance review.
-   This educational project is not a certified medical device or an
    electronic health record system.

## Suggested test cases

-   A simple symptom report with some missing vital signs.
-   A note containing several symptoms and relevant medical history.
-   A conversation with no user-provided patient information.
-   A simulated internet/API connection failure.
-   Generating a second patient session after clicking **Start New
    Patient**.
-   Checking that the downloaded file is valid JSON and includes the
    expected fields.

## Future improvements

-   Add automated unit tests for JSON parsing and validation.
-   Validate every field's type and handle unexpected extra or missing
    keys consistently.
-   Add retry logic only for transient failures, with a bounded retry
    count.
-   Add explicit tests for urgent-symptom safety behavior.
-   Provide a clinician review/edit step before exporting the note.
-   Add secure audit logging that never stores API keys or unnecessary
    patient details.

