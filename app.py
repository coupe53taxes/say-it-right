# Enhanced Streamlit MVP with Integrated Disagreement Detection

import streamlit as st
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Say It Right", page_icon="✉️")
st.title("Say It Right")
st.caption("Preserve relationships, defuse tensions, and discover clarity.")

# Select primary mode
mode = st.selectbox("Choose how you'd like to approach this:", ["Rephrase My Message", "Steelman Their Message"])

# User input based on mode
user_input = st.text_area("Type the message here:")

# Main function to interact with GPT-4o
def call_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You're a calm, insightful, conflict-mediating assistant skilled at reducing tension and clarifying real disagreements."},
                      {"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error from OpenAI API: {e}"

# Core prompt templates
prompt_templates = {
    "Rephrase My Message": "Rephrase this message in a calm, respectful, and charitable tone. Clarify ambiguity and reduce exaggeration:\n\n'{}'",
    "Steelman Their Message": "Interpret this statement charitably, in its strongest and most reasonable form:\n\n'{}'"
}

# Process the initial request
if st.button("Translate"):
    initial_prompt = prompt_templates[mode].format(user_input)
    revised_message = call_gpt(initial_prompt)
    
    st.subheader("Here's a better way to say it:")
    st.write(revised_message)

    # Optional follow-up: Detect real disagreement
    follow_up_prompt = (
        "Given the original message and the improved version, briefly explain the real underlying disagreement or issue. "
        "Be clear, neutral, and insightful.\n\n"
        f"Original message: '{user_input}'\n"
        f"Improved version: '{revised_message}'"
    )

    disagreement_insight = call_gpt(follow_up_prompt)

    st.subheader("💡 Insight: The Real Disagreement")
    st.write(disagreement_insight)

    st.info("Knowing where the real disagreement lies can make conversations more meaningful and less stressful.")

    # Optional advanced step: further clarify disagreement
    if st.button("Explore this disagreement deeper"):
        deeper_prompt = (
            "Offer advice on how to respectfully explore and resolve this specific type of disagreement:\n\n"
            f"Disagreement: '{disagreement_insight}'"
        )
        deeper_advice = call_gpt(deeper_prompt)

        st.subheader("🚦 How to Navigate this Disagreement")
        st.write(deeper_advice)
        st.success("You’re now equipped to handle this conversation with greater clarity and confidence.")
