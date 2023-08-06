from typing import Optional

from pydantic import BaseModel, Field

from .extended_value import ExtendedValue


class CellData(BaseModel):
    """
    Data about a specific cell.

    https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/cells#CellData
    """

    user_entered_value: Optional[ExtendedValue] = Field(None, alias="userEnteredValue")
    effective_value: Optional[ExtendedValue] = Field(None, alias="effectiveValue")
    formatted_value: Optional[str] = Field(None, alias="formattedValue")
