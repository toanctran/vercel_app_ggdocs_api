
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
from pydantic import BaseModel
from typing import List
from fastapi import FastAPI, HTTPException, Body, Query
import io
import json


# Create a service object to interact with the Drive API
SERVICE_ACCOUNT_JSON_PATH = json.loads(os.getenv("GOOGLE_SHEETS_JSON_KEY_CONTENTS"))

creds = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_JSON_PATH, scopes=['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents'])

# Create a Google Docs API, Drive API client
docs_service = build('docs', 'v1', credentials=creds)
drive_service = build('drive', 'v3', credentials=creds)
# Create a FastAPI app
app = FastAPI()
@app.get("/")
async def root():
  return{"message":"Created by Tran Chi Toan - chitoantran@gmail.com"}


# Define the Pydantic model for request body
class CreateGoogleDocRequest(BaseModel):
    content: str
    parent_folder_id: str
    title: str

# Define a function to create a Google Docs document with content
def create_google_doc_with_content(content, parent_folder_id, title):
    document = {
        'title': title
    }
    doc = docs_service.documents().create(body=document).execute()
    document_id = doc['documentId']

    # Insert content into the document
    requests = [
        {
            'insertText': {
                'location': {
                    'index': 1,  # Insert at the beginning of the document
                },
                'text': content,
            }
        }
    ]
    docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

    # Move the document to the specified folder
    
    drive_service.files().update(fileId=document_id, addParents=parent_folder_id).execute()

    return f"https://docs.google.com/document/d/{document_id}"

# Define a route to create a Google Docs document with content
@app.post("/create_google_doc_with_content")
async def create_google_doc_with_content_route(request: CreateGoogleDocRequest):
    content = request.content
    parent_folder_id = request.parent_folder_id
    title = request.title
    doc_link = create_google_doc_with_content(content, parent_folder_id, title)
    return {"google_doc_link": doc_link}

