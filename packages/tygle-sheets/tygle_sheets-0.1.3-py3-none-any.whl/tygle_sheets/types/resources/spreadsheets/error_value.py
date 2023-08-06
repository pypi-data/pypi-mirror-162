from pydantic import BaseModel, Field
from tygle_sheets.types.enums import ErrorType


class ErrorValue(BaseModel):
    """
    An error in a cell.

    https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/other#ErrorValue
    """

    type: ErrorType = Field()
    message: str = Field()
