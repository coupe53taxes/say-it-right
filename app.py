# Interactive Streamlit App: Conversation Mediation & Guidance

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

# Session state for storing conversation
if "dialogue" not in st.session_state:
    st.session_state.dialogue = []

if "stage" not in st.session_state:
    st.session_state.stage = "purpose"

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

# Structured conversation analysis and rewriter
def analyze_turn(dialogue):
    system_prompt = {
        "role": "system",
        "content": (
            "You're an emotionally intelligent AI trained to help people navigate heated or delicate conversations. "
            "You help users:\n"
            "1. Clarify what’s actually being argued\n"
            "2. Steelman the other person's perspective\n"
            "3. Identify emotionally loaded or exaggerated claims in the user's response\n"
            "4. Offer a fact-aware, calm, clear version of their response\n"
            "5. Help them move the conversation forward in good faith"
        )
    }
    return call_gpt([system_prompt] + dialogue)

# Step 1 – Purpose of the conversation
if st.session_state.stage == "purpose":
    st.subheader("Step 1: What's going on?")
    purpose = st.selectbox("Choose the situation you're dealing with:", [
        "A disagreement with an acquaintance in person",
        "A text argument with a friend or loved one",
        "An emotionally charged topic online",
        "Someone misunderstood me and got upset",
        "I lost my temper and want to respond better"
    ])
    if st.button("Next"):
        st.session_state.stage = "context"
        st.session_state.dialogue.append({"role": "user", "content": f"Situation: {purpose}"})
        st.rerun()

# Step 2 – Context of the conversation
elif st.session_state.stage == "context":
    st.subheader("Step 2: What's the disagreement about?")
    context = st.text_area("Describe the situation. What are you trying to say, and how did they respond?")
    if st.button("Analyze the situation"):
        st.session_state.dialogue.append({"role": "user", "content": f"Context: {context}"})
        st.session_state.stage = "analyze"
        st.rerun()

# Step 3 – Analyze the initial setup
elif st.session_state.stage == "analyze":
    st.subheader("🧠 Insight from the situation")
    with st.spinner("Thinking clearly about what matters most..."):
        insight = analyze_turn(st.session_state.dialogue)
    st.markdown(insight)
    st.session_state.stage = "user_reply"
    st.rerun()

# Step 4 – User's intended reply
elif st.session_state.stage == "user_reply":
    st.subheader("Step 4: Your next move")
    reply = st.text_area("What are you planning to say next?")
    if st.button("Polish and optimize my response"):
        st.session_state.dialogue.append({"role": "user", "content": f"User’s planned message: {reply}"})
        st.session_state.stage = "rewrite"
        st.rerun()

# Step 5 – Rewrite and moderate the response
elif st.session_state.stage == "rewrite":
    st.subheader("✍️ A refined version of your message")
    with st.spinner("Rewriting for clarity, fairness, and impact..."):
        rewrite = analyze_turn(st.session_state.dialogue)

    st.markdown("#### Here's a calmer, clearer version you might send:")
    st.text_area("Polished Reply:", value=rewrite, height=120)

    email_body = rewrite.replace(" ", "%20").replace("\n", "%0A")
    sms_body = rewrite.replace(" ", "%20").replace("\n", "%0A")
    st.markdown(f"[✉️ Email](mailto:?subject=Suggested%20Response&body={email_body})")
    st.markdown(f"[📱 SMS](sms:?body={sms_body})")

    st.markdown("---")
    st.info("Want to keep going? Paste their reply below and we'll continue helping.")
    st.session_state.stage = "loop"

# Step 6 – Loop: handle ongoing exchange
elif st.session_state.stage == "loop":
    st.subheader("Step 5: What did they say back?")
    new_input = st.text_area("Paste their most recent message here:")
    if st.button("Continue the conversation"):
        st.session_state.dialogue.append({"role": "user", "content": f"Interlocutor reply: {new_input}"})
        st.session_state.stage = "user_reply"
        st.rerun()

# Option to restart
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Start Over"):
    st.session_state.dialogue = []
    st.session_state.stage = "purpose"
    st.rerun()
