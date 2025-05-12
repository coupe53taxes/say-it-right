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
    st.markdown("Pass the device to the first debater. Click below when you're ready.")
    if st.button(f"I'm {st.session_state.user_A_name}, Continue"):
        st.session_state.current_user = st.session_state.user_A_name
        st.session_state.stage = "private_feedback"
        st.rerun()

# Handoff to Second User
elif st.session_state.stage == "pass_to_second_user":
    st.header("Pass to Second Debater")
    st.markdown("Pass the device to the second debater. Click below when you're ready.")
    if st.button(f"I'm {st.session_state.user_B_name}, Continue"):
        st.session_state.current_user = st.session_state.user_B_name
        st.session_state.stage = "private_feedback"
        st.rerun()

# Private Feedback Stage
elif st.session_state.stage == "private_feedback":
    user = st.session_state.current_user
    opponent = st.session_state.user_B_name if user == st.session_state.user_A_name else st.session_state.user_A_name

    st.subheader(f"{user}, briefly explain why you believe your view is correct:")
    argument = st.text_area("Your Justification:")

    if st.button("Get Guidance"):
        st.session_state.fight_history.append({"user": user, "content": argument})

        prompt = [
            {"role": "system", "content": f"You're a concise, fair debate coach. Return three labeled items:\n1. One-sentence fact check if needed.\n2. One-sentence steelman of {opponent}'s likely view.\n3. One short, tactful response the user could use. Label each clearly."},
            {"role": "user", "content": argument}
        ]
        feedback = call_gpt(prompt)
        polished = feedback.split("Polished Reply:")[-1].strip()

        st.markdown("---")
        st.markdown("### Feedback")
        st.markdown(feedback.split("Polished Reply:")[0].strip())

        st.markdown("---")
        st.subheader("Your Improved Response")
        final = st.text_area("Edit before submitting:", value=polished, height=100)

        if st.button("Submit and Pass"):
            st.session_state.fight_history[-1]["polished"] = final
            if user == st.session_state.user_A_name:
                st.session_state.current_user = st.session_state.user_B_name
                st.session_state.stage = "pass_to_second_user"
            else:
                st.session_state.current_user = st.session_state.user_A_name
                st.session_state.stage = "pass_to_first_user"
            st.rerun()

# Sidebar Tools
if st.session_state.stage.startswith("pass_to"):
    with st.sidebar:
        st.header("Debate Tools")

        if st.button("🧾 View Debate Summary"):
            history = "\n\n".join([f"{entry['user']}: {entry['polished']}" for entry in st.session_state.fight_history if 'polished' in entry])
            summary = call_gpt([
                {"role": "system", "content": "Provide a brief, fair summary of the debate's progress and any areas of agreement or disagreement."},
                {"role": "user", "content": history}
            ])
            st.markdown(summary)

        if st.button("🏁 End Debate"):
            st.session_state.stage = "wrap_up"
            st.rerun()

# Wrap-Up Phase
elif st.session_state.stage == "wrap_up":
    st.subheader("Debate Wrap-Up")
    history = "\n\n".join([f"{entry['user']}: {entry['polished']}" for entry in st.session_state.fight_history if 'polished' in entry])

    summary = call_gpt([
        {"role": "system", "content": "Offer a thoughtful wrap-up of the debate with individual suggestions for each participant."},
        {"role": "user", "content": history}
    ])
    st.markdown(summary)

    if st.button("🤖 Let AI pick a winner (just for fun)"):
        verdict = call_gpt([
            {"role": "system", "content": "Based on the arguments shared, pick the side that made the stronger case. Be fair but brief."},
            {"role": "user", "content": history}
        ])
        st.success(verdict)

    if st.button("🔄 Restart"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
