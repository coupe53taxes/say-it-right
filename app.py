# Enhanced Interactive Streamlit App for Conversation Mediation

import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Say It Right", page_icon="✉️")
st.title("Say It Right")
st.caption("Navigate difficult conversations with clarity, empathy, and insight.")

# Store conversation context
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Function to interact with OpenAI API
def call_gpt(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error from OpenAI API: {e}"

# Function to generate structured response
def generate_structured_response(conversation):
    prompt_messages = [
        {"role": "system", "content": "You are a calm, insightful mediator skilled at reducing tensions and clarifying disagreements."}
    ]
    prompt_messages += conversation

    structured_prompt = (
        "Given this conversation, perform the following tasks clearly separated by headers:\n"
        "1. **Steelman Each Perspective**: Restate each person's viewpoint in its strongest, most reasonable form.\n"
        "2. **Clarify Real Disagreement**: Identify the core issue or value underlying the disagreement.\n"
        "3. **Constructive Next Message**: Suggest a calm, respectful, and clear message for the next step in the conversation."
    )

    prompt_messages.append({"role": "user", "content": structured_prompt})

    return call_gpt(prompt_messages)

# User input area
st.subheader("Describe the Conversation")
user_message = st.text_area("Describe what's happening in the conversation or paste your last message here:", height=150)

if st.button("Get Insight"):
    if user_message:
        st.session_state.conversation_history.append({"role": "user", "content": user_message})

        with st.spinner("Analyzing conversation..."):
            structured_response = generate_structured_response(st.session_state.conversation_history)

        st.subheader("🧠 Insight and Guidance")
        st.markdown(structured_response)

        # Option to copy/share suggested response
        suggested_message_start = structured_response.find("**Constructive Next Message**")
        if suggested_message_start != -1:
            suggested_message = structured_response[suggested_message_start:].split("\n", 1)[1].strip()

            st.text_area("Suggested Message to Send:", value=suggested_message, height=100)

            st.write("Copy and paste the above message into your preferred messaging app or email.")

            st.markdown("---")
            st.info("This app respects your privacy by not sending messages directly. You control what gets shared.")

            st.markdown("### 📤 Easy Share")
            st.write("Use the buttons below to quickly share this suggestion:")
            email_body = suggested_message.replace(" ", "%20").replace("\n", "%0A")
            sms_body = suggested_message.replace(" ", "%20").replace("\n", "%0A")

            st.markdown(f"[✉️ Email](mailto:?subject=Conversation%20Suggestion&body={email_body})")
            st.markdown(f"[📱 SMS](sms:?body={sms_body})")
    else:
        st.warning("Please enter some details about the conversation before continuing.")

# Button to reset conversation history
if st.button("Start New Conversation"):
    st.session_state.conversation_history = []
    st.success("Conversation context reset.")
