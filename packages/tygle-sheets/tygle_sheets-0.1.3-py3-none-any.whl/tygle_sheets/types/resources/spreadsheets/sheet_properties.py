from pydantic import BaseModel, Field


class SheetProperties(BaseModel):
    """
    Properties of a sheet.

    https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/sheets#SheetProperties
    """

    sheet_id: int = Field(alias="sheetId")
    title: str = Field()
