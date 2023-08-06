from pydantic import BaseModel


class SpreadsheetProperties(BaseModel):
    """
    Properties of a spreadsheet.

    https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets#spreadsheetproperties
    """

    title: str
