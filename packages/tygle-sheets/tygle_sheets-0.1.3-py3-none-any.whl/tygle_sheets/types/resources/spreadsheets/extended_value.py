from typing import Optional

from pydantic import BaseModel, Field

from .error_value import ErrorValue


class ExtendedValue(BaseModel):
    """
    The kinds of value that a cell in a spreadsheet can have.

    https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/other#ExtendedValue
    """

    number_value: Optional[float] = Field(None, alias="numberValue")
    string_value: Optional[str] = Field(None, alias="stringValue")
    bool_value: Optional[bool] = Field(None, alias="boolValue")
    formula_value: Optional[str] = Field(None, alias="formulaValue")
    error_value: Optional[ErrorValue] = Field(None, alias="errorValue")
