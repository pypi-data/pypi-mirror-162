from typing import Optional

from pydantic import BaseModel, Field


class GridRange(BaseModel):
    """
    A range on a sheet. All indexes are zero-based.
    Indexes are half open, i.e. the start index is inclusive and the end index is exclusive -- [startIndex, endIndex).
    Missing indexes indicate the range is unbounded on that side.

    https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/other#GridRange
    """

    sheet_id: Optional[int] = Field(None, alias="sheetId")
    start_row_index: int = Field(alias="startRowIndex")
    end_row_index: int = Field(alias="endRowIndex")
    start_column_index: int = Field(alias="startColumnIndex")
    end_column_index: int = Field(alias="endColumnIndex")
