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

# Goal selection entry point
if st.session_state.stage == "goal_select":
    st.subheader("What best describes your situation?")
    cols1 = st.columns(2)

    if cols1[0].button("🥊 Fight Productively"):
        st.session_state.stage = "debate_setup"
        st.rerun()

# Debate setup
if st.session_state.stage == "debate_setup":
    st.subheader("Set up your debate")
    st.session_state.debate_topic = st.text_input("Debate topic:", st.session_state.get("debate_topic", ""))
    st.session_state.user_A_name = st.text_input("Name of User A:", st.session_state.user_A_name)
    st.session_state.user_A_position = st.text_input(f"{st.session_state.user_A_name}'s position:", st.session_state.get("user_A_position", ""))
    st.session_state.user_B_name = st.text_input("Name of User B:", st.session_state.user_B_name)
    st.session_state.user_B_position = st.text_input(f"{st.session_state.user_B_name}'s position:", st.session_state.get("user_B_position", ""))

    if st.button("Continue to Proposition"):
        st.session_state.stage = "proposition_edit"
        st.rerun()

# Proposition editing
if st.session_state.stage == "proposition_edit":
    st.subheader("🧭 Let's clarify the disagreement")
    summary = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Draft a clear, debate-ready proposition that fairly represents opposing views."},
            {"role": "user", "content": f"Topic: {st.session_state.debate_topic}\n\nUser A position: {st.session_state.user_A_position}\n\nUser B position: {st.session_state.user_B_position}"}
        ]
    ).choices[0].message.content.strip()

    st.session_state.debate_prop = st.text_area("Debate Proposition:", summary)

    if st.button("Pass to First Debater"):
        st.session_state.stage = "handoff_A"
        st.rerun()

# Handoff to User A
if st.session_state.stage == "handoff_A":
    st.header("Pass to First Debater")
    st.markdown("Pass the device to **User A**. Click below when ready.")
    if st.button(f"I'm {st.session_state.user_A_name}, Continue"):
        st.session_state.stage = "user_A_input"
        st.rerun()

# Additional functionality to be added... (user_A_input, feedback, response editing, etc.)
