from typing import TYPE_CHECKING, ClassVar, List, Optional

from pydantic import Field, PrivateAttr
from tygle.base import Resource, RESTs

from .chains import ValuesChain
from .sheet import Sheet
from .spreadsheet_properties import SpreadsheetProperties

if TYPE_CHECKING:
    from tygle_sheets.rest.spreadsheets import Spreadsheets
    from tygle_sheets.rest.values import Values


class SpreadsheetRESTs(RESTs):
    def __init__(self, Spreadsheets: "Spreadsheets", Values: "Values"):
        self.Spreadsheets = Spreadsheets
        self.Values = Values


class Spreadsheet(Resource):
    """
    Resource that represents a spreadsheet.

    https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets#resource:-spreadsheet
    """

    __rests__: ClassVar[SpreadsheetRESTs] = PrivateAttr()

    @property
    def Values(self):
        return ValuesChain(self.__rests__.Values, spreadsheet_id=self.spreadsheet_id)

    def get(
        self,
        ranges: Optional[List[str]] = None,
        include_grid_data: bool = True,
    ):
        return self.__rests__.Spreadsheets.get(
            self.spreadsheet_id,
            ranges=ranges,
            include_grid_data=include_grid_data,
        )

    spreadsheet_id: str = Field(alias="spreadsheetId")
    properties: SpreadsheetProperties = Field()
    sheets: list[Sheet] = Field()
