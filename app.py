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

# Initialize session state
if "stage" not in st.session_state:
    st.session_state.stage = "goal_select"
if "fight_stage" not in st.session_state:
    st.session_state.fight_stage = None
if "fight_history" not in st.session_state:
    st.session_state.fight_history = []
if "current_user" not in st.session_state:
    st.session_state.current_user = "A"
if "user_a_name" not in st.session_state:
    st.session_state.user_a_name = "User A"
if "user_b_name" not in st.session_state:
    st.session_state.user_b_name = "User B"
if "topic" not in st.session_state:
    st.session_state.topic = ""
if "proposition" not in st.session_state:
    st.session_state.proposition = ""

# GPT Call Helper
def call_gpt(messages):
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=messages)
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# Step 1: Goal Selection
def show_goal_selection():
    st.subheader("What best describes your situation?")
    st.markdown("Pick the one that fits best, and I’ll guide you from there.")

    cols1 = st.columns(2)
    cols2 = st.columns(2)
    cols3 = st.columns(2)

    if cols1[0].button("🥊 Fight Productively"):
        st.session_state.stage = "debate_setup"
    cols1[1].button("🧯 Cool things down (Coming soon)", disabled=True)
    cols2[0].button("🧠 Make my case—no fight (Coming soon)", disabled=True)
    cols2[1].button("📱 Online heated (Coming soon)", disabled=True)
    cols3[0].button("❤️ It's personal (Coming soon)", disabled=True)
    cols3[1].button("😤 I need to vent (Coming soon)", disabled=True)

# Step 2: Debate Setup
def show_debate_setup():
    st.subheader("Set up your debate")
    st.session_state.topic = st.text_input("Debate Topic:", value=st.session_state.topic)
    st.session_state.user_a_name = st.text_input("Name of First User:", value=st.session_state.user_a_name)
    st.session_state.user_a_position = st.text_input(f"{st.session_state.user_a_name}'s Position:")
    st.session_state.user_b_name = st.text_input("Name of Second User:", value=st.session_state.user_b_name)
    st.session_state.user_b_position = st.text_input(f"{st.session_state.user_b_name}'s Position:")

    if st.button("Next"):
        st.session_state.stage = "proposition_suggestion"
        st.rerun()

# Step 3: Proposition Suggestion
def show_proposition_suggestion():
    st.subheader("Suggested Debate Proposition")
    suggestion = call_gpt([
        {"role": "system", "content": "Your job is to turn two positions into a concise, fair proposition they can debate."},
        {"role": "user", "content": f"Topic: {st.session_state.topic}\n{st.session_state.user_a_name}'s stance: {st.session_state.user_a_position}\n{st.session_state.user_b_name}'s stance: {st.session_state.user_b_position}"}
    ])
    st.session_state.proposition = st.text_area("Edit if needed:", value=suggestion)
    if st.button("Looks good – let’s begin!"):
        st.session_state.stage = "handoff_to_a"
        st.session_state.fight_history = []
        st.session_state.current_user = "A"
        st.rerun()

# Intermediary Handoff Page
def show_handoff():
    user = st.session_state.current_user
    name = st.session_state.user_a_name if user == "A" else st.session_state.user_b_name
    st.header(f"Now it’s {name}'s turn")
    st.markdown("Please pass the device to the next user.")
    if st.button("I’m ready"):
        st.session_state.stage = f"user_{user.lower()}_justify"
        st.rerun()

# Justification Entry
def show_justification():
    user = st.session_state.current_user
    name = st.session_state.user_a_name if user == "A" else st.session_state.user_b_name
    st.subheader(f"{name}, why do you believe your position is right?")
    justification = st.text_area("Share your reasoning:")
    if st.button("Continue"):
        st.session_state.fight_history.append({"user": name, "content": justification})
        st.session_state.stage = f"user_{user.lower()}_feedback"
        st.rerun()

