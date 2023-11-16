import os
import sys
from tempfile import NamedTemporaryFile
from flask import Flask, request, render_template
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from langchain.llms import OpenAI
from langchain.agents import create_csv_agent
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from utils import json_csv
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase 
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
import pyodbc
import pandas as pd
#test commit
load_dotenv()

app=Flask(__name__)

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
AZURE_STORAGE_CONN_STRING = os.environ.get('AZURE_STORAGE_CONN_STRING') #azure database uri

openai = OpenAI(api_key=OPENAI_API_KEY)  
#blob_service = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONN_STRING)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'file_path/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def create():        #function to create sql agent, create_sql_agent
  #server = os.environ.get("AZURE_SQL_SERVER")
  #database = os.environ.get("AZURE_SQL_DB")
  #username = os.environ.get("AZURE_SQL_USER")
  #password = os.environ.get("AZURE_SQL_PASSWORD")
  server="tcp:peearz.database.windows.net"
  database="FuelData"
  username="peearzadmin"
  password="Peearz2023$$"
  conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
  conn=pyodbc.connect(conn_str)#specify odbc driver17
  db = SQLDatabase.from_uri(conn_str)

  llm = OpenAI(temperature=0)  #main component
  toolkit = SQLDatabaseToolkit(db=db,llm=llm)
  

  agent = create_sql_agent(   
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
  )

  return agent

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/predictdata', methods=['GET','POST'])
def predict_datapoint():
    if request.method=='GET':
        return render_template('home.html')
    else:
        if 'file' not in request.files:
            return "No File Part"
    
        user_file = request.files['file']
        
        if user_file:
                
            filename = secure_filename(user_file.filename)

            temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            user_file.save(temp_file_path)

            # Upload the file to Azure Blob storage
            #upload_to_blob_storage(temp_file_path, filename)

            if filename.endswith(".csv"):
    
                with NamedTemporaryFile() as f: # Create temporary file
                    f.write(user_file.getvalue()) # Save uploaded contents to file
                    f.flush()
                    llm = OpenAI(temperature=0)
                    user_question = request.form['query']
                    agent=create_csv_agent(llm, f.name, verbose=True,  early_stopping_method="generate")

                if user_question is not None and user_question != "":
                    response = agent.run(user_question)

            elif filename.endswith(".json"):
                json_csv(UPLOAD_FOLDER, user_file.getvalue().decode('utf-8')) #converting the json file to csv for the csv agent

                llm = OpenAI(temperature=0)


                user_question = request.form['query']

                agent=create_csv_agent(llm, 'test.csv', verbose=True, early_stopping_method="generate")

                if user_question is not None and user_question != "":
                    response = agent.run(user_question)

            # Remove the temporary file after uploading
            os.remove(temp_file_path)

        else:  #sql agent part
            agent=create()
            query=request.form['query']
            response=agent.run(query)
        
        agent.toolkit.database_connection.close() 
    return response
    
if __name__=="__main__":
    app.run(host="0.0.0.0", port="4999",debug=True)
