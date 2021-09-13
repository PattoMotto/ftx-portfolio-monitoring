import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import pandas as pd
import json

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

# Load local config
configFile = open('portfolio_monitoring_bot.config')
jsonConfig = json.load(configFile)

credentialFile = jsonConfig['googleCredential']
creds = ServiceAccountCredentials.from_json_keyfile_name(credentialFile, scope)

client = gspread.authorize(creds)

def writeDataFrame(dataFrame, fileName, worksheetName):
    spreadsheet = client.open(fileName)
    for worksheet in spreadsheet.worksheets():
        if worksheetName == worksheet.title:
            worksheet = spreadsheet.worksheet(worksheetName)
            set_with_dataframe(worksheet, dataFrame)
            return
    worksheet = spreadsheet.add_worksheet(title=worksheetName, rows=len(dataFrame.index), cols=len(dataFrame.columns))
    set_with_dataframe(worksheet, dataFrame)

def readWorksheet(fileName, worksheetName):
    spreadsheet = client.open(fileName)
    for worksheet in spreadsheet.worksheets():
        if worksheetName == worksheet.title:
            worksheet = spreadsheet.worksheet(worksheetName)
            return pd.DataFrame(worksheet.get_all_values())
    worksheet = spreadsheet.add_worksheet(title=worksheetName, rows=100, cols=10)
    return pd.DataFrame(worksheet.get_all_values())

def clearWorksheet(fileName, worksheetName, range):
    sheet = client.open(fileName)
    sheet.values_clear('{}!{}'.format(worksheetName, range))

def setFirstRowAsColumn(dataFrame):
    dataFrame.columns = dataFrame.iloc[0]
    dataFrame = dataFrame[1:]
    return dataFrame
