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

# Session state for storing conversation and flow control
if "dialogue" not in st.session_state:
    st.session_state.dialogue = []
if "stage" not in st.session_state:
    st.session_state.stage = "goal_select"
    st.session_state.stage = "goal_select"
    st.session_state.stage = "initial_input"
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

# Analyze user's situation input

def classify_situation(user_input):
    if "user_goal" not in st.session_state:
        st.session_state.stage = "goal_select"
        st.rerun()

    user_goal = st.session_state.user_goal
    convo_description = f"""User goal: {user_goal}

User input: {user_input}

Please respond with:
Situation: [brief summary of what’s going on]
Ongoing conversation: [Yes/No]
User style: [short phrase]"""

    prompt = [
        {
            "role": "system",
            "content": (
                "You are a conversation strategist. The user will describe a communication challenge."
                " Based on what they write and their stated goal, analyze the context and infer their communication style."
            )
        },
        {
            "role": "user",
            "content": convo_description
        }
    ]
    return call_gpt(prompt)

# Generate rewrite using learned communication style

def generate_rewrite(dialogue):
    rewrite_prompt = [
        {"role": "system", "content": (
            f"You are a communication assistant that rewrites emotionally intense or unclear messages into tactful, truthful, and constructive ones.\n"
            f"Preserve the user's core intent and match their natural communication style: {st.session_state.user_style}.\n"
            "Soften exaggerations or insults. Clarify any factual claims gently."
        )},
        *dialogue,
        {"role": "user", "content": "Rewrite my last message in a tactful, emotionally constructive way."}
    ]
    return call_gpt(rewrite_prompt)

# Initial context-free prompt
if st.session_state.stage == "goal_select":
    # Prompt user with intuitive button grid before asking for context
    st.subheader("What best describes your situation?")
    st.markdown("Pick the one that fits best, and I’ll guide you from there.")

    cols1 = st.columns(2)
    cols2 = st.columns(2)
    cols3 = st.columns(2)

    if cols1[0].button("🫱 I want to explain myself clearly"):
        st.session_state.user_goal = "Be understood"
        st.session_state.stage = "initial_input"
        st.rerun()

    if cols1[1].button("🧯 I want to cool things down before it gets worse"):
        st.session_state.user_goal = "Defuse the situation"
        st.session_state.stage = "initial_input"
        st.rerun()

    if cols2[0].button("🤝 I want to get through to them without causing a fight"):
        st.session_state.user_goal = "Persuade without escalation"
        st.session_state.stage = "initial_input"
        st.rerun()

    if cols2[1].button("⚖️ We both think we're right"):
        st.session_state.user_goal = "Mutual conviction"
        st.session_state.stage = "initial_input"
        st.rerun()

    if cols3[0].button("📣 Media has me heated"):
        st.session_state.user_goal = "Reacting to content"
        st.session_state.stage = "initial_input"
        st.rerun()

    if cols3[1].button("🧘 I just need to vent and reflect"):
        st.session_state.user_goal = "Venting"
        st.session_state.stage = "initial_input"
        st.rerun()

elif st.session_state.stage == "initial_input":
    st.subheader("🧭 What’s going on?")
    user_input = st.text_area("Briefly describe the situation, what's been said (if anything), and what you’re hoping to achieve.")
    if st.button("Analyze My Situation"):
        st.session_state.dialogue.append({"role": "user", "content": user_input})
        classification = classify_situation(user_input)
        st.session_state.situation_type = classification.split("\n")[0]
        st.session_state.user_style = classification.split("\n")[-1]
        st.session_state.stage = "user_reply"
        st.rerun()

# Display feedback and let user respond
elif st.session_state.stage == "user_reply":
    st.subheader("Step 2: What do you want to say next?")
    st.markdown(f"**Detected Situation:** {st.session_state.situation_type.replace('Situation: ', '')}")
    st.markdown(f"**Your Communication Style:** {st.session_state.user_style.replace('User style: ', '')}")

    reply = st.text_area("Draft your next message or response:")
    if st.button("Polish My Message"):
        st.session_state.dialogue.append({"role": "user", "content": f"User’s planned message: {reply}"})
        st.session_state.stage = "rewrite"
        st.rerun()

# Rewrite based on inferred style
elif st.session_state.stage == "rewrite":
    st.subheader("✍️ A refined version of your message")

    if "rewrite_response" not in st.session_state:
        with st.spinner("Rewriting for clarity, fairness, and impact..."):
            rewrite = generate_rewrite(st.session_state.dialogue)
        st.session_state.rewrite_response = rewrite

    st.markdown("#### Here's a calmer, clearer version you might send:")
    st.text_area("Polished Reply:", value=st.session_state.rewrite_response, height=120)

    email_body = st.session_state.rewrite_response.replace(" ", "%20").replace("\n", "%0A")
    sms_body = st.session_state.rewrite_response.replace(" ", "%20").replace("\n", "%0A")

    st.markdown(f"[✉️ Email](mailto:?subject=Suggested%20Response&body={email_body})")
    st.markdown(f"[📱 SMS](sms:?body={sms_body})")

    if st.button("🔁 Start Over"):
        st.session_state.dialogue = []
        st.session_state.stage = "initial_input"
        st.session_state.user_style = ""
        st.session_state.situation_type = ""
        st.rerun()
