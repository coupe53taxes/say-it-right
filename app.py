#Full Integrated Streamlit Debate Moderator App

import streamlit as st
import os
import re
from openai import OpenAI
from PIL import Image
import requests

from datetime import datetime
from zoneinfo import ZoneInfo
now = datetime.now(ZoneInfo("America/New_York"))
iso_timestamp = now.isoformat()  # This will include offset like "-04:00"

# Page Configuration
st.set_page_config(page_title="CoolerHeads", page_icon="🔥🧠🧊")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
ZAPIER_WEBHOOK_URL = st.secrets["ZAPIER_WEBHOOK_URL"]

# Show logo at top of page
st.image("CoolerHeads logo 1.png", width=200)

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
        "summary_mode": False,
        "debate_topic_input": "",
    }
    for key, value in keys_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_state()

#for unique user data
import uuid

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# GPT Call Helper
def call_gpt(messages):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    return response.choices[0].message.content.strip()

def extract_winner_name(judgment_text, name_a, name_b):
    text = judgment_text.lower()
    if name_a.lower() in text:
        return name_a
    elif name_b.lower() in text:
        return name_b
    else:
        return "Undetermined"

# Send transcript to Zapier
ZAPIER_WEBHOOK_URL = os.getenv("ZAPIER_WEBHOOK_URL")

def send_transcript_to_zapier():
    
    transcript_lines = []
    transcript_lines.append(f"=== New Debate Session ===")
    transcript_lines.append(f"Timestamp: {datetime.now(ZoneInfo('America/New_York')).strftime('%Y-%m-%d %H:%M:%S')}")
    transcript_lines.append(f"Topic: {st.session_state.get('debate_topic_input', 'No topic provided')}")
    transcript_lines.append(f"{st.session_state.user_A_name} position: {st.session_state.user_A_position}")
    transcript_lines.append(f"{st.session_state.user_B_name} position: {st.session_state.user_B_position}")
    
    for entry in st.session_state.fight_history:
        user_name = st.session_state.user_A_name if entry['user'] == 'A' else st.session_state.user_B_name
        transcript_lines.append(f"\n{user_name} INPUT:\n{entry.get('raw_input', '')}")
        transcript_lines.append(f"FEEDBACK:\n{entry.get('feedback', '')}")
        transcript_lines.append(f"FINAL REPLY:\n{entry['message']}")

    transcript_lines.append("\n=== AI Decision (Not Always Shown to Users) ===")
    transcript_lines.append(st.session_state.get("winner_judgment", "N/A"))
    transcript_lines.append("\n=== End of Session ===\n")
    final_text = "\n".join(transcript_lines)

    zapier_url = os.getenv("ZAPIER_WEBHOOK_URL")

    topic_input = st.session_state.get("debate_topic_input", "").strip()
    topic_display = topic_input if topic_input else "No topic provided"

    # Clean version for filenames: underscores, no special chars
    topic_clean = re.sub(r"[^a-zA-Z0-9_]+", "", topic_input.replace(" ", "_")).lower()[:50]
    if not topic_clean:
        topic_clean = "untitled"
    
    timestamp_local = datetime.now(ZoneInfo("America/New_York"))
    timestamp_iso = timestamp_local.isoformat()  # includes DST-aware offset, e.g., -04:00
    timestamp_display = timestamp_local.strftime('%Y-%m-%d %H:%M:%S')  # for readability
    timestamp_label = timestamp_local.strftime('%Y-%m-%d_%H-%M-%S_%Z')  # for filename
    
    payload = {
        "transcript_text": final_text,
        "session_timestamp": timestamp_iso,
        "session_timestamp_readable": timestamp_display,
        "debate_topic_clean": topic_clean,
        "filename_timestamp": timestamp_label,
        
        # For the spreadsheet
        "Timestamp": timestamp_local.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "Topic": topic_display,
        "User A Name": st.session_state.get("user_A_name") or "User A",
        "User B Name": st.session_state.get("user_B_name") or "User B",
        "User A Position": st.session_state.get("user_A_position") or "No position provided",
        "User B Position": st.session_state.get("user_B_position") or "No position provided",
        "Number of Rounds": len(st.session_state.fight_history),
        "LLM Productivity": 0,
        "User Rating": "N/A",
        "Transcript URL": "N/A",
        "Summary": "N/A",
        "Winner": extract_winner_name(st.session_state.get("winner_judgment", "N/A"),
                              st.session_state.user_A_name,
                              st.session_state.user_B_name),
        "Flagged": False
    }

    try:
        requests.post(zapier_url, json=payload)
    except Exception as e:
        st.error(f"Failed to send transcript to Zapier: {e}")

