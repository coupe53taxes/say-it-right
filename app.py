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
if "user_A_position" not in st.session_state:
    st.session_state.user_A_position = ""
if "user_B_position" not in st.session_state:
    st.session_state.user_B_position = ""
if "debate_proposition" not in st.session_state:
    st.session_state.debate_proposition = ""

st.set_page_config(page_title="Say It Right", page_icon="✉️")
st.title("Say It Right")
st.caption("Diffuse conflict. Preserve truth. Protect what matters.")

def call_gpt(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# Icon Grid – Starting Screen
if st.session_state.stage == "goal_select":
    st.subheader("What best describes your situation?")
    cols = st.columns(2)
    if cols[0].button("🥊 Debate Productively"):
        st.session_state.stage = "debate_setup"
        st.rerun()
    cols[1].button("🧯 Cool things down (Coming soon)", disabled=True)
    cols[0].button("🧠 Make my case—no fight (Coming soon)", disabled=True)
    cols[1].button("📱 Online heated (Coming soon)", disabled=True)
    cols[0].button("❤️ It's personal (Coming soon)", disabled=True)
    cols[1].button("😤 I need to vent (Coming soon)", disabled=True)

# Debate Setup Flow
elif st.session_state.stage == "debate_setup":
    st.header("Set Up Your Debate")
    st.session_state.debate_topic = st.text_input("Debate Topic:", st.session_state.debate_topic)
    st.session_state.user_A_name = st.text_input("Name of User A:", st.session_state.user_A_name)
    st.session_state.user_A_position = st.text_area(f"{st.session_state.user_A_name}'s Position:", st.session_state.user_A_position)
    st.session_state.user_B_name = st.text_input("Name of User B:", st.session_state.user_B_name)
    st.session_state.user_B_position = st.text_area(f"{st.session_state.user_B_name}'s Position:", st.session_state.user_B_position)

    if st.button("Next: Propose Debate Wording"):
        st.session_state.stage = "proposition_draft"
        st.rerun()

# Proposition Refinement Page
elif st.session_state.stage == "proposition_draft":
    st.header("Draft the Debate Proposition")
    proposed = call_gpt([
        {"role": "system", "content": "Draft a neutral and clear debate proposition based on two opposing positions."},
        {"role": "user", "content": f"Topic: {st.session_state.debate_topic}\nA: {st.session_state.user_A_position}\nB: {st.session_state.user_B_position}"}
    ])
    st.markdown("Suggested Proposition:")
    st.session_state.debate_proposition = st.text_area("Proposition", value=proposed, height=100)

    if st.button("Looks Good, Begin Debate"):
        st.session_state.stage = "pass_to_A"
        st.rerun()

# Intermediary Pass to User A
elif st.session_state.stage == "pass_to_A":
    st.header("Pass to First Debater")
    st.markdown(f"Pass the device to **{st.session_state.user_A_name}**. Click below when ready.")
    if st.button(f"I'm {st.session_state.user_A_name}, Continue"):
        st.session_state.stage = "user_A_input"
        st.session_state.current_user = "A"
        st.rerun()

# User A Input
elif st.session_state.stage == "user_A_input":
    st.subheader(f"🗣️ {st.session_state.user_A_name}, make your case")
    st.markdown(f"Debate Proposition: *{st.session_state.debate_proposition}*")
    a_input = st.text_area("Why do you support your position?")
    if st.button("Submit and Get Feedback"):
        st.session_state.fight_history.append({"user": st.session_state.user_A_name, "content": a_input})
        st.session_state.stage = "feedback_A"
        st.rerun()

# Feedback for User A
elif st.session_state.stage == "feedback_A":
    last_input = st.session_state.fight_history[-1]["content"]
    steelman = call_gpt([
        {"role": "system", "content": "Steelman the opposing viewpoint for clarity."},
        {"role": "user", "content": st.session_state.user_B_position}
    ])
    rewrite = call_gpt([
        {"role": "system", "content": "Rewrite the user's argument clearly and persuasively."},
        {"role": "user", "content": last_input}
    ])
    st.subheader("Feedback")
    st.markdown(f"**Steelmanning {st.session_state.user_B_name}'s Side:** {steelman}")
    st.subheader("Your Improved Response")
    final_a = st.text_area("Edit before submitting:", value=rewrite)
    if st.button("Lock in and pass to other user"):
        st.session_state.fight_history[-1]["polished"] = final_a
        st.session_state.stage = "pass_to_B"
        st.rerun()

# Intermediary Pass to User B
elif st.session_state.stage == "pass_to_B":
    st.header("Pass to Second Debater")
    st.markdown(f"Pass the device to **{st.session_state.user_B_name}**. Click below when ready.")
    if st.button(f"I'm {st.session_state.user_B_name}, Continue"):
        st.session_state.stage = "user_B_input"
        st.session_state.current_user = "B"
        st.rerun()

# User B Input – sees what A submitted
elif st.session_state.stage == "user_B_input":
    st.subheader(f"🗣️ {st.session_state.user_B_name}, respond to your opponent")
    st.markdown(f"**{st.session_state.user_A_name}'s statement:**\n\n{st.session_state.fight_history[-1]['polished']}")
    b_input = st.text_area("What's your response?")
    if st.button("Submit and Get Feedback"):
        st.session_state.fight_history.append({"user": st.session_state.user_B_name, "content": b_input})
        st.session_state.stage = "feedback_B"
        st.rerun()

# Feedback for User B
elif st.session_state.stage == "feedback_B":
    last_input = st.session_state.fight_history[-1]["content"]
    steelman = call_gpt([
        {"role": "system", "content": "Steelman the opposing viewpoint for clarity."},
        {"role": "user", "content": st.session_state.user_A_position}
    ])
    rewrite = call_gpt([
        {"role": "system", "content": "Rewrite the user's argument clearly and persuasively."},
        {"role": "user", "content": last_input}
    ])
    st.subheader("Feedback")
    st.markdown(f"**Steelmanning {st.session_state.user_A_name}'s Side:** {steelman}")
    st.subheader("Your Improved Response")
    final_b = st.text_area("Edit before submitting:", value=rewrite)
    if st.button("Lock in and pass to other user"):
        st.session_state.fight_history[-1]["polished"] = final_b
        st.session_state.stage = "end_or_continue"
        st.rerun()

# Final options page
elif st.session_state.stage == "end_or_continue":
    st.header("Choose Next Step")
    st.markdown("Would you like to continue the debate or conclude?")
    if st.button("Continue Exchange"):
        next_user = "A" if st.session_state.current_user == "B" else "B"
        st.session_state.current_user = next_user
        st.session_state.stage = f"user_{next_user}_input"
        st.rerun()
    if st.button("End Debate and See Summary"):
        st.session_state.stage = "summary"
        st.rerun()

# Summary screen
elif st.session_state.stage == "summary":
    st.header("Debate Summary")
    public_history = [f"**{entry['user']}**: {entry['polished']}" for entry in st.session_state.fight_history if "polished" in entry]
    st.markdown("\n\n".join(public_history))

    if st.button("Have AI Declare a Winner (for fun)"):
        joined = "\n".join([f"{entry['user']}: {entry['polished']}" for entry in st.session_state.fight_history])
        verdict = call_gpt([
            {"role": "system", "content": "You are a neutral debate judge. Based on their arguments, declare who made the more persuasive case."},
            {"role": "user", "content": joined}
        ])
        st.subheader("🎖️ AI's Verdict")
        st.write(verdict)

    if st.button("🔄 Start New Debate"):
        for key in ["stage", "fight_stage", "fight_history", "current_user", "user_A_name", "user_B_name", "user_A_position", "user_B_position", "debate_topic", "debate_proposition"]:
            st.session_state.pop(key, None)
        st.rerun()
