import pickle

import tqdm
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import csv
import io


def authenticate_google_drive():
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    creds = None

    # The file token.pickle stores the user's access and refresh tokens and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('res/token.pickle'):
        with open('res/token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'res/credentials.json', SCOPES)  # credentials.json is the downloaded JSON file
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('res/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)


service = authenticate_google_drive()


# Function to download a file from Google Drive
def download_file_from_google_drive(file_id, file_name):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()


def download():
    # Process the CSV
    input_csv = 'data.csv'  # Replace with your CSV file name
    output_csv = 'paths.csv'

    with open(input_csv, newline='', encoding='utf-8') as csvfile, \
            open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        errors = []

        for row in tqdm.tqdm(reader, total=144):
            try:
                file_url = row['URL']
                file_id = file_url.split('https://drive.google.com/file/d/')[1]
                file_id = file_id.split('/')[0].split('?')[0]
                file_name = os.path.join('res/files', f'{file_id}.pdf')  # or any other file format
                os.makedirs(os.path.dirname(file_name), exist_ok=True)

                if not os.path.exists(file_name):
                    download_file_from_google_drive(file_id, file_name)

                row['URL'] = file_name  # Replace URL with local file path

                writer.writerow(row)
            except Exception as e:
                errors.append((file_url, file_name))

        for url, name in errors:
            os.remove(name)

        print("\n".join([e[0] for e in errors]))


if __name__ == '__main__':
    download()