# Feedback Page
def show_feedback():
    user = st.session_state.current_user
    name = st.session_state.user_a_name if user == "A" else st.session_state.user_b_name
    other_name = st.session_state.user_b_name if user == "A" else st.session_state.user_a_name
    last_entry = st.session_state.fight_history[-1]

    summary = call_gpt([
        {"role": "system", "content": "Fact-check, briefly steelman the opposing view, then rewrite user's point clearly and persuasively in their own style. Each section should be 1-3 sentences."},
        {"role": "user", "content": last_entry['content']}
    ])

    parts = summary.split("###")
    fact_check = next((p for p in parts if "Fact" in p), "").strip()
    steelman = next((p for p in parts if "Steel" in p), "").strip()
    rewrite = next((p for p in parts if "Rewrite" in p), "").strip()

    st.markdown(f"**Fact-check of {name}'s Claim:**\n{fact_check}")
    st.markdown(f"**Steel-Manning {other_name}'s Side:**\n{steelman}")
    st.markdown("**Concise Polished Reply:**")

    response = rewrite.split("\n", 1)[-1] if "\n" in rewrite else rewrite
    final = st.text_area("Polished version of your argument:", value=response)

    if st.button("Lock in and pass to other user"):
        st.session_state.fight_history[-1]["polished"] = final
        st.session_state.current_user = "B" if user == "A" else "A"
        st.session_state.stage = "handoff"
        st.rerun()

# Debate Summary

def show_summary():
    st.subheader("Debate Summary")
    transcript = "\n\n".join([f"{entry['user']}: {entry['polished']}" for entry in st.session_state.fight_history if 'polished' in entry])
    st.markdown(transcript)

    if st.button("📊 End Debate and Get Final Thoughts"):
        st.session_state.stage = "wrap_up"
        st.rerun()

# Wrap-up Page
def show_wrap_up():
    a_entries = [e for e in st.session_state.fight_history if e['user'] == st.session_state.user_a_name]
    b_entries = [e for e in st.session_state.fight_history if e['user'] == st.session_state.user_b_name]

    summary_a = call_gpt([
        {"role": "system", "content": "Give a short helpful note to this debater on how they communicated, what they did well, and what to improve."},
        {"role": "user", "content": "\n\n".join([e['polished'] for e in a_entries])}
    ])

    summary_b = call_gpt([
        {"role": "system", "content": "Give a short helpful note to this debater on how they communicated, what they did well, and what to improve."},
        {"role": "user", "content": "\n\n".join([e['polished'] for e in b_entries])}
    ])

    st.markdown(f"**{st.session_state.user_a_name}'s Wrap-Up:**\n{summary_a}")
    st.markdown(f"**{st.session_state.user_b_name}'s Wrap-Up:**\n{summary_b}")

    if st.button("👑 Ask AI who won (just for fun)"):
        verdict = call_gpt([
            {"role": "system", "content": "You are a judge. Pick the more correct or convincing debater based on their messages."},
            {"role": "user", "content": "\n\n".join([f"{e['user']}: {e['polished']}" for e in st.session_state.fight_history])}
        ])
        st.success(f"🏁 Verdict: {verdict}")

    if st.button("🔄 Start Over"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# Main control flow
if st.session_state.stage == "goal_select":
    show_goal_selection()
elif st.session_state.stage == "debate_setup":
    show_debate_setup()
elif st.session_state.stage == "proposition_suggestion":
    show_proposition_suggestion()
elif st.session_state.stage == "handoff_to_a" or st.session_state.stage == "handoff":
    show_handoff()
elif st.session_state.stage == "user_a_justify" or st.session_state.stage == "user_b_justify":
    show_justification()
elif st.session_state.stage == "user_a_feedback" or st.session_state.stage == "user_b_feedback":
    show_feedback()
elif st.session_state.stage == "summary":
    show_summary()
elif st.session_state.stage == "wrap_up":
    show_wrap_up()
