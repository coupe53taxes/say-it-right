import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Cooler Heads", page_icon="🥊")
st.title("Cooler Heads")
st.caption("Productive debate. Preserve truth. Protect what matters.")

# Session state initialization
if "stage" not in st.session_state:
    st.session_state.stage = "setup"
if "debate_history" not in st.session_state:
    st.session_state.debate_history = []
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "users" not in st.session_state:
    st.session_state.users = {}
if "topic" not in st.session_state:
    st.session_state.topic = ""
if "current_input" not in st.session_state:
    st.session_state.current_input = ""
if "current_feedback" not in st.session_state:
    st.session_state.current_feedback = ""

# GPT helper
def call_gpt(messages):
    response = client.chat.completions.create(model="gpt-4o", messages=messages)
    return response.choices[0].message.content.strip()

# Screens
def setup_screen():
    st.subheader("Set up your debate:")
    user_a = st.text_input("First person's name:", key="user_a")
    stance_a = st.text_area(f"{user_a or 'First person'}'s position:", key="stance_a")

    user_b = st.text_input("Second person's name:", key="user_b")
    stance_b = st.text_area(f"{user_b or 'Second person'}'s position:", key="stance_b")

    topic = st.text_input("Briefly, what's the debate about?", key="debate_topic")

    if st.button("Start Debate"):
        if not all([user_a, stance_a, user_b, stance_b, topic]):
            st.error("Please fill in all fields to proceed.")
        else:
            st.session_state.users = {
                "A": {"name": user_a, "stance": stance_a},
                "B": {"name": user_b, "stance": stance_b}
            }
            st.session_state.topic = topic
            st.session_state.current_user = "A"
            st.session_state.stage = "handoff"
            st.rerun()

def handoff_screen():
    current = st.session_state.users[st.session_state.current_user]["name"]
    st.subheader(f"Please hand the device to {current}.")
    if st.button(f"{current} ready to continue"):
        st.session_state.stage = "user_input"
        st.rerun()

    st.markdown("---")
    if st.button("End Debate Now"):
        st.session_state.stage = "wrapup"
        st.rerun()

def user_input_screen():
    current_key = st.session_state.current_user
    current = st.session_state.users[current_key]["name"]
    other_key = "B" if current_key == "A" else "A"
    other = st.session_state.users[other_key]["name"]

    st.header(f"Your turn, {current}")
    if st.session_state.debate_history:
        last_public = st.session_state.debate_history[-1]["message"]
        st.markdown(f"**{other}'s last response:**")
        st.info(last_public)

    input_text = st.text_area(f"{current}, what's your response?")

    if st.button("Get feedback and refine response"):
        if input_text:
            feedback = call_gpt([
                {"role": "system", "content": f"""
                    You are helping {current} in a debate about "{st.session_state.topic}".
                    Their stance: {st.session_state.users[current_key]['stance']}.
                    Opponent ({other}) stance: {st.session_state.users[other_key]['stance']}.
                    Provide:
                    1. A fact-check of their argument
                    2. A steelman of the opponent's view
                    3. A persuasive rewrite of their message
                """},
                {"role": "user", "content": input_text}
            ])
            rewrite = call_gpt([
                {"role": "system", "content": "Return ONLY a persuasive rewrite of the user's message. No explanations, labels, or headings."},
                {"role": "user", "content": input_text}
            ])
            st.session_state.current_feedback = feedback
            st.session_state.current_input = rewrite
            st.session_state.stage = "feedback"
            st.rerun()
        else:
            st.error("Please enter your response.")

def feedback_screen():
    current = st.session_state.users[st.session_state.current_user]["name"]
    feedback = st.session_state.current_feedback
    st.header(f"🔍 {current}'s Feedback & Suggestions")
    st.write(feedback)

    polished_response = st.text_area("Refine or accept this suggested message:", st.session_state.current_input)

    if st.button("Lock in my response"):
        st.session_state.debate_history.append({
            "user": current,
            "message": polished_response
        })
        st.session_state.current_user = "B" if st.session_state.current_user == "A" else "A"
        st.session_state.stage = "handoff"
        st.rerun()

def wrapup_screen():
    st.header("🎯 Debate Summary")
    public_history = "\n\n".join([f"{item['user']}: {item['message']}" for item in st.session_state.debate_history])
    st.markdown(public_history)

    st.header("🧠 Personal Feedback")
    for key in ["A", "B"]:
        user = st.session_state.users[key]["name"]
        personal_feedback = call_gpt([
            {"role": "system", "content": f"Provide concise, private feedback to {user} about their performance in this debate. Include praise and constructive advice."},
            {"role": "user", "content": public_history}
        ])
        st.subheader(f"{user}'s feedback:")
        st.write(personal_feedback)

    if st.button("🤖 Who won?"):
        judgment = call_gpt([
            {"role": "system", "content": "Neutrally evaluate the debate and declare who argued their point more effectively, briefly explaining your decision."},
            {"role": "user", "content": public_history}
        ])
        st.markdown(f"### 🏆 Debate Winner:\n{judgment}")

    email_body = public_history.replace(" ", "%20").replace("\n", "%0A")
    st.markdown(f"[✉️ Share via Email](mailto:?subject=Our%20Debate%20Summary&body={email_body})")
    st.markdown(f"[📱 Share via SMS](sms:?body={email_body})")

    if st.button("🔄 New Debate"):
        for key in ["stage", "debate_history", "current_user", "users", "topic", "current_feedback", "current_input"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# Flow controller
if st.session_state.stage == "setup":
    setup_screen()
elif st.session_state.stage == "handoff":
    handoff_screen()
elif st.session_state.stage == "user_input":
    user_input_screen()
elif st.session_state.stage == "feedback":
    feedback_screen()
elif st.session_state.stage == "wrapup":
    wrapup_screen()
