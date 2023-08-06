from typing import List, Optional

from aiogoogle import GoogleAPI
from pydantic import create_model
from tygle.base import REST
from tygle.base.requests import DataRequest
from tygle.client import Client
from tygle_sheets.types.resources.spreadsheets import Spreadsheet, SpreadsheetRESTs

from .values import Values


class Spreadsheets(REST):
    def __init__(self, client: Client, parent: GoogleAPI) -> None:
        super().__init__(client, parent)
        self.values = Values(client, self.parent)  # todo move

        self.Spreadsheet = create_model("Spreadsheet", __base__=Spreadsheet)
        self.Spreadsheet.__rests__ = SpreadsheetRESTs(self, self.values)

    def get(
        self,
        spreadsheet_id: str,
        /,
        *,
        ranges: Optional[List[str]] = None,
        include_grid_data: bool = True,
    ) -> DataRequest[Spreadsheet]:
        if ranges is None:
            ranges = []
        return DataRequest(
            self.client,
            self.parent.spreadsheets.get(
                spreadsheetId=spreadsheet_id,
                ranges=ranges,
                includeGridData=include_grid_data,
            ),
            self.Spreadsheet,
        )
