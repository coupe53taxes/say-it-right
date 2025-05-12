# Interactive Streamlit App: Context-Aware Communication Assistant
import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Session state setup
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
if "user_A_position" not in st.session_state:
    st.session_state.user_A_position = ""
if "user_B_position" not in st.session_state:
    st.session_state.user_B_position = ""
if "debate_proposition" not in st.session_state:
    st.session_state.debate_proposition = ""

# GPT call helper
def call_gpt(messages):
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=messages)
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

st.set_page_config(page_title="Say It Right", page_icon="✉️")
st.title("Say It Right")
st.caption("Diffuse conflict. Preserve truth. Protect what matters.")

# Goal selection grid
if st.session_state.stage == "goal_select":
    st.subheader("What best describes your situation?")
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
    st.subheader("Set Up Your Debate")
    st.session_state.debate_topic = st.text_input("What is the topic of the debate?", st.session_state.debate_topic)
    st.session_state.user_A_name = st.text_input("User A's Name:", st.session_state.user_A_name)
    st.session_state.user_A_position = st.text_area("User A's Position:", st.session_state.user_A_position)
    st.session_state.user_B_name = st.text_input("User B's Name:", st.session_state.user_B_name)
    st.session_state.user_B_position = st.text_area("User B's Position:", st.session_state.user_B_position)
    if st.button("Next: Propose Shared Proposition"):
        st.session_state.stage = "debate_proposition"
        st.rerun()

# Proposition Agreement
elif st.session_state.stage == "debate_proposition":
    st.subheader("Agree on a Shared Proposition")
    if not st.session_state.debate_proposition:
        prompt = [
            {"role": "system", "content": "You help formulate debate propositions."},
            {"role": "user", "content": f"Debate topic: {st.session_state.debate_topic}\n\n{st.session_state.user_A_name}: {st.session_state.user_A_position}\n{st.session_state.user_B_name}: {st.session_state.user_B_position}"}
        ]
        st.session_state.debate_proposition = call_gpt(prompt)
    st.markdown("Suggested proposition:")
    st.session_state.debate_proposition = st.text_area("Edit if needed:", st.session_state.debate_proposition)
    if st.button("Agree and Start Debate"):
        st.session_state.fight_stage = "user_a_argument"
        st.session_state.stage = "pass_to_a"
        st.rerun()

# Intermediary screen: Pass to A
elif st.session_state.stage == "pass_to_a":
    st.header("Pass to First Debater")
    st.markdown(f"Pass the device to **{st.session_state.user_A_name}**. Click below when ready.")
    if st.button(f"I'm {st.session_state.user_A_name}, Continue"):
        st.session_state.stage = "user_argument"
        st.session_state.current_user = "A"
        st.rerun()

# Intermediary screen: Pass to B
elif st.session_state.stage == "pass_to_b":
    st.header("Pass to Next Debater")
    st.markdown(f"Pass the device to **{st.session_state.user_B_name}**. Click below when ready.")
    if st.button(f"I'm {st.session_state.user_B_name}, Continue"):
        st.session_state.stage = "user_argument"
        st.session_state.current_user = "B"
        st.rerun()

# Argument entry
elif st.session_state.stage == "user_argument":
    current = st.session_state.current_user
    name = st.session_state.user_A_name if current == "A" else st.session_state.user_B_name
    st.subheader(f"🗣️ {name}: Justify Your Position")
    user_text = st.text_area("Share why you believe your position is right:")
    if st.button("Get Feedback"):
        st.session_state.fight_history.append({"user": name, "content": user_text})
        st.session_state.stage = "feedback"
        st.rerun()

# Feedback and polish
elif st.session_state.stage == "feedback":
    current = st.session_state.current_user
    name = st.session_state.user_A_name if current == "A" else st.session_state.user_B_name
    opponent = st.session_state.user_B_name if current == "A" else st.session_state.user_A_name
    latest = st.session_state.fight_history[-1]["content"]
    prompt = [
        {"role": "system", "content": f"You help users improve arguments. Provide max 2-sentence fact check (if needed), max 2-sentence steelman of {opponent}, and 1 sentence persuasive rewrite. Then isolate suggested response only."},
        {"role": "user", "content": latest}
    ]
    result = call_gpt(prompt)
    try:
        fact, steel, polished = result.split("\n\n")
    except:
        fact = ""
        steel = ""
        polished = result
    st.subheader("Feedback")
    st.markdown(f"1. {fact}")
    st.markdown(f"2. {steel}")
    st.markdown(f"3. Response: {polished}")
    st.subheader("Your Improved Response")
    revised = st.text_area("Edit before submitting:", polished)
    if st.button("Submit and Pass"):
        st.session_state.fight_history[-1]["polished"] = revised
        st.session_state.stage = "pass_to_b" if current == "A" else "pass_to_a"
        st.session_state.current_user = "B" if current == "A" else "A"
        st.rerun()

# End debate screen
elif st.session_state.stage == "end_debate":
    st.subheader("Debate Summary")
    history = "\n\n".join([f"**{entry['user']}**: {entry['polished']}" for entry in st.session_state.fight_history if "polished" in entry])
    st.markdown(history)
    if st.button("🧠 Generate Final Analysis"):
        analysis = call_gpt([
            {"role": "system", "content": "Provide a fair, brief summary of this debate. Mention key arguments, tone, and insights each participant showed."},
            {"role": "user", "content": history}
        ])
        st.markdown(analysis)
    if st.button("🎉 Have AI Choose a Winner (for fun)"):
        verdict = call_gpt([
            {"role": "system", "content": "Based on the arguments, choose a winner (just for fun). Be clear and brief."},
            {"role": "user", "content": history}
        ])
        st.success(verdict)
    if st.button("🔄 Start Over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Offer to end debate after each pass
if st.session_state.stage in ["pass_to_a", "pass_to_b"]:
    if st.button("🏁 End Debate"):
        st.session_state.stage = "end_debate"
        st.rerun()
