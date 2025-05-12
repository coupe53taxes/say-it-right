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
if "user_A_name" not in st.session_state:
    st.session_state.user_A_name = "User A"
if "user_B_name" not in st.session_state:
    st.session_state.user_B_name = "User B"
if "debate_topic" not in st.session_state:
    st.session_state.debate_topic = ""
if "proposition" not in st.session_state:
    st.session_state.proposition = ""
if "user_goal" not in st.session_state:
    st.session_state.user_goal = ""
if "dialogue" not in st.session_state:
    st.session_state.dialogue = []

# GPT helper
def call_gpt(messages):
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=messages)
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# UI flow
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

elif st.session_state.stage == "debate_setup":
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

elif st.session_state.stage == "proposition_confirm":
    st.subheader("Suggested Proposition")
    st.markdown("### Based on what you wrote, here's a focused proposition to debate:")
    st.session_state.proposition = st.text_area("Proposition", value=st.session_state.proposition)

    if st.button("Start Debate with this Proposition"):
        st.session_state.stage = "handoff_to_A"
        st.rerun()

elif st.session_state.stage == "handoff_to_A":
    st.subheader("Pass to First Debater")
    st.write(f"Pass the device to **{st.session_state.user_A_name}**. Click below when ready.")
    if st.button("I'm {st.session_state.user_A_name}, Continue"):
        st.session_state.fight_stage = "user_input"
        st.session_state.current_user = st.session_state.user_A_name
        st.rerun()

elif st.session_state.stage == "handoff_to_B":
    st.subheader("Pass to Second Debater")
    st.write(f"Pass the device to **{st.session_state.user_B_name}**. Click below when ready.")
    if st.button("I'm {st.session_state.user_B_name}, Continue"):
        st.session_state.fight_stage = "user_input"
        st.session_state.current_user = st.session_state.user_B_name
        st.rerun()

elif st.session_state.fight_stage == "user_input":
    user = st.session_state.current_user
    st.subheader(f"{user}, Justify Your Position")
    argument = st.text_area("Briefly explain why you hold your view on the proposition.")
    if st.button("Get Feedback and Refine"):
        st.session_state.fight_history.append({"user": user, "content": argument})
        st.session_state.fight_stage = "user_feedback"
        st.rerun()

elif st.session_state.fight_stage == "user_feedback":
    user = st.session_state.current_user
    opponent = st.session_state.user_B_name if user == st.session_state.user_A_name else st.session_state.user_A_name
    user_input = st.session_state.fight_history[-1]["content"]

    prompt = [
        {"role": "system", "content": f"You're a constructive debate coach. Provide 1-sentence fact-check (if needed), a 1-sentence steel-man of {opponent}'s likely position, and a single concise, tactful response {user} might send. Label each."},
        {"role": "user", "content": user_input}
    ]
    analysis = call_gpt(prompt)

    st.subheader("Private Feedback")
    st.markdown(analysis)

    polished = analysis.split("Polished Reply:")[-1].strip()
    final = st.text_area("Edit before sending:", value=polished, height=100)

    if st.button("Lock in and pass to other user"):
        st.session_state.fight_history[-1]["polished"] = final
        if user == st.session_state.user_A_name:
            st.session_state.current_user = st.session_state.user_B_name
            st.session_state.stage = "handoff_to_B"
        else:
            st.session_state.current_user = st.session_state.user_A_name
            st.session_state.stage = "handoff_to_A"
        st.session_state.fight_stage = None
        st.rerun()

# Summary, exit, etc.
if st.session_state.fight_history and st.session_state.stage.startswith("handoff"):
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
