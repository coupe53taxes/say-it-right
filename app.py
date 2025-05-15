# Full Integrated Streamlit Debate Moderator App

import streamlit as st
import os
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page Configuration
st.set_page_config(page_title="CoolerHeads", page_icon="✉️")

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

# GPT Call Helper
def call_gpt(messages):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    return response.choices[0].message.content.strip()

# Goal Selection Grid
if st.session_state.stage == "goal_select":
    st.title("Say It Right")
    st.caption("Diffuse conflict. Preserve truth. Protect what matters.")
    st.subheader("Choose your situation:")

    cols = st.columns(2)
    if cols[0].button("🥊 Fight Productively"):
        st.session_state.stage = "debate_setup"
        st.rerun()

    cols[1].button("🫯 Cool things down (Coming soon)", disabled=True)
    cols[0].button("🧠 Make my case—no fight (Coming soon)", disabled=True)
    cols[1].button("📱 Online heated (Coming soon)", disabled=True)
    cols[0].button("❤️ It's personal (Coming soon)", disabled=True)
    cols[1].button("😤 I need to vent (Coming soon)", disabled=True)

# Debate Setup
elif st.session_state.stage == "debate_setup":
    st.header("Set up your debate")
    debate_topic = st.text_area("Debate Topic:", key="debate_topic_input")

    st.session_state.user_A_name = st.text_input("User A Name:", value=st.session_state.user_A_name, key="user_A_name_input")
    st.session_state.user_A_position = st.text_area("Position of User A:", key="user_A_position_input")
    st.session_state.user_B_name = st.text_input("User B Name:", value=st.session_state.user_B_name, key="user_B_name_input")
    st.session_state.user_B_position = st.text_area("Position of User B:", key="user_B_position_input")

    if st.button("Generate Proposition"):
        prop_prompt = [{
            "role": "system",
            "content": "Generate a neutral debate proposition: 'The disagreement is over whether X is beneficial.'"
        }, {
            "role": "user",
            "content": f"Topic: {debate_topic}\n{st.session_state.user_A_name}: {st.session_state.user_A_position}\n{st.session_state.user_B_name}: {st.session_state.user_B_position}"
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
            "message": polished_reply
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

    if st.button("🤖Let AI Decide the Winner"):
        judge_prompt = [{
            "role": "system",
            "content": "Decide who presented the stronger arguments in the following exchange. Explain briefly in 3 sentences or less."
        }, {
            "role": "user",
            "content": "\n".join([
                f"{st.session_state.user_A_name if e['user']=='A' else st.session_state.user_B_name}: {e['message']}"
                for e in st.session_state.fight_history])
        }]
        winner_judgment = call_gpt(judge_prompt)
        st.success(winner_judgment)

# Sidebar
with st.sidebar:
    st.header("Debate Controls")
    if st.button("🔎 View Summary So Far"):
        st.session_state.summary_mode = not st.session_state.summary_mode
        st.rerun()

    if st.button("🛑 End Debate"):
        st.session_state.stage = "summary"
        st.rerun()

    if st.session_state.summary_mode and st.session_state.fight_history:
        st.markdown("### 📋 Summary So Far")
        st.markdown(f"**Proposition:** {st.session_state.debate_prop}")
        for entry in st.session_state.fight_history:
            user_name = st.session_state.user_A_name if entry['user'] == 'A' else st.session_state.user_B_name
            st.write(f"{user_name}: {entry['message']}")
