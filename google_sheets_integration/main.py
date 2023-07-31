from __future__ import print_function

import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1Ltb4clF96MZ1WxaQ_YnHjy7jdaaLDntm5v9eLcH3k_A'
SAMPLE_RANGE_NAME = 'Workers!A1:AF50'


class GoogleSheet:
    SPREADSHEET_ID = SAMPLE_SPREADSHEET_ID
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    service = None

    def __init__(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print('flow')
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.path.join(os.getcwd(), 'google_sheets_integration', 'credentials.json'), self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('sheets', 'v4', credentials=creds)

    def appendToColumnA(self, new_username):
        range_to_update = 'A:A'
        data = {
            'range': range_to_update,
            'majorDimension': 'COLUMNS',
            'values': [[new_username]],
        }
        self.service.spreadsheets().values().append(spreadsheetId=self.SPREADSHEET_ID,
                                                    range=range_to_update,
                                                    valueInputOption='USER_ENTERED',
                                                    insertDataOption='INSERT_ROWS',
                                                    body=data).execute()
        result = self.service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_ID,
                                                          range=range_to_update).execute()
        print(result['values'])

        print(f'New username appended to column A: {new_username}, index is ')


def add_user_to_table(user_name: str):
    gs = GoogleSheet()
    gs.appendToColumnA(new_username=user_name)
