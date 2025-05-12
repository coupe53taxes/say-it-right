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

# Initialize state
if "stage" not in st.session_state:
    st.session_state.stage = "goal_select"
if "fight_stage" not in st.session_state:
    st.session_state.fight_stage = None
if "fight_history" not in st.session_state:
    st.session_state.fight_history = []
if "current_user" not in st.session_state:
    st.session_state.current_user = "A"
if "debate_topic" not in st.session_state:
    st.session_state.debate_topic = ""
if "user_a_name" not in st.session_state:
    st.session_state.user_a_name = ""
if "user_b_name" not in st.session_state:
    st.session_state.user_b_name = ""
if "user_a_position" not in st.session_state:
    st.session_state.user_a_position = ""
if "user_b_position" not in st.session_state:
    st.session_state.user_b_position = ""
if "debate_proposition" not in st.session_state:
    st.session_state.debate_proposition = ""

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

# Goal selection
if st.session_state.stage == "goal_select":
    st.subheader("What best describes your situation?")
    st.markdown("Pick the one that fits best, and I’ll guide you from there.")

    cols1 = st.columns(2)
    cols2 = st.columns(2)
    cols3 = st.columns(2)

    if cols1[0].button("🥊 Fight Productively"):
        st.session_state.stage = "debate_setup"
        st.rerun()

    cols1[1].button("🧯 Cool things down (Coming soon)", disabled=True)
    cols2[0].button("🧠 Make my case—no fight (Coming soon)", disabled=True)
    cols2[1].button("📱 Online heated (Coming soon)", disabled=True)
    cols3[0].button("❤️ It's personal (Coming soon)", disabled=True)
    cols3[1].button("😤 I need to vent (Coming soon)", disabled=True)

# Debate setup
elif st.session_state.stage == "debate_setup":
    st.subheader("Set up your debate")
    st.session_state.debate_topic = st.text_input("What is the topic of the debate?")
    st.session_state.user_a_name = st.text_input("Name of User A")
    st.session_state.user_a_position = st.text_area("Position of User A")
    st.session_state.user_b_name = st.text_input("Name of User B")
    st.session_state.user_b_position = st.text_area("Position of User B")

    if st.button("Next: Draft a Proposition"):
        st.session_state.stage = "draft_proposition"
        st.rerun()

# Draft proposition
elif st.session_state.stage == "draft_proposition":
    st.subheader("Help Frame the Debate")

    prompt = [
        {"role": "system", "content": "Your job is to draft a clear debate proposition that frames a productive and focused disagreement."},
        {"role": "user", "content": f"Topic: {st.session_state.debate_topic}\n\n{st.session_state.user_a_name}'s stance: {st.session_state.user_a_position}\n\n{st.session_state.user_b_name}'s stance: {st.session_state.user_b_position}"}
    ]
    proposition = call_gpt(prompt)
    st.markdown("Here's a proposed debate resolution. You can edit if needed:")
    st.session_state.debate_proposition = st.text_area("Debate Proposition", value=proposition)

    if st.button(f"Next: Pass to {st.session_state.user_a_name}"):
        st.session_state.current_user = "A"
        st.session_state.fight_stage = "user_input"
        st.session_state.stage = "debate_moderator"
        st.rerun()

# Debate moderator flow
elif st.session_state.stage == "debate_moderator":
    current_user = st.session_state.current_user
    other_user = "B" if current_user == "A" else "A"
    current_name = st.session_state.user_a_name if current_user == "A" else st.session_state.user_b_name
    other_name = st.session_state.user_b_name if current_user == "A" else st.session_state.user_a_name

    if st.session_state.fight_stage == "user_input":
        st.subheader(f"🎤 {current_name}, tell us why you hold your view")
        user_justification = st.text_area("Briefly explain your reasoning:")
        if st.button("Submit justification"):
            st.session_state.fight_history.append({"user": current_name, "stance": user_justification})
            st.session_state.fight_stage = "user_feedback"
            st.rerun()

    elif st.session_state.fight_stage == "user_feedback":
        user_entry = st.session_state.fight_history[-1]["stance"]

        analysis = call_gpt([
            {"role": "system", "content": (
                f"You're a debate coach. Your task is to fact-check, steel-man the opposing view held by {other_name}, "
                f"and offer a tactful rewrite of {current_name}'s position to strengthen clarity and impact. Keep it brief."
            )},
            {"role": "user", "content": user_entry}
        ])

        rewrite_start = analysis.lower().find("rewrite")
        if rewrite_start != -1:
            suggested_reply = analysis[rewrite_start:].split("\n", 1)[-1].strip()
        else:
            suggested_reply = analysis

        st.subheader("🔧 Persuasive Rewrite")
        st.markdown(analysis[:rewrite_start].strip() if rewrite_start != -1 else analysis)
        polished = st.text_area("Final version to send:", value=suggested_reply)

        if st.button(f"Lock in and pass to {other_name}"):
            st.session_state.fight_history[-1]["polished"] = polished
            st.session_state.current_user = other_user
            st.session_state.fight_stage = "user_input"
            st.rerun()

# Sidebar summary tool
with st.sidebar:
    st.header("Debate Tools")
    if st.button("🧾 View Debate Summary") and st.session_state.fight_history:
        public_history = "\n\n".join(
            [f"{entry['user']}: {entry['polished']}" for entry in st.session_state.fight_history if "polished" in entry]
        )
        summary = call_gpt([
            {"role": "system", "content": "Summarize the public debate up to now."},
            {"role": "user", "content": public_history}
        ])
        st.markdown(summary)

# Restart option
if st.button("🔄 Restart Debate"):
    for key in ["stage", "fight_stage", "fight_history", "current_user", "debate_topic",
                "user_a_name", "user_b_name", "user_a_position", "user_b_position", "debate_proposition"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()
