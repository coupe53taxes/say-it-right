# Interactive Streamlit App: Context-Aware Communication Assistant
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
if "debate_topic" not in st.session_state:
    st.session_state.debate_topic = ""
if "proposition" not in st.session_state:
    st.session_state.proposition = ""

st.set_page_config(page_title="Say It Right", page_icon="✉️")
st.title("Say It Right")
st.caption("Diffuse conflict. Preserve truth. Protect what matters.")

# GPT helper
def call_gpt(messages):
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=messages)
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# Goal Selection Grid
if st.session_state.stage == "goal_select":
    st.subheader("What best describes your situation?")
    st.markdown("Choose your goal to get started:")

    cols1 = st.columns(2)
    cols2 = st.columns(2)
    cols3 = st.columns(2)

    if cols1[0].button("🥊 Fight Productively"):
        st.session_state.stage = "setup_debate"
        st.rerun()

    cols1[1].button("🧯 Cool things down (Coming soon)", disabled=True)
    cols2[0].button("🧠 Make my case—no fight (Coming soon)", disabled=True)
    cols2[1].button("📱 Media has me heated (Coming soon)", disabled=True)
    cols3[0].button("❤️ It's personal (Coming soon)", disabled=True)
    cols3[1].button("😤 I just need to vent (Coming soon)", disabled=True)

# Debate Setup Screen
elif st.session_state.stage == "setup_debate":
    st.subheader("Set Up Your Debate")
    st.session_state.debate_topic = st.text_input("Debate Topic", st.session_state.debate_topic)
    st.session_state.user_A_name = st.text_input("First Debater's Name", st.session_state.user_A_name)
    user_A_position = st.text_area("Position Statement for First Debater")
    st.session_state.user_B_name = st.text_input("Second Debater's Name", st.session_state.user_B_name)
    user_B_position = st.text_area("Position Statement for Second Debater")

    if st.button("Next: Suggest Debate Proposition"):
        setup_context = f"Debate topic: {st.session_state.debate_topic}\n\n{st.session_state.user_A_name}'s position: {user_A_position}\n\n{st.session_state.user_B_name}'s position: {user_B_position}"
        prompt = [
            {"role": "system", "content": "You create debate propositions that help focus disagreements. Make it brief, clear, and centered on where the actual disagreement lies."},
            {"role": "user", "content": setup_context}
        ]
        st.session_state.proposition = call_gpt(prompt)
        st.session_state.fight_history.append({"topic": st.session_state.debate_topic, "positions": {st.session_state.user_A_name: user_A_position, st.session_state.user_B_name: user_B_position}})
        st.session_state.stage = "proposition_confirm"
        st.rerun()

# Proposition Confirmation
elif st.session_state.stage == "proposition_confirm":
    st.subheader("Suggested Proposition")
    st.markdown("### Based on what you wrote, here's a focused proposition to debate:")
    st.session_state.proposition = st.text_area("Proposition", value=st.session_state.proposition)

    if st.button("Start Debate with this Proposition"):
        st.session_state.stage = "pass_to_first_user"
        st.rerun()

# Handoff to First User
elif st.session_state.stage == "pass_to_first_user":
    st.header("Pass to First Debater")
    st.markdown("Pass the device to **User A**. Click below when ready.")
    if st.button(f"I'm {st.session_state.user_A_name}, Continue"):
        st.session_state.stage = "first_user_private"
        st.rerun()

# Placeholder for first user private screen (to be implemented)
elif st.session_state.stage == "first_user_private":
    st.write("This is where the private interaction for User A would begin.")
    if st.button("Back to Goal Selection"):
        st.session_state.stage = "goal_select"
        st.rerun()
