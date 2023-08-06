from pydantic import BaseModel, Field

from .cell_data import CellData


class RowData(BaseModel):
    """
    Data about each cell in a row.

    https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/sheets#RowData
    """

    values: list[CellData] = Field([])
