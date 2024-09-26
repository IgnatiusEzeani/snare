import os
import pandas as pd
import streamlit as st
from groq import Groq
from analyzer import *
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
     page_title = "Spatio-Temporal Explorer",
     page_icon = "🌎", # 📍🗾🌏🌎🌐
     layout = "wide",
     initial_sidebar_state = "expanded",
     menu_items={
         'Get Help': "https://github.com/SpaceTimeNarratives",
         'Report a bug': "https://github.com/SpaceTimeNarratives",
         'About': '''## Understanding imprecise space and time in narratives through qualitative representations, reasoning, and visualisation'''
     }
 )

st.markdown("## SNARE 1.0")
st.markdown("#### Spatial Narratives Representation Environment")
st.markdown("###### Analysing the Lake District Writing and Holocaust Testimonies")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

models = {"llama3-8b-8192": "llama3-8b-8192", "llama3-70b-8192": "llama3-70b-8192", 
          "llama-3.1-70b-versatile": "llama-3.1-70b-versatile", "gemma2-9b-it": "gemma2-9b-it", 
          "llama-3.1-8b-instant": "llama-3.1-8b-instant", "gemma-7b-it": "gemma-7b-it", 
          "mixtral-8x7b-32768": "mixtral-8x7b-32768"}

example_ids = [('268', 'M'), ('36999','F'), ('37250','M'), ('37409','F')] # added gender information for later use

# file_formats = {"csv": pd.read_csv, "tsv": pd.read_csv, "xls": pd.read_excel, "xlsx": pd.read_excel, 
#                 "xlsm": pd.read_excel, "xlsb": pd.read_excel, "json": pd.read_json}

# @st.cache_data(ttl="2h")
# def load_data(uploaded_file):
#     try:
#         ext = os.path.splitext(uploaded_file.name)[1][1:].lower()
#     except:
#         ext = uploaded_file.split(".")[-1]
#     if ext in file_formats:
#         return file_formats[ext](uploaded_file) if ext!="json" else file_formats[ext](uploaded_file)
#     else:
#         st.error(f"Unsupported file format: {ext}")
#         return None

def main() -> None:
    option = st.sidebar.radio("What do you you want to do?", ["Spatial Data Analysis", "LLM Query-Prompting"], index=None)

    if option == "Spatial Data Analysis":
        # Add emotion selector
        all_emotions = ['sadness', 'anger', 'fear', 'anxiety', 'despair', 'joy', 'gratitude', 'surprise', 'neutral']
        selected_emotions = st.sidebar.multiselect("Select emotions", all_emotions, ["sadness", "anger", "fear", "joy"])

        # Add testimony id selector
        fileids = sorted([f.split('_')[0] for f in os.listdir("llm_emotion_scores") if f!="all_file_scores.tsv"])  # List of file IDs
        selected_fileids = st.sidebar.multiselect("Select Testimony ID", fileids, [id for id, _ in example_ids])

        # Include plot of combined scores in the plot?
        with_combined = st.sidebar.checkbox("Include plot of combined scores?", False)

        # # Include plot of combined scores for male survivors
        males = st.sidebar.checkbox("Include combined male scores?", False)

        # # Include plot of combined scores for male survivors
        females = st.sidebar.checkbox("Include combined female scores?", False)
        
        # Line or Barchart
        barchart = st.checkbox("Use Barchart?", False)

        err = plot_emotions(selected_emotions, selected_fileids, with_combined, barchart=barchart,
                            males=males, females=females)

        if err: st.error(err, icon="🚨")

    elif option == "LLM Query-Prompting":
        # Get model
        llm_model = st.sidebar.selectbox(
            "Select Model", options= models.values()
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
    else:
        pass

main()

# elif option == "Spatial AnalysisCorpora LLM Prompting":
#     pass
    # uploaded_files = st.file_uploader("Upload annotated testimony file(s)", accept_multiple_files=True)

    # for uploaded_file in uploaded_files:
    #     # bytes_data = uploaded_file.read()
    #     # st.write("filename:", uploaded_file.name)
    #     # st.write(bytes_data)
    
    #     # Read the Pandas DataFrame
    #     filedf = load_data(uploaded_file)
    #     st.dataframe(filedf.T)