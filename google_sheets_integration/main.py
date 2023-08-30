from __future__ import print_function

import calendar
import locale
import os.path
import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import SAMPLE_SPREADSHEET_ID
from json_functionality import get_all_user_names

locale.setlocale(locale.LC_ALL, 'uk_UA')


def get_column_letter(col):
    """
    Convert a 1-based column index to the corresponding column letter.
    For example: 1 -> 'A', 2 -> 'B', ..., 27 -> 'AA', ...
    """
    letters = []
    while col > 0:
        col, remainder = divmod(col - 1, 26)
        letters.append(chr(65 + remainder))
    return ''.join(reversed(letters))


def current_month_days_list():
    now = datetime.datetime.now()
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    days_month_list = [f"{str(day).zfill(2)}.{now.strftime('%m')}" for day in range(1, days_in_month + 1)]
    return days_month_list


class GoogleSheet:
    SPREADSHEET_ID = SAMPLE_SPREADSHEET_ID
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    sheet_id = None
    service = None

    def __init__(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
            # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.path.join(os.getcwd(), 'google_sheets_integration', 'credentials.json'), self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            self.service = build('sheets', 'v4', credentials=creds)

        except HttpError as err:
            pass

    def append_to_column_a(self, new_username):
        current_month_year = f"{datetime.datetime.now().strftime('%B')} {datetime.datetime.now().strftime('%Y')}"

        range_to_update = f'{current_month_year}!A:A'
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

        # print(f'New username appended to column A: {new_username}, index is ')

    def create_month_table(self):
        current_month_year = f"{datetime.datetime.now().strftime('%B')} {datetime.datetime.now().strftime('%Y')}"
        bold_format = {
            "textFormat": {
                "bold": True
            }
        }

        requests = [
            {
                "addSheet": {
                    "properties": {
                        "title": current_month_year
                    }
                }
            }
        ]
        response = self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.SPREADSHEET_ID, body={'requests': requests}).execute()  # створює таблицю з іменем місяця

        self.sheet_id = response['replies'][0]['addSheet']['properties']['sheetId']  # присвоюємо id нової таблиці

        # Apply bold formatting to the header cells
        format_request = [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": self.sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": len(current_month_days_list()) + 1
                    },
                    "cell": {
                        "userEnteredFormat": bold_format
                    },
                    "fields": "userEnteredFormat"
                }
            }
        ]
        format_response = self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.SPREADSHEET_ID, body={'requests': format_request}).execute()
        all_users = get_all_user_names()
        values = [['П.І.Б. / дата'] + current_month_days_list() + ['Сума'],
                  *all_users]
        data = [{
            'values': values,
            'range': f"{current_month_year}!1:1000"
        }]
        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': data
        }
        value_response = self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=self.SPREADSHEET_ID, body=body).execute()

        # Auto-resize the columns and formula for SUM
        resize_requests = [
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": self.sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 1,
                        "endIndex": len(values[0])
                    },
                    "properties": {
                        "pixelSize": 40
                    },
                    "fields": "pixelSize"
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": self.sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 1,
                    },
                    "properties": {
                        "pixelSize": 160
                    },
                    "fields": "pixelSize"
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "sheetId": self.sheet_id,
                        "startRowIndex": 1,
                        "endRowIndex": len(values[0]),
                        "startColumnIndex": 1,
                        "endColumnIndex": 150,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "numberFormat": {
                                "type": "DATE_TIME",
                                "pattern": "[h]:mm"
                            }
                        }
                    },
                    "fields": "userEnteredFormat.numberFormat"
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "sheetId": self.sheet_id,
                        "startRowIndex": 1,
                        "endRowIndex": len(all_users) + 1,
                        "startColumnIndex": len(values[0]) - 1,
                        "endColumnIndex": len(values[0])
                    },
                    "cell": {
                        "userEnteredValue": {
                            "formulaValue": "=SUM(B2:AF2)"
                        }
                    },
                    "fields": "userEnteredValue"
                }
            }
        ]

        self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.SPREADSHEET_ID, body={'requests': resize_requests}).execute()

    def get_sheets(self):
        res = self.service.spreadsheets().get(spreadsheetId=SAMPLE_SPREADSHEET_ID).execute()
        all_sheets = [r['properties']['title'] for r in res['sheets']]
        return all_sheets

    def user_date_coords(self, user_name: str):
        current_date = datetime.datetime.now().strftime('%d.%m')
        current_month_year = f"{datetime.datetime.now().strftime('%B')} {datetime.datetime.now().strftime('%Y')}"

        try:
            sheet = self.service.spreadsheets()
            date_row_data = sheet.values().get(spreadsheetId=self.SPREADSHEET_ID,
                                               range=f'{current_month_year}!1:1').execute()
            date_num_coord = date_row_data['values'][0].index(current_date) + 1
            date_letter_coord = get_column_letter(col=date_num_coord)

            users = sheet.values().get(spreadsheetId=self.SPREADSHEET_ID, range=f'{current_month_year}!A:A').execute()
            user_id = users['values'].index([user_name]) + 1

            return f"{date_letter_coord}{user_id}"

        except HttpError as err:
            return f"An error occurred: {err}"

    def add_work_hours(self, user_name, work_time):
        coords = self.user_date_coords(user_name=user_name)
        current_month_year = f"{datetime.datetime.now().strftime('%B')} {datetime.datetime.now().strftime('%Y')}"
        range_to_update = f'{current_month_year}!{coords}'
        try:
            body = {
                'values': [[work_time]]
            }
            result = self.service.spreadsheets().values().update(spreadsheetId=self.SPREADSHEET_ID,
                                                                 range=range_to_update,
                                                                 valueInputOption='USER_ENTERED',
                                                                 body=body).execute()
            # print(f"Data '{work_time}' inserted at {coords}")
        except HttpError as err:
            # return print(f"An error occurred: {err}")
            pass

    def get_work_hours(self, user_name):
        coords = self.user_date_coords(user_name=user_name)
        current_month_year = f"{datetime.datetime.now().strftime('%B')} {datetime.datetime.now().strftime('%Y')}"

        range_to_get = f'{current_month_year}!{coords}'
        try:
            result = self.service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_ID,
                                                              range=range_to_get).execute()
            values = result.get('values')[0][0]
            return values
        except HttpError as err:
            # return print(f'An error occurred: {err}')
            pass

    def get_month_hours(self, user_name):
        current_month_year = f"{datetime.datetime.now().strftime('%B')} {datetime.datetime.now().strftime('%Y')}"

        sum_cell_index = len(current_month_days_list()) + 2
        users = self.service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_ID,
                                                         range=f'{current_month_year}!A:A').execute()
        row_index = users['values'].index([user_name]) + 1
        column_index = get_column_letter(sum_cell_index)

        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.SPREADSHEET_ID,
            range=f"{current_month_year}!{column_index}{row_index}", majorDimension='ROWS').execute()

        return result['values'][0][0]


gs = GoogleSheet()


def add_user_to_table(user_name: str):
    gs.append_to_column_a(new_username=user_name)


def create_new_month_sheet():
    try:
        gs.create_month_table()
    except HttpError:
        # print('table already exist')
        pass
