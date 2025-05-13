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
for key, default in {
    "stage": "goal_select",
    "fight_stage": None,
    "fight_history": [],
    "current_user": "A",
    "user_A_name": "User A",
    "user_B_name": "User B",
    "user_A_position": "",
    "user_B_position": "",
    "debate_topic": "",
    "debate_prop": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

st.set_page_config(page_title="Say It Right", page_icon="✉️")
st.title("Say It Right")
st.caption("Diffuse conflict. Preserve truth. Protect what matters.")

# --- Helper Function ---
def call_gpt(messages):
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=messages)
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# --- Stage: Goal Selection ---
if st.session_state.stage == "goal_select":
    st.subheader("What best describes your situation?")
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

# --- Stage: Debate Setup ---
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

# --- Stage: Proposition Generation ---
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

# --- Stage: Handoff A ---
elif st.session_state.stage == "handoff_A":
    st.header("Pass to First Debater")
    st.markdown("Pass the device to **User A**. Click below when ready.")
    if st.button(f"I'm {st.session_state.user_A_name}, Continue"):
        st.session_state.stage = "first_user_private"
        st.rerun()

# --- Stage: User A First Response ---
elif st.session_state.stage == "first_user_private":
    st.subheader(f"🗣️ {st.session_state.user_A_name}, make your case")
    st.markdown(f"**Debate Proposition:** *{st.session_state.debate_prop}*\n\nParticipants will discuss and evaluate the potential benefits and drawbacks of the tariffs, with one side arguing in favor of their positive impact on domestic industries and the economy, while the other side will argue that the tariffs are ultimately detrimental to economic growth and consumer prices.*")

    user_input = st.text_area("Why do you support your position?")
    if st.button("Submit and Get Feedback"):
        st.session_state.fight_history.append({"user": st.session_state.user_A_name, "content": user_input})
        st.session_state.stage = "feedback_A"
        st.rerun()

# --- Stage: Feedback A ---
elif st.session_state.stage == "feedback_A":
    user_input = st.session_state.fight_history[-1]["content"]
    opponent_name = st.session_state.user_B_name

    feedback = call_gpt([
        {"role": "system", "content": (
            f"You're moderating a debate. Briefly fact-check {st.session_state.user_A_name}'s argument, then offer a concise steel-man of {opponent_name}'s likely position, and conclude with a polished version of {st.session_state.user_A_name}'s argument. Keep each part under 3 sentences."
        )},
        {"role": "user", "content": user_input}
    ])

    st.markdown("### Feedback")
    st.markdown(feedback)

    polished_response = feedback.split("Response:")[-1].strip()
    st.markdown("---")
    st.subheader("Your Improved Response")
    st.markdown("Edit before submitting:")
    final_response = st.text_area("Polished version of your argument:", value=polished_response)

    if st.button("Submit and Pass"):
        st.session_state.fight_history[-1]["polished"] = final_response
        st.session_state.stage = "handoff_B"
        st.rerun()

# Add future stages here, including handoff_B, feedback_B, and ongoing response cycles
