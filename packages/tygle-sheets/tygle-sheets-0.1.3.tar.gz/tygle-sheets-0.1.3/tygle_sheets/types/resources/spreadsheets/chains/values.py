from typing import TYPE_CHECKING, Optional

from pydantic import PrivateAttr
from tygle.base import Chain
from tygle_sheets.types.enums import (
    DateTimeRenderOption,
    Dimension,
    InsertDataOption,
    ValueInputOption,
    ValueRenderOption,
)
from tygle_sheets.types.resources.values import ValueRange

if TYPE_CHECKING:
    from tygle_sheets.rest.values import Values


class ValuesChain(Chain):
    _rest: "Values" = PrivateAttr()
    spreadsheet_id: str

    def __init__(self, rest, **data):
        super().__init__(**data)
        self._rest = rest

    def get(
        self,
        range: str,
        /,
        *,
        major_dimension: Optional[Dimension] = None,
        value_render_option: Optional[ValueRenderOption] = None,
        date_time_render_option: Optional[DateTimeRenderOption] = None,
    ):
        return self._rest.get(
            self.spreadsheet_id,
            range,
            major_dimension=major_dimension,
            value_render_option=value_render_option,
            date_time_render_option=date_time_render_option,
        )

    def append(
        self,
        range: str,
        /,
        value_range: ValueRange,
        *,
        value_input_option: Optional[ValueInputOption] = None,
        insert_data_option: Optional[InsertDataOption] = None,
        include_values_in_response: Optional[bool] = None,
        response_value_render_option: Optional[ValueRenderOption] = None,
        response_date_time_render_option: Optional[DateTimeRenderOption] = None,
    ):
        return self._rest.append(
            self.spreadsheet_id,
            range,
            value_range,
            value_input_option=value_input_option,
            insert_data_option=insert_data_option,
            include_values_in_response=include_values_in_response,
            response_value_render_option=response_value_render_option,
            response_date_time_render_option=response_date_time_render_option,
        )
