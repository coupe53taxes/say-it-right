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

# Session state initialization
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
if "debate_topic" not in st.session_state:
    st.session_state.debate_topic = ""
if "debate_positions" not in st.session_state:
    st.session_state.debate_positions = {}
if "debate_proposition" not in st.session_state:
    st.session_state.debate_proposition = ""

# GPT Call Helper
def call_gpt(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# Icon Grid for selecting conversation goal
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

# Debate setup
elif st.session_state.stage == "debate_setup":
    st.subheader("Set Up Your Debate")
    st.session_state.debate_topic = st.text_input("Debate Topic:", value=st.session_state.debate_topic)
    st.session_state.user_a_name = st.text_input("Name of User A:", value=st.session_state.user_a_name)
    position_a = st.text_area("User A's Position:")
    st.session_state.user_b_name = st.text_input("Name of User B:", value=st.session_state.user_b_name)
    position_b = st.text_area("User B's Position:")

    if st.button("Next: Frame the Debate"):
        st.session_state.debate_positions = {
            st.session_state.user_a_name: position_a,
            st.session_state.user_b_name: position_b
        }
        st.session_state.stage = "proposition_review"
        st.rerun()

# Proposition Review
elif st.session_state.stage == "proposition_review":
    st.subheader("Agree on the Proposition")
    summary_prompt = [
        {"role": "system", "content": "You are a moderator. Based on the topic and two users' positions, craft a debate proposition that captures the core point of disagreement."},
        {"role": "user", "content": f"Topic: {st.session_state.debate_topic}\n{st.session_state.user_a_name}: {st.session_state.debate_positions[st.session_state.user_a_name]}\n{st.session_state.user_b_name}: {st.session_state.debate_positions[st.session_state.user_b_name]}"}
    ]
    proposition = call_gpt(summary_prompt)
    st.session_state.debate_proposition = st.text_area("Suggested Proposition:", value=proposition)

    if st.button("Proceed to Debate"):
        st.session_state.stage = "handoff_to_user_a"
        st.rerun()

# Intermediary screen before each user's turn
elif st.session_state.stage == "handoff_to_user_a":
    st.subheader(f"Pass the device to {st.session_state.user_a_name}")
    if st.button("I'm {0}, ready to continue".format(st.session_state.user_a_name)):
        st.session_state.current_user = "A"
        st.session_state.fight_stage = "justify"
        st.session_state.stage = "debate_turn"
        st.rerun()

elif st.session_state.stage == "handoff_to_user_b":
    st.subheader(f"Pass the device to {st.session_state.user_b_name}")
    if st.button("I'm {0}, ready to continue".format(st.session_state.user_b_name)):
        st.session_state.current_user = "B"
        st.session_state.fight_stage = "justify"
        st.session_state.stage = "debate_turn"
        st.rerun()

# Debate Turn Logic
elif st.session_state.stage == "debate_turn":
    user = st.session_state.user_a_name if st.session_state.current_user == "A" else st.session_state.user_b_name
    opponent = st.session_state.user_b_name if st.session_state.current_user == "A" else st.session_state.user_a_name

    if st.session_state.fight_stage == "justify":
        st.subheader(f"{user}, why do you believe your position is correct?")
        user_input = st.text_area("Your Justification:")
        if st.button("Get Feedback"):
            st.session_state.fight_history.append({"user": user, "content": user_input})
            st.session_state.fight_stage = "feedback"
            st.rerun()

    elif st.session_state.fight_stage == "feedback":
        st.subheader("Persuasive Rewrite")

        history = st.session_state.fight_history[-1]["content"]
        guidance = call_gpt([
            {"role": "system", "content": f"You are helping {user} prepare a persuasive debate response. Provide a brief fact-check of their claim, then a steel-manning of {opponent}'s side, and finally a concise polished reply."},
            {"role": "user", "content": history}
        ])

        # Split out the polished part if possible
        polished_part = guidance.split("### Persuasive Rewrite")[-1].strip() if "### Persuasive Rewrite" in guidance else guidance

        st.markdown("#### Guidance:")
        st.markdown(guidance.split("### Persuasive Rewrite")[0])
        user_edit = st.text_area("Polished version of your argument:", value=polished_part)

        if st.button("Lock in and pass to other user"):
            st.session_state.fight_history[-1]["polished"] = user_edit
            st.session_state.stage = "handoff_to_user_b" if st.session_state.current_user == "A" else "handoff_to_user_a"
            st.rerun()

# Sidebar: Debate Summary
with st.sidebar:
    st.header("Debate Tools")
    if st.button("🧭 View Debate Summary") and st.session_state.fight_history:
        history = "\n\n".join([
            f"{entry['user']}: {entry['polished']}"
            for entry in st.session_state.fight_history if 'polished' in entry
        ])
        summary = call_gpt([
            {"role": "system", "content": "Provide a neutral summary of the public portions of the debate."},
            {"role": "user", "content": history}
        ])
        st.markdown(summary)

    if st.button("🏁 End Debate"):
        st.session_state.stage = "debate_end"
        st.rerun()

# End of debate feedback
if st.session_state.stage == "debate_end":
    st.subheader("Debate Summary & Reflections")
    public_history = "\n\n".join([
        f"{entry['user']}: {entry['polished']}"
        for entry in st.session_state.fight_history if 'polished' in entry
    ])
    reflection_prompt = [
        {"role": "system", "content": "You're a debate coach. Summarize the public debate, and then provide one short, personalized tip for each user based on their contributions."},
        {"role": "user", "content": public_history}
    ]
    reflection = call_gpt(reflection_prompt)
    st.markdown(reflection)

    if st.button("🎓 Declare a Winner (for fun)"):
        verdict = call_gpt([
            {"role": "system", "content": "Act as a playful debate judge. Based only on public arguments, who made the stronger case? Keep it light."},
            {"role": "user", "content": public_history}
        ])
        st.success(verdict)

    if st.button("🔁 Restart"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.stage = "goal_select"
        st.rerun()

st.caption("All feedback remains confidential. Your opponent can't see your inputs or the feedback you receive.")
