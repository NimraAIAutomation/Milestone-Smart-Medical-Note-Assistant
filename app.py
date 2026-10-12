import streamlit as st
from llm_service import (
    get_assistant_response,
    generate_medical_note
)
import json

#Page configuration
st.set_page_config(
    page_title="Smart Medical Note Assistant",
    layout="centered"
)
#Sidebar content
if st.sidebar.button("Start New Patient"):
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I can help document your symptoms "
                "and relevant medical information. "
                "What is your main concern today?"
            )
        }
    ]

    st.session_state.pop("medical_note_data", None)
    st.rerun()

st.sidebar.warning(
    "Use synthetic patient data for testing. "
    "Do not enter identifiable patient information. "
    "Generated notes require professional review."
)

st.title("Smart Medical Note Assistant")
st.caption(
    "A conversational assistant for collecting and organizing "
    "patient-reported health information."
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I can help organize your health information "
                "into a structured medical note. "
                "What symptoms would you like to record today?"
            )
        }
    ]

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
user_input = st.chat_input("Describe your symptoms...")


if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Preparing your response..."):
            try:
                reply = get_assistant_response(
                    st.session_state.messages
                )

                st.markdown(reply)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": reply
                    }
                )

            except Exception as e:
                st.error("Failed to generate a response.")
                st.exception(e)

#Clinical Note Generation Section
#st.caption(
#    "Review the conversation before generating a draft. "
#    "The draft must be checked by a qualified healthcare professional."
#)
st.divider()
st.subheader("Clinical Note")

if st.button("Generate Medical Note", type="primary"):

    if not any(
        message["role"] == "user"
        for message in st.session_state.messages
    ):
        st.warning("Please enter patient information first.")

    else:
        with st.spinner("Generating structured medical note..."):
            try:
                note_data = generate_medical_note(
                    st.session_state.messages
                )
                # Verify that the JSON can be parsed
                json_text = json.dumps(note_data, indent=4)
                json.loads(json_text)  # Verify that the JSON can be parsed

                st.session_state["medical_note_data"] = note_data
            
            except Exception as e:
                error_name = type(e).__name__

                if error_name == "APIConnectionError":
                    st.error(
                        "Connection failed. Check your internet "
                        "connection and try again."
                    )
                else:
                    st.error(
                        "Unable to generate the medical note. "
                        "Please try again."
                    )

                st.caption(f"Error type: {error_name}")

#Session State
if st.session_state.get("medical_note_data"):

    note = st.session_state["medical_note_data"]

    st.subheader("Clinical Summary")

    st.markdown("### Chief Complaint")
    st.write(note["chief_complaint"])

    st.markdown("### Symptoms")
    for symptom in note["symptoms"]:
        st.markdown(f"- {symptom}")

    st.markdown("### Vital Signs")
    for vital, value in note["vital_signs"].items():
        label = vital.replace("_", " ").title()
        st.markdown(f"- **{label}:** {value}")

    st.markdown("### Medical History")
    st.write(note["medical_history"])

    st.markdown("### Medications")
    st.write(note["medications"])

    st.markdown("### Allergies")
    st.write(note["allergies"])

    st.markdown("### Missing Information")
    if note["missing_information"]:
        for item in note["missing_information"]:
            st.markdown(f"- {item}")
    else:
        st.write("No missing information was identified.")

    st.download_button(
        label="Download Medical Note (JSON)",
        data=json.dumps(note, indent=4),
        file_name="medical_note.json",
        mime="application/json"
    )

