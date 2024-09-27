import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def write_ids_to_js(image_ids):
    """Writes the image IDs to a JavaScript file."""
    js_content = f"const imageIds = {json.dumps(image_ids, indent=2)};"
    with open("imageIds.js", "w") as js_file:
        js_file.write(js_content)
    print("Image IDs have been written to imageIds.js")

def main():
    """Retrieves and prints the IDs of image files in Google Drive."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("drive", "v3", credentials=creds)

        # Call the Drive v3 API to search for image files
        results = service.files().list(
            q="mimeType contains 'image/'",
            spaces='drive',
            pageSize=200,  # Adjust this value to retrieve more or fewer results
            fields="nextPageToken, files(id, name)"
        ).execute()
        items = results.get("files", [])

        if not items:
            print("No image files found.")
            return
        print("Image files:")
        for item in items:
            print(f"{item['name']} = {item['id']}")
            image_ids = [item['id'] for item in items]
        
        print(f"\nTotal image files found: {len(items)}")

        write_ids_to_js(image_ids)
        
    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()