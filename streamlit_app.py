import os
import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="Spatial Narratives",
    # page_icon=":orange_heart:",
)
st.markdown("## Spatial Narratives Project")
st.markdown("#### Analysing the Lake District Writing and Holocaust Testimonies")

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def main() -> None:
    # Get model
    llm_model = st.sidebar.selectbox(
        "Select Model", options=["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"]
    )

    example_file = st.sidebar.selectbox(
        "Select example text", options=['ht_268_excerpt.txt', "cldw_66_1857_excerpt.txt"]
    )

    # Set assistant_type in session state
    if "llm_model" not in st.session_state:
        st.session_state["llm_model"] = llm_model
    # Restart the assistant if assistant_type has changed
    elif st.session_state["llm_model"] != llm_model:
        st.session_state["llm_model"] = llm_model
        st.rerun()

    # Set example text in session state
    if "example_file" not in st.session_state:
        st.session_state["example_file"] = example_file
    # Restart the assistant if assistant_type has changed
    elif st.session_state["example_file"] != example_file:
        st.session_state["example_file"] = example_file
        st.rerun()

    # Get topic for report
    context = st.text_area("Text to analyze (You can copy and paste your text)",
                           placeholder='Give a context here', 
                           value=open(example_file).read().replace('\n',' ').replace('  ',' '))

    prompt = st.text_input(":thinking_face: Give your instruction",
        value="Identify the emotion (fear, sadness, anger, joy or neutral) expressed in this text",
    )

    # Button to generate report
    generate_response = st.button("Generate response")
    if generate_response:
        # st.session_state["topic"] = f"{prompt}: '{context}'"
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user", "content": f"{prompt}: '{context}'. Focus ONLY on the given text.",
                }
            ],
            model=llm_model,
        )
        st.markdown(chat_completion.choices[0].message.content)

main()
