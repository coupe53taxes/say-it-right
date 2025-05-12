# Interactive Streamlit App: Context-Aware Communication Assistant

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
st.caption("Diffuse conflict. Preserve truth. Protect what matters.")

# Set up session state
if "stage" not in st.session_state:
    st.session_state.stage = "goal_select"
if "fight_stage" not in st.session_state:
    st.session_state.fight_stage = None
if "fight_history" not in st.session_state:
    st.session_state.fight_history = []
if "current_user" not in st.session_state:
    st.session_state.current_user = "A"

# GPT call helper
def call_gpt(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# Icon Grid (Initial page)
if st.session_state.stage == "goal_select":
    st.subheader("What best describes your situation?")
    st.markdown("Pick the one that fits best, and I’ll guide you from there.")

    cols1 = st.columns(2)
    cols2 = st.columns(2)
    cols3 = st.columns(2)

    if cols1[0].button("
