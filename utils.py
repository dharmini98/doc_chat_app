import json
import pandas as pd
from pandas import json_normalize
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os 

Connection_String_to_blob = os.environ.get('Connection_String_to_blob')

def get_blob_service_client():
    connection_string = Connection_String_to_blob
    return BlobServiceClient.from_connection_string(connection_string)

def upload_to_blob_storage(file_path, filename):
    blob_service_client = get_blob_service_client()
    container_name = 'peearzchatdocupload'  # Create a container in your Blob storage account

    # Get a blob client
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)

    # Upload the file to Blob storage
    with open(file_path, 'rb') as data:
        blob_client.upload_blob(data, overwrite=True)

def json_csv(path_to_store, file):

    dictionary = json.loads(file)

    df = None
    first = True

    for document in dictionary:
        if document == None:
            continue
        else:
            dfLeft = json_normalize(document)

        for title, value in document.items():
            if type(value) == list:
                dfLeft.drop(title, axis="columns", inplace=True)
                dfRight = json_normalize(value)
                dfRight = dfRight.add_prefix(f"{title}_")
                dfLeft = pd.concat([dfLeft, dfRight], axis = 1)    

        if first:
            df = dfLeft
            first = False
        else:
            df = pd.concat([df, dfLeft], axis = 0)

    df.reset_index(inplace=True, drop=True)

    df1 = df.T.drop_duplicates().T

    df1.to_csv('test.csv')
