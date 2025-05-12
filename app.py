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

# Set up session state
if "stage" not in st.session_state:
    st.session_state.stage = "goal_select"
if "fight_stage" not in st.session_state:
    st.session_state.fight_stage = None
if "fight_history" not in st.session_state:
    st.session_state.fight_history = []
if "current_user" not in st.session_state:
    st.session_state.current_user = "A"

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

# Icon Grid (Initial page)
if st.session_state.stage == "goal_select":
    st.subheader("What best describes your situation?")
    st.markdown("Pick the one that fits best, and I’ll guide you from there.")

    cols1 = st.columns(2)
    cols2 = st.columns(2)
    cols3 = st.columns(2)

    if cols1[0].button("🫈 Fight Productively"):
        st.session_state.stage = "debate_moderator"
        st.session_state.fight_stage = "user_a_input"
        st.session_state.fight_history = []
        st.session_state.current_user = "A"
        st.rerun()

    cols1[1].button("🫯 Cool things down (Coming soon)", disabled=True)
    cols2[0].button("🧠 Make my case—no fight (Coming soon)", disabled=True)
    cols2[1].button("📱 Online heated (Coming soon)", disabled=True)
    cols3[0].button("❤️ It's personal (Coming soon)", disabled=True)
    cols3[1].button("🨤 I need to vent (Coming soon)", disabled=True)

# Debate Moderator Mode
elif st.session_state.stage == "debate_moderator":
    st.header("🌜 Debate Moderator Mode")

    current_user = st.session_state.current_user
    other_user = "B" if current_user == "A" else "A"

    if st.session_state.fight_stage == f"user_{current_user.lower()}_input":
        st.subheader(f"🗣️ User {current_user}: Your Argument")

        if st.session_state.fight_history:
            last_polished = st.session_state.fight_history[-1].get("polished", "")
            st.markdown(f"**User {other_user}'s last response:**")
            st.info(last_polished)

        user_text = st.text_area("Enter your side of the debate:")
        if st.button("Get My Private Feedback"):
            st.session_state.fight_history.append({"user": current_user, "content": user_text})
            st.session_state.fight_stage = f"user_{current_user.lower()}_feedback"
            st.rerun()

    elif st.session_state.fight_stage == f"user_{current_user.lower()}_feedback":
        st.subheader(f"🔍 User {current_user}: Feedback & Fact Check")

        feedback = call_gpt([
            {"role": "system", "content": (
                "You're moderating a debate. Fact-check the user's input, steelman the opposing view, and offer a clear, persuasive rewrite."
            )},
            {"role": "user", "content": st.session_state.fight_history[-1]["content"]}
        ])

        st.markdown("### 🧠 Private Feedback:")
        st.write(feedback)

        polished_response = st.text_area("Polished version of your argument:", feedback)

        if st.button(f"Finalize and pass to User {other_user}"):
            st.session_state.fight_history[-1]["polished"] = polished_response
            st.session_state.current_user = other_user
            st.session_state.fight_stage = f"user_{other_user.lower()}_input"
            st.rerun()

    # Sidebar Summary
    with st.sidebar:
        st.header("Debate Tools")
        if st.button("🗒️ View Debate Summary") and st.session_state.fight_history:
            history = "\n\n".join([
                f"{entry['user']}: {entry['polished']}"
                for entry in st.session_state.fight_history if 'polished' in entry
            ])
            summary = call_gpt([
                {
                    "role": "system",
                    "content": (
                        "Provide a neutral summary of the ongoing debate highlighting points of agreement, disagreement, and potential resolution points."
                    )
                },
                {"role": "user", "content": history}
            ])
            st.markdown(summary)

    if st.button("🔄 Restart Debate"):
        st.session_state.stage = "goal_select"
        st.session_state.fight_stage = None
        st.session_state.fight_history = []
        st.session_state.current_user = "A"
        st.rerun()

    st.caption("All feedback remains confidential. Your opponent can't see your inputs or the feedback you receive.")
