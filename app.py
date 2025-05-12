import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Session State Initialization ---
def initialize_state():
    defaults = {
        "stage": "goal_select",
        "fight_stage": None,
        "fight_history": [],
        "current_user": "A",
        "user_A_name": "User A",
        "user_B_name": "User B",
        "debate_topic": "",
        "user_A_position": "",
        "user_B_position": "",
        "debate_prop": "",
        "A_last": "",
        "B_last": "",
        "last_turn": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

initialize_state()

st.set_page_config(page_title="Say It Right", page_icon="✉️")
st.title("Say It Right")
st.caption("Diffuse conflict. Preserve truth. Protect what matters.")

# --- GPT Call Helper ---
def call_gpt(messages):
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=messages)
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# --- Stage Logic ---
def goal_selection():
    st.subheader("What best describes your situation?")
    cols = st.columns(2)
    if cols[0].button("🥊 Fight Productively"):
        st.session_state.stage = "debate_setup"
        st.rerun()


def debate_setup():
    st.subheader("Set up your debate")
    st.session_state.debate_topic = st.text_input("Debate topic:", st.session_state.debate_topic)
    st.session_state.user_A_name = st.text_input("Name of User A:", st.session_state.user_A_name)
    st.session_state.user_A_position = st.text_input(f"{st.session_state.user_A_name}'s position:", st.session_state.user_A_position)
    st.session_state.user_B_name = st.text_input("Name of User B:", st.session_state.user_B_name)
    st.session_state.user_B_position = st.text_input(f"{st.session_state.user_B_name}'s position:", st.session_state.user_B_position)
    if st.button("Continue to Proposition"):
        st.session_state.stage = "proposition_edit"
        st.rerun()


def proposition_edit():
    st.subheader("🧭 Let's clarify the disagreement")
    summary = call_gpt([
        {"role": "system", "content": "Draft a clear, debate-ready proposition that fairly represents opposing views."},
        {"role": "user", "content": f"Topic: {st.session_state.debate_topic}\n\nUser A position: {st.session_state.user_A_position}\n\nUser B position: {st.session_state.user_B_position}"}
    ])
    st.session_state.debate_prop = st.text_area("Debate Proposition:", summary)
    if st.button("Pass to First Debater"):
        st.session_state.stage = "handoff_A"
        st.rerun()


def handoff_A():
    st.header("Pass to First Debater")
    st.markdown("Pass the device to **User A**. Click below when ready.")
    if st.button(f"I'm {st.session_state.user_A_name}, Continue"):
        st.session_state.stage = "user_A_input"
        st.rerun()


def user_input_turn(user):
    opponent = "B" if user == "A" else "A"
    user_name = st.session_state[f"user_{user}_name"]
    opponent_name = st.session_state[f"user_{opponent}_name"]
    st.subheader(f"🗣️ {user_name}, make your case")
    st.markdown(f"**Debate Proposition:** *{st.session_state.debate_prop}*")

    # Show prior opponent's response
    last_entry = [e for e in reversed(st.session_state.fight_history) if e['user'] == opponent]
    if last_entry:
        st.markdown(f"### {opponent_name}'s last response:")
        st.info(last_entry[0]['polished'])

    # User input
    response = st.text_area("Why do you support your position?")
    if st.button("Submit and Get Feedback"):
        st.session_state.fight_history.append({"user": user, "content": response})
        st.session_state.stage = f"user_{user}_feedback"
        st.rerun()


def user_feedback(user):
    opponent = "B" if user == "A" else "A"
    user_name = st.session_state[f"user_{user}_name"]
    opponent_name = st.session_state[f"user_{opponent}_name"]
    content = st.session_state.fight_history[-1]["content"]

    summary = call_gpt([
        {"role": "system", "content": f"You're helping {user_name} refine their debate message. First, offer a one-line fact check if needed. Then steel-man {opponent_name}'s position in 1-2 sentences. Then give a single polished rewrite of {user_name}'s input."},
        {"role": "user", "content": content}
    ])

    # Extract last paragraph only
    suggestion = summary.strip().split("\n")[-1]

    st.subheader("Your Improved Response")
    polished = st.text_area("Edit before submitting:", value=suggestion)
    if st.button("Submit and Pass"):
        st.session_state.fight_history[-1]["polished"] = polished
        st.session_state.current_user = opponent
        st.session_state.stage = f"handoff_{opponent}"
        st.rerun()


def end_handoff(user):
    st.header("Pass the device")
    st.markdown(f"Pass the device to **{st.session_state[f'user_{user}_name']}**. Click below when ready.")
    if st.button(f"I'm {st.session_state[f'user_{user}_name']}, Continue"):
        st.session_state.stage = f"user_{user}_input"
        st.rerun()


def view_summary():
    st.sidebar.header("Debate Tools")
    if st.sidebar.button("🧾 View Debate Summary"):
        transcript = "\n\n".join([f"{e['user']}: {e['polished']}" for e in st.session_state.fight_history if 'polished' in e])
        st.sidebar.markdown(transcript)
    if st.sidebar.button("🔚 End Debate"):
        st.session_state.stage = "end_summary"
        st.rerun()


def end_summary():
    st.subheader("🤝 Debate Complete")
    st.markdown("The following is a summary of the final positions and interaction:")
    summary = call_gpt([
        {"role": "system", "content": "Summarize the key arguments and disagreements from the following exchange, neutrally."},
        {"role": "user", "content": "\n\n".join([f"{e['user']}: {e['polished']}" for e in st.session_state.fight_history if 'polished' in e])}
    ])
    st.markdown(summary)
    if st.button("📣 Ask AI to Pick a Winner (Just for Fun)"):
        verdict = call_gpt([
            {"role": "system", "content": "You are an impartial judge. Pick a winner based on the strength of reasoning alone."},
            {"role": "user", "content": "\n\n".join([f"{e['user']}: {e['polished']}" for e in st.session_state.fight_history if 'polished' in e])}
        ])
        st.success(verdict)


# --- Main Routing ---
view_summary()

if st.session_state.stage == "goal_select":
    goal_selection()
elif st.session_state.stage == "debate_setup":
    debate_setup()
elif st.session_state.stage == "proposition_edit":
    proposition_edit()
elif st.session_state.stage == "handoff_A":
    handoff_A()
elif st.session_state.stage == "user_A_input":
    user_input_turn("A")
elif st.session_state.stage == "user_A_feedback":
    user_feedback("A")
elif st.session_state.stage == "handoff_B":
    end_handoff("B")
elif st.session_state.stage == "user_B_input":
    user_input_turn("B")
elif st.session_state.stage == "user_B_feedback":
    user_feedback("B")
elif st.session_state.stage == "end_summary":
    end_summary()
