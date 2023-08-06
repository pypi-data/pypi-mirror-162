from typing import Optional

from aiogoogle import GoogleAPI
from pydantic import create_model
from tygle.base import REST
from tygle.base.requests import DataRequest
from tygle.client import Client
from tygle_sheets.types.enums import (
    DateTimeRenderOption,
    Dimension,
    InsertDataOption,
    ValueInputOption,
    ValueRenderOption,
)
from tygle_sheets.types.resources.values import ValueRange, ValueRangeRESTs
from tygle_sheets.types.responses.values import AppendValuesResponse


class Values(REST):
    def __init__(self, client: Client, parent: GoogleAPI) -> None:
        super().__init__(client, parent)

        self.ValueRange = create_model("ValueRange", __base__=ValueRange)
        self.ValueRange.__rests__ = ValueRangeRESTs(self)

    def get(
        self,
        spreadsheet_id: str,
        range: str,
        /,
        *,
        major_dimension: Optional[Dimension] = None,
        value_render_option: Optional[ValueRenderOption] = None,
        date_time_render_option: Optional[DateTimeRenderOption] = None,
    ) -> DataRequest["ValueRange"]:
        """Returns a range of values from a spreadsheet. The caller must specify the spreadsheet ID and a range.

        https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/get
        """
        return DataRequest(
            self.client,
            self.parent.spreadsheets.values.get(
                spreadsheetId=spreadsheet_id,
                range=range,
                majorDimension=major_dimension.value if major_dimension else None,
                valueRenderOption=value_render_option.value
                if value_render_option
                else None,
                dateTimeRenderOption=date_time_render_option.value
                if date_time_render_option
                else None,
            ),
            self.ValueRange,
        )

    def append(
        self,
        spreadsheet_id: str,
        range: str,
        /,
        value_range: "ValueRange",
        *,
        value_input_option: Optional[ValueInputOption] = None,
        insert_data_option: Optional[InsertDataOption] = None,
        include_values_in_response: Optional[bool] = None,
        response_value_render_option: Optional[ValueRenderOption] = None,
        response_date_time_render_option: Optional[DateTimeRenderOption] = None,
    ) -> DataRequest[AppendValuesResponse]:
        """Appends values to a spreadsheet.

        https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append
        """
        return DataRequest(
            self.client,
            self.parent.spreadsheets.values.append(
                spreadsheetId=spreadsheet_id,
                range=range,
                json=value_range.dict(),
                valueInputOption=value_input_option.value
                if value_input_option
                else None,
                insertDataOption=insert_data_option.value
                if insert_data_option
                else None,
                includeValuesInResponse=include_values_in_response,
                responseValueRenderOption=response_value_render_option.value
                if response_value_render_option
                else None,
                responseDateTimeRenderOption=response_date_time_render_option.value
                if response_date_time_render_option
                else None,
            ),
            AppendValuesResponse,
        )
