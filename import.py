import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
FOLDER_NAME = "BUENA"  # Replace with your folder name

def write_ids_to_js(image_ids):
    """Writes the image IDs to a JavaScript file."""
    js_content = f"const imageIds = {json.dumps(image_ids, indent=2)};"
    with open("imageIds.js", "w") as js_file:
        js_file.write(js_content)
    print(f"Image IDs have been written to imageIds.js")

def get_drive_service():
    """Authenticates and returns the Google Drive service."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("drive", "v3", credentials=creds)

def get_folder_id(service, folder_name):
    """Retrieves the ID of the specified folder."""
    try:
        results = service.files().list(
            q=f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false",
            spaces='drive',
            fields="files(id, name)"
        ).execute()
        folders = results.get('files', [])
        
        if not folders:
            print(f"Folder '{folder_name}' not found.")
            return None
        
        return folders[0]['id']
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def get_image_ids(service, folder_id):
    """Retrieves image file IDs from the specified folder in Google Drive."""
    try:
        results = service.files().list(
            q=f"'{folder_id}' in parents and mimeType contains 'image/' and trashed=false",
            spaces='drive',
            pageSize=160,  # Adjust this value as needed
            fields="nextPageToken, files(id, name)"
        ).execute()
        items = results.get("files", [])
        
        if not items:
            print("No image files found in the specified folder.")
            return []
        
        image_ids = [item['id'] for item in items]
        print(f"Total image files found in the folder: {len(image_ids)}")
        return image_ids
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

def main():
    """Retrieves image IDs from the specified folder and writes them to a JS file."""
    service = get_drive_service()
    folder_id = get_folder_id(service, FOLDER_NAME)
    
    if not folder_id:
        print(f"Cannot proceed without a valid folder ID for '{FOLDER_NAME}'.")
        return

    image_ids = get_image_ids(service, folder_id)
    write_ids_to_js(image_ids)

if __name__ == "__main__":
    main()