def log_user_activity():
    activity_payload = {
        "Timestamp": datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M:%S %Z"),
        "User ID": st.session_state.user_id,
        "Session ID": st.session_state.session_id,
        "Stage Reached": st.session_state.stage,
        "Number of Rounds": len(st.session_state.fight_history),
        "Topic": st.session_state.get("debate_topic_input", "N/A").strip() or "N/A",
        "User Rating": "N/A",  # Placeholder
        "Completed": st.session_state.stage == "summary"
    }

    try:
        requests.post(st.secrets["ZAPIER_ACTIVITY_WEBHOOK_URL"], json=activity_payload)
    except Exception as e:
        st.error(f"Failed to send user activity log: {e}")

# Goal Selection Grid
if st.session_state.stage == "goal_select":
    st.title("CoolerHeads")
    st.caption("Diffuse the conflict. Strengthen the relationships. Seek the truth.")
    st.subheader("Choose your situation:")

    cols = st.columns(2)
    if cols[0].button("🥊 Fight Productively"):
        st.session_state.stage = "debate_setup"
        st.rerun()

    cols[1].button("🧯 Cool things down (Coming soon)", disabled=True)
    cols[0].button("🧠 Make my case—no fight (Coming soon)", disabled=True)
    cols[1].button("📱 Online heated (Coming soon)", disabled=True)
    cols[0].button("❤️ It's personal (Coming soon)", disabled=True)
    cols[1].button("😤 I need to vent (Coming soon)", disabled=True)

# Debate Setup
elif st.session_state.stage == "debate_setup":
    st.header("Set up your debate")

    st.session_state.debate_topic_input = st.text_area("Debate Topic:", value=st.session_state.debate_topic_input)
    st.text_input("User A Name:", key="user_A_name", value=st.session_state.user_A_name)
    st.text_area("Position of User A:", key="user_A_position", value=st.session_state.user_A_position)
    st.text_input("User B Name:", key="user_B_name", value=st.session_state.user_B_name)
    st.text_area("Position of User B:", key="user_B_position", value=st.session_state.user_B_position)

    if st.button("Generate Proposition"):
        prop_prompt = [{
            "role": "system",
            "content": "Generate a neutral debate proposition: 'The disagreement is over whether X is beneficial.'"
        }, {
            "role": "user",
            "content": f"Topic: {st.session_state.debate_topic_input}\n"
                       f"{st.session_state.user_A_name}: {st.session_state.user_A_position}\n"
                       f"{st.session_state.user_B_name}: {st.session_state.user_B_position}"
        }]
        st.session_state.debate_prop = call_gpt(prop_prompt)
        st.session_state.stage = "proposition_review"
        st.rerun()

# Proposition Review
elif st.session_state.stage == "proposition_review":
    st.subheader("Clarify the disagreement")
    st.session_state.debate_prop = st.text_area("Debate Proposition:", value=st.session_state.debate_prop)

    if st.button("Proceed to Debate"):
        st.session_state.stage = "private_input"
        st.session_state.current_user = "A"
        st.rerun()

