import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="Spatial Narratives",
    # page_icon=":orange_heart:",
)
st.markdown("## Spatial Narratives Project")
st.markdown("#### Analysing the Lake District Writing and Holocaust Testimonies")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

models = {"llama3-8b-8192": "llama3-8b-8192", "llama3-70b-8192": "llama3-70b-8192", 
          "llama-3.1-70b-versatile": "llama-3.1-70b-versatile", "gemma2-9b-it": "gemma2-9b-it", 
          "llama-3.1-8b-instant": "llama-3.1-8b-instant", "gemma-7b-it": "gemma-7b-it", 
          "mixtral-8x7b-32768": "mixtral-8x7b-32768"}


def main() -> None:

    # Get model
    llm_model = st.sidebar.selectbox(
        "Select Model", options= models.values() #["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"]
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

    def display_input_row(index):
        left, middle, right = st.columns(3)
        left.text_input('First', key=f'first_{index}')
        middle.text_input('Middle', key=f'middle_{index}')
        right.text_input('Last', key=f'last_{index}')

    if 'rows' not in st.session_state:
        st.session_state['rows'] = 0

    def increase_rows():
        st.session_state['rows'] += 1

    st.button('Add person', on_click=increase_rows)

    for i in range(st.session_state['rows']):
        display_input_row(i)

    # Show the results
    st.subheader('People')
    for i in range(st.session_state['rows']):
        st.write(
            f'Person {i+1}:',
            st.session_state[f'first_{i}'],
            st.session_state[f'middle_{i}'],
            st.session_state[f'last_{i}']
        )

main()