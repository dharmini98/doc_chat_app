from tempfile import NamedTemporaryFile
import streamlit as st
from langchain.agents import create_csv_agent
from langchain.llms import OpenAI
from dotenv import load_dotenv
from utils import json_csv
import os

def main():
    load_dotenv()

    st.set_page_config(page_title="Ask your CSV")
    st.header("Ask your CSV")
 
    user_file = st.file_uploader("Upload your csv file")

    if user_file is not None and user_file.name.endswith(".csv"):
        with NamedTemporaryFile() as f: # Create temporary file
            f.write(user_file.getvalue()) # Save uploaded contents to file
            f.flush()
            llm=OpenAI(temperature=0)
            user_question = st.text_input("Ask a question to your csv:")
            agent=create_csv_agent(llm, f.name, verbose=True, max_execution_time=1, early_stopping_method="generate")

        if user_question is not None and user_question != "":
            response = agent.run(user_question)

            st.write(response)

    elif user_file is not None and user_file.name.endswith(".json"):
        json_csv(user_file.getvalue().decode('utf-8')) #converting the json file to csv for the csv agent

        llm=OpenAI(temperature=0)
        user_question = st.text_input("Ask a question to your json:")
        agent=create_csv_agent(llm, "data_files/ready_to_use.csv", verbose=True, max_execution_time=1, early_stopping_method="generate")

        if user_question is not None and user_question != "":
            response = agent.run(user_question)

            st.write(response)

if __name__ == "__main__":
    main()
