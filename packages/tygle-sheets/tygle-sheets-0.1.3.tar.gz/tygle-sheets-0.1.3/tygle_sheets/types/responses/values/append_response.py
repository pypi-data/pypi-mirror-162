from pydantic import BaseModel, Field
from tygle_sheets.types.responses import UpdateValuesResponse


class AppendValuesResponse(BaseModel):
    """
    The response when updating a range of values in a spreadsheet.

    https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append#response-body
    """

    spreadsheet_id: str = Field(alias="spreadsheetId")
    table_range: str = Field(alias="tableRange")
    updates: UpdateValuesResponse = Field()