# Private Input
elif st.session_state.stage == "private_input":
    current_name = st.session_state.user_A_name if st.session_state.current_user == "A" else st.session_state.user_B_name
    opponent_name = st.session_state.user_B_name if st.session_state.current_user == "A" else st.session_state.user_A_name

    st.subheader(f"{current_name}, it’s your turn.")
    if st.session_state.fight_history:
        last_reply = st.session_state.fight_history[-1]["message"]
        st.info(f"{opponent_name}'s response: {last_reply}")

    user_input = st.text_area("Your argument:")
    if st.button("Get Feedback"):
        feedback_prompt = [{
            "role": "system",
            "content": "You are a debate assistant helping the user give their strongest reply. You'll receive the debate topic, positions, and the user's current draft. Provide structured feedback: mirror what the user is trying to say, as in 'It sounds like you're arguing that...', fact-check if needed, steelman the *opponent's* position, flag fallacies, and end with a brief proposed response clearly labeled with 'Suggested Response:'."
        }, {
            "role": "user",
            "content": f"Debate topic: {st.session_state.debate_prop}\n\n"
                       f"{st.session_state.user_A_name}'s position: {st.session_state.user_A_position}\n"
                       f"{st.session_state.user_B_name}'s position: {st.session_state.user_B_position}\n"
                       f"Current user: {current_name}\n"
                       f"Current draft: {user_input}"
        }]
        feedback = call_gpt(feedback_prompt)
        st.session_state.temp_feedback = feedback
        st.session_state.temp_input = user_input
        st.session_state.stage = "feedback"
        st.rerun()

# Feedback
elif st.session_state.stage == "feedback":
    feedback = st.session_state.temp_feedback
    st.markdown("### Your Feedback")
    st.write(feedback)

    match = re.search(r"(?i)suggested response:\s*(.*)", feedback, re.DOTALL)
    suggested_reply = match.group(1).strip() if match else ""
    polished_reply = st.text_area("Polished Reply:", value=suggested_reply)

    if st.button("Submit & Pass"):
        st.session_state.fight_history.append({
            "user": st.session_state.current_user,
            "message": polished_reply,
            "raw_input": st.session_state.temp_input,
            "feedback": feedback
        })
        st.session_state.current_user = "B" if st.session_state.current_user == "A" else "A"
        st.session_state.stage = "handoff"
        st.rerun()

# Handoff
elif st.session_state.stage == "handoff":
    next_user = st.session_state.user_A_name if st.session_state.current_user == "A" else st.session_state.user_B_name
    st.header(f"Pass the device to {next_user}")

    if st.button(f"I'm {next_user}, continue"):
        st.session_state.stage = "private_input"
        st.rerun()

# Summary
elif st.session_state.stage == "summary":
    st.header("Debate Summary")
    st.markdown(f"**Proposition:** {st.session_state.debate_prop}")

    summary_prompt = [{
        "role": "system",
        "content": "Write a short (under 5 sentences) summary of the public debate exchange below. Be neutral and conversational."
    }, {
        "role": "user",
        "content": "\n".join([
            f"{st.session_state.user_A_name if e['user']=='A' else st.session_state.user_B_name}: {e['message']}"
            for e in st.session_state.fight_history])
    }]
    debate_summary = call_gpt(summary_prompt)
    st.markdown(debate_summary)

    # Always generate winner (hidden until revealed)
    judge_prompt = [{
        "role": "system",
        "content": "Decide who presented the stronger arguments in the following exchange. Explain briefly in 3 sentences or less."
    }, {
        "role": "user",
        "content": "\n".join([
            f"{st.session_state.user_A_name if e['user']=='A' else st.session_state.user_B_name}: {e['message']}"
            for e in st.session_state.fight_history])
    }]
    st.session_state.winner_judgment = call_gpt(judge_prompt)
    
    # Optional reveal button
    if st.button("🤖Let AI Decide the Winner"):
        st.success(st.session_state.winner_judgment)

    send_transcript_to_zapier()
    log_user_activity()

# Sidebar
with st.sidebar:
    st.header("Debate Controls")
    if st.button("🔎 View Summary So Far"):
        st.session_state.summary_mode = not st.session_state.summary_mode
        st.rerun()

    if st.button("🚩 End Debate"):
        st.session_state.stage = "summary"
        st.rerun()

    if st.session_state.summary_mode and st.session_state.fight_history:
        st.markdown("### 📋 Summary So Far")
        st.markdown(f"**Proposition:** {st.session_state.debate_prop}")
        for entry in st.session_state.fight_history:
            user_name = st.session_state.user_A_name if entry['user'] == 'A' else st.session_state.user_B_name
            st.write(f"{user_name}: {entry['message']}")
