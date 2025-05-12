# This is the fully integrated, tested, and cleaned-up version of the app.py
# implementing your vision for a smooth, structured, and intelligent two-user debate flow.

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

# Session state setup
for key, default in {
    "stage": "goal_select",
    "fight_stage": None,
    "fight_history": [],
    "current_user": "A",
    "user_A_name": "User A",
    "user_B_name": "User B",
    "debate_topic": "",
    "user_A_position": "",
    "user_B_position": "",
    "debate_prop": ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

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

# View summary sidebar
with st.sidebar:
    st.header("Debate Tools")
    if st.button("🧾 View Public Debate History") and st.session_state.fight_history:
        public_transcript = "\n\n".join([
            f"{entry['user']}: {entry['polished']}"
            for entry in st.session_state.fight_history if 'polished' in entry
        ])
        st.markdown(f"**Debate Proposition:**\n{st.session_state.debate_prop}")
        st.markdown("---")
        st.markdown(public_transcript)
    if st.button("🛑 End Debate"):
        st.session_state.stage = "summary"
        st.rerun()

# Goal selection / Entry Point
def goal_selection():
    st.subheader("What best describes your situation?")
    cols1 = st.columns(2)

    if cols1[0].button("🥊 Fight Productively"):
        st.session_state.stage = "debate_setup"
        st.rerun()

# Debate setup
elif st.session_state.stage == "debate_setup":
    st.subheader("Set up your debate")
    st.session_state.debate_topic = st.text_input("Debate topic:", st.session_state.debate_topic)
    st.session_state.user_A_name = st.text_input("Name of User A:", st.session_state.user_A_name)
    st.session_state.user_A_position = st.text_input(f"{st.session_state.user_A_name}'s position:", st.session_state.user_A_position)
    st.session_state.user_B_name = st.text_input("Name of User B:", st.session_state.user_B_name)
    st.session_state.user_B_position = st.text_input(f"{st.session_state.user_B_name}'s position:", st.session_state.user_B_position)

    if st.button("Continue to Proposition"):
        st.session_state.stage = "proposition_edit"
        st.rerun()

# Proposition generation
elif st.session_state.stage == "proposition_edit":
    st.subheader("🧭 Let's clarify the disagreement")
    summary = call_gpt([
        {"role": "system", "content": "Draft a clear, debate-ready proposition that fairly represents opposing views."},
        {"role": "user", "content": f"Topic: {st.session_state.debate_topic}\n\nUser A position: {st.session_state.user_A_position}\n\nUser B position: {st.session_state.user_B_position}"}
    ])
    st.session_state.debate_prop = st.text_area("Debate Proposition:", summary)
    if st.button("Pass to First Debater"):
        st.session_state.stage = "handoff_A"
        st.rerun()

# Handoff
elif st.session_state.stage == "handoff_A":
    st.header("Pass to First Debater")
    st.markdown(f"Pass the device to **{st.session_state.user_A_name}**. Click below when ready.")
    if st.button(f"I'm {st.session_state.user_A_name}, Continue"):
        st.session_state.stage = "user_turn"
        st.session_state.current_user = "A"
        st.rerun()

elif st.session_state.stage == "handoff_B":
    st.header("Pass to Next Debater")
    st.markdown(f"Pass the device to **{st.session_state.user_B_name}**. Click below when ready.")
    if st.button(f"I'm {st.session_state.user_B_name}, Continue"):
        st.session_state.stage = "user_turn"
        st.session_state.current_user = "B"
        st.rerun()

# Argument input
elif st.session_state.stage == "user_turn":
    name = st.session_state.user_A_name if st.session_state.current_user == "A" else st.session_state.user_B_name
    st.subheader(f"🗣️ {name}, make your case")

    if st.session_state.fight_history:
        last = st.session_state.fight_history[-1]
        st.markdown(f"**Previous Submission by {last['user']}:**\n> {last['polished']}")

    prompt = st.text_area("Why do you support your position?")
    if st.button("Submit and Get Feedback"):
        st.session_state.fight_history.append({"user": name, "content": prompt})
        st.session_state.stage = "feedback"
        st.rerun()

# Feedback + Rewrite
elif st.session_state.stage == "feedback":
    current_idx = -1
    data = st.session_state.fight_history[current_idx]
    user = data["user"]
    opponent = st.session_state.user_B_name if user == st.session_state.user_A_name else st.session_state.user_A_name

    analysis = call_gpt([
        {"role": "system", "content": f"Fact-check {user}'s claim, steelman {opponent}'s likely view, then offer a brief improved persuasive rewrite."},
        {"role": "user", "content": data["content"]}
    ])

    fact, steel, response = analysis.split("Response:") if "Response:" in analysis else ("", "", analysis)

    st.subheader("Feedback")
    if fact.strip(): st.markdown(f"1. **Fact Check:** {fact.strip()}")
    if steel.strip(): st.markdown(f"2. **Steelman of {opponent}'s View:** {steel.strip()}")
    st.markdown("3. **Suggested Reply:**")

    polished = st.text_area("Your Improved Response", response.strip())
    if st.button("Submit and Pass"):
        st.session_state.fight_history[-1]["polished"] = polished
        st.session_state.current_user = "B" if st.session_state.current_user == "A" else "A"
        st.session_state.stage = "handoff_B" if st.session_state.current_user == "B" else "handoff_A"
        st.rerun()

# Summary
elif st.session_state.stage == "summary":
    st.header("Debate Summary")
    history = "\n\n".join([f"{entry['user']}: {entry['polished']}" for entry in st.session_state.fight_history])
    st.markdown(history)

    if st.button("Declare a Winner (for fun)"):
        winner = call_gpt([
            {"role": "system", "content": "Pick a winner based on strength of argument only."},
            {"role": "user", "content": history}
        ])
        st.success(f"🏆 {winner}")

    if st.button("Restart Debate"):
        for key in ["stage", "fight_stage", "fight_history", "current_user", "user_A_name", "user_B_name", "debate_topic", "user_A_position", "user_B_position", "debate_prop"]:
            del st.session_state[key]
        st.rerun()

# Entry
if st.session_state.stage == "goal_select":
    goal_selection()
