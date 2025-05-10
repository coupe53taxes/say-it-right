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

# Session state for storing conversation and controls
if "dialogue" not in st.session_state:
    st.session_state.dialogue = []
if "stage" not in st.session_state:
    st.session_state.stage = "purpose"
if "show_map" not in st.session_state:
    st.session_state.show_map = False

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

# Generate map description
def generate_convo_map(dialogue):
    map_prompt = [
        {"role": "system", "content": "You summarize and visually map how a conversation is progressing, especially arguments or disagreements."},
        {"role": "user", "content": f"Here's the conversation so far:\n\n{dialogue}\n\nPlease create a simple flow description and a one-paragraph summary."}
    ]
    return call_gpt(map_prompt)

# Sidebar map button
with st.sidebar:
    if st.button("🧭 View Conversation Map"):
        st.session_state.show_map = not st.session_state.show_map
    if st.session_state.show_map:
        st.subheader("Conversation Map")
        raw_dialogue = "\n\n".join([f"{entry['role']}: {entry['content']}" for entry in st.session_state.dialogue])
        map_output = generate_convo_map(raw_dialogue)
        st.markdown(map_output)

# Structured conversation analysis and rewriter
def analyze_turn(dialogue):
    system_prompt = {
        "role": "system",
        "content": (
            "You are an emotionally intelligent assistant helping users navigate difficult conversations."
            "Your job is to:"
            "1. Clarify what’s actually being argued"
            "2. Steelman the other person’s point of view"
            "3. Identify exaggerations or emotionally charged language"
            "4. Offer insights about the deeper disagreement"
            "5. Suggest how to keep the conversation constructive"
        )
    }
    return call_gpt([system_prompt] + dialogue)

# Just a spacer to ensure content differs for patch tracking

def generate_rewrite(dialogue):
    rewrite_prompt = [
        {"role": "system", "content": "You are a communication assistant that rewrites emotionally intense or unclear messages into tactful, truthful, and constructive ones. Always aim to preserve the user's intent while removing hyperbole, insults, or unproductive framing."},
        *dialogue,
        {"role": "user", "content": "Rewrite my last message in a more tactful, clear, and emotionally constructive way. If it contains factual exaggeration or assumptions, note or clarify them calmly within the rewrite."}
    ]
    return call_gpt(rewrite_prompt)

# Last step preview display
if len(st.session_state.dialogue) > 0:
    st.markdown("### 🔁 Previous Input")
    last = st.session_state.dialogue[-1]
    st.markdown(f"**{last['role'].capitalize()}:** {last['content']}")

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

    if "insight_response" not in st.session_state:
        with st.spinner("Thinking clearly about what matters most..."):
            insight = analyze_turn(st.session_state.dialogue)
        st.session_state.insight_response = insight

    st.markdown(st.session_state.insight_response)

    if st.button("Continue"):
        st.session_state.stage = "user_reply"
        del st.session_state.insight_response
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

    if st.button("Continue the conversation"):
        st.session_state.stage = "loop"
        del st.session_state.rewrite_response
        st.rerun()

# Step 6 – Loop: handle ongoing exchange
elif st.session_state.stage == "loop":
    st.subheader("Step 6: What did they say back?")
    new_input = st.text_area("Paste their most recent message here:")
    if st.button("Submit interlocutor's reply"):
        st.session_state.dialogue.append({"role": "user", "content": f"Interlocutor reply: {new_input}"})
        st.session_state.stage = "user_reply"
        st.rerun()

# Option to restart
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Start Over"):
    st.session_state.dialogue = []
    st.session_state.stage = "purpose"
    st.session_state.show_map = False
    st.rerun()
