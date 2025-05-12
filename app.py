# Final cleaned and debugged app.py with f-string and block errors fixed.
# Only one copy of each section retained. All bad f-string formatting and indentation bugs resolved.

import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Say It Right", page_icon="\u2709\ufe0f")
st.title("Say It Right")
st.caption("Diffuse conflict. Preserve truth. Protect what matters.")

# Initialize session state
if "stage" not in st.session_state or st.session_state.stage == "initial_input":
    st.session_state.stage = "goal_select"
    st.session_state.fight_stage = None
    st.session_state.fight_history = []
    st.session_state.current_user = "A"

if "dialogue" not in st.session_state:
    st.session_state.dialogue = []
if "show_map" not in st.session_state:
    st.session_state.show_map = False
if "situation_type" not in st.session_state:
    st.session_state.situation_type = ""
if "user_style" not in st.session_state:
    st.session_state.user_style = ""

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

# Classifier function
def classify_situation(user_input):
    user_goal = st.session_state.user_goal
    convo_description = f"""User goal: {user_goal}\n\nUser input: {user_input}\n\nPlease respond with:\nSituation: [brief summary]\nOngoing conversation: [Yes/No]\nUser style: [short phrase]"""

    prompt = [
        {"role": "system", "content": "You are a conversation strategist."},
        {"role": "user", "content": convo_description}
    ]
    return call_gpt(prompt)

# Rewrite with style awareness
def generate_rewrite(dialogue):
    rewrite_prompt = [
        {"role": "system", "content": (
            f"You are a communication assistant that rewrites intense messages into tactful ones.\n"
            f"Preserve intent and match the user style: {st.session_state.user_style}.\n"
            "Clarify factual claims and soften exaggerations."
        )},
        *dialogue,
        {"role": "user", "content": "Rewrite my last message in a tactful, constructive way."}
    ]
    return call_gpt(rewrite_prompt)

# Goal Selection Grid
if st.session_state.stage == "goal_select":
    st.subheader("What best describes your situation?")
    cols1, cols2, cols3 = st.columns(2), st.columns(2), st.columns(2)

    if cols1[0].button("\udad1 I want to explain myself clearly"):
        st.session_state.user_goal = "Be understood"
        st.session_state.stage = "context_input"
        st.rerun()
    if cols1[1].button("\ud83e\udeef I want to cool things down before it gets worse"):
        st.session_state.user_goal = "Defuse the situation"
        st.session_state.stage = "context_input"
        st.rerun()
    if cols2[0].button("\ud83e\udd1d I want to get through to them without causing a fight"):
        st.session_state.user_goal = "Persuade without escalation"
        st.session_state.stage = "context_input"
        st.rerun()
    if cols2[1].button("\u2696\ufe0f We both think we're right"):
        st.session_state.user_goal = "Mutual conviction"
        st.session_state.stage = "context_input"
        st.rerun()
    if cols3[0].button("\ud83d\udce3 Media has me heated"):
        st.session_state.user_goal = "Reacting to content"
        st.session_state.stage = "context_input"
        st.rerun()
    if cols3[1].button("\ud83e\uddd8 I just need to vent and reflect"):
        st.session_state.user_goal = "Venting"
        st.session_state.stage = "context_input"
        st.rerun()

# Context Input
elif st.session_state.stage == "context_input":
    st.subheader("\ud83e\udde1 What's going on?")
    user_input = st.text_area("Briefly describe the situation and what you’re hoping to achieve.")
    if st.button("Analyze My Situation"):
        st.session_state.dialogue.append({"role": "user", "content": user_input})
        classification = classify_situation(user_input)
        st.session_state.situation_type = classification.split("\n")[0]
        st.session_state.user_style = classification.split("\n")[-1]
        st.session_state.stage = "user_reply"
        st.rerun()

# User reply entry
elif st.session_state.stage == "user_reply":
    st.subheader("Step 2: What do you want to say next?")
    st.markdown(f"**Detected Situation:** {st.session_state.situation_type.replace('Situation: ', '')}")
    st.markdown(f"**Your Communication Style:** {st.session_state.user_style.replace('User style: ', '')}")

    reply = st.text_area("Draft your next message or response:")
    if st.button("Polish My Message"):
        st.session_state.dialogue.append({"role": "user", "content": f"User’s planned message: {reply}"})
        st.session_state.stage = "rewrite"
        st.rerun()

# Final rewrite
elif st.session_state.stage == "rewrite":
    st.subheader("\u270d\ufe0f A refined version of your message")
    if "rewrite_response" not in st.session_state:
        with st.spinner("Rewriting for clarity, fairness, and impact..."):
            st.session_state.rewrite_response = generate_rewrite(st.session_state.dialogue)

    st.markdown("#### Here's a calmer, clearer version you might send:")
    st.text_area("Polished Reply:", value=st.session_state.rewrite_response, height=120)

    email_body = st.session_state.rewrite_response.replace(" ", "%20").replace("\n", "%0A")
    sms_body = st.session_state.rewrite_response.replace(" ", "%20").replace("\n", "%0A")

    st.markdown(f"[\u2709\ufe0f Email](mailto:?subject=Suggested%20Response&body={email_body})")
    st.markdown(f"[\ud83d\udcf1 SMS](sms:?body={sms_body})")

    if st.button("\ud83d\udd01 Start Over"):
        for key in ["dialogue", "stage", "user_style", "situation_type"]:
            st.session_state[key] = [] if key == "dialogue" else "goal_select" if key == "stage" else ""
        st.rerun()
