# Full Integrated Streamlit Debate Moderator App (With Context Retention, Clean Feedback Box, and Custom End Recap)

import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Say It Right", page_icon="✉️")

# Session State Initialization
def initialize_state():
    keys_defaults = {
        "stage": "goal_select",
        "fight_history": [],
        "debate_prop": "",
        "user_A_name": "User A",
        "user_B_name": "User B",
        "user_A_position": "",
        "user_B_position": "",
        "current_user": "A",
        "temp_feedback": "",
        "temp_input": "",
        "summary_mode": False
    }
    for key, value in keys_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_state()

# GPT Helper

def call_gpt(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Error calling GPT: {e}]"

# Goal Selection Grid
if st.session_state.stage == "goal_select":
    st.title("Say It Right")
    st.caption("Diffuse conflict. Preserve truth. Protect what matters.")
    st.subheader("Choose your situation:")

    cols = st.columns(2)
    if cols[0].button("
