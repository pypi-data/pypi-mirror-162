from typing import Optional

from pydantic import BaseModel, Field

from .row_data import RowData


class GridData(BaseModel):
    """
    Data in the grid, as well as metadata about the dimensions.

    https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/sheets#GridData
    """

    start_row: Optional[int] = Field(None, alias="startRow")
    start_column: Optional[int] = Field(None, alias="startColumn")
    row_data: list[RowData] = Field(alias="rowData")
