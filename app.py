# Interactive Streamlit App: Context-Aware Communication Assistant
import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Session State Initialization
if "stage" not in st.session_state:
    st.session_state.stage = "goal_select"
if "fight_stage" not in st.session_state:
    st.session_state.fight_stage = None
if "fight_history" not in st.session_state:
    st.session_state.fight_history = []
if "current_user" not in st.session_state:
    st.session_state.current_user = "A"
if "user_A_name" not in st.session_state:
    st.session_state.user_A_name = "User A"
if "user_B_name" not in st.session_state:
    st.session_state.user_B_name = "User B"

st.set_page_config(page_title="Say It Right", page_icon="✉️")
st.title("Say It Right")
st.caption("Diffuse conflict. Preserve truth. Protect what matters.")

# Main App Logic
if st.session_state.stage == "pass_to_first_user":
    st.header("Pass to First Debater")
    st.markdown("Pass the device to **User A**. Click below when ready.")
    if st.button(f"I'm {st.session_state.user_A_name}, Continue"):
        st.session_state.stage = "first_user_private"
        st.rerun()

# Placeholder for the rest of the app logic...
# You should add your additional stages and flows below as needed.
