from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1E6W1Y4_jZclw351nrqKzJerIkIDekUIieY_7GMG6pRM'
SAMPLE_RANGE_NAME = 'TourneyTotals!A2:E'


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        sheet_metadata = sheet.get(spreadsheetId=SAMPLE_SPREADSHEET_ID).execute()
        sheet_metadata = sheet_metadata.get('sheets', '')
        
        sheet_ids = range(1, 13)
        titles = []
        dfs = []
        for index in sheet_ids:
            title = sheet_metadata[index].get("properties", {}).get("title", "Sheet1")
            # print("title: ")
            # print(title)
            titles.append(title)
            # sheet_id = sheet_metadata[index].get("properties", {}).get("sheetId", index)
            # print("sheet_id: ")
            # print(sheet_id)
            result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=f'{title}').execute()
            # Maybe batch this later
            # result = service.spreadsheets().values().batchGet(spreadsheetId=SPREADSHEET_ID, ranges=ranges).execute()
            df = pd.DataFrame(
                result.get('values', []), 
                columns=[
                    "Players", 
                    "GP", 
                    "KILLS", 
                    "DEATHS", 
                    "KDR", 
                    "DMG DEALT", 
                    "DMG TAKEN", 
                    "NET +/-",
                    "HITS",
                    "FIRED",
                    "ACC",
                    "HITS",
                    "FIRED",
                    "ACC",
                    "HITS",
                    "FIRED",
                    "ACC",
                    "HITS",
                    "FIRED",
                    "ACC",
                    "HITS",
                    "FIRED",
                    "ACC",
                    "HITS",
                    "FIRED",
                    "ACC",
                    "HITS",
                    "FIRED",
                    "ACC",
                    "HITS",
                    "FIRED",
                    "ACC"
                ]
            )
            # print('df: ')
            # print(df)
            dfs.append(df)
            
        if not dfs:
            print('No data found.')
            return
        
        return dfs

    except HttpError as err:
        print(err)

if __name__ == '__main__':
    main()