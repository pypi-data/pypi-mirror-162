from pydantic import BaseModel, Field

from .grid_data import GridData
from .grid_range import GridRange
from .sheet_properties import SheetProperties


class Sheet(BaseModel):
    """
    A sheet in a spreadsheet.

    https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/sheets#Sheet
    """

    properties: SheetProperties = Field()
    data: list[GridData] = Field()
    merges: list[GridRange] = Field()
