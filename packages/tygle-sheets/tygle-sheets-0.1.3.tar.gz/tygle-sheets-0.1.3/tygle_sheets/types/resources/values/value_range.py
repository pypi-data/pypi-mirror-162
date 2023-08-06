from typing import TYPE_CHECKING, ClassVar, Optional

from pydantic import Field, PrivateAttr
from tygle.base import Resource, RESTs
from tygle_sheets.types.enums import (
    DateTimeRenderOption,
    Dimension,
    InsertDataOption,
    ValueInputOption,
    ValueRenderOption,
)

if TYPE_CHECKING:
    from tygle_sheets.rest.values import Values


class ValueRangeRESTs(RESTs):
    def __init__(self, Values: "Values"):
        self.Values = Values


class ValueRange(Resource):
    """Data within a range of the spreadsheet.

    https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values#ValueRange
    """

    range: str = Field()
    major_dimension: Dimension = Field(alias="majorDimension")
    values: list[list] = Field()

    __rests__: ClassVar[ValueRangeRESTs] = PrivateAttr()

    def get(
        self,
        spreadsheet_id: str,
        /,
        *,
        major_dimension: Optional[Dimension] = None,
        value_render_option: Optional[ValueRenderOption] = None,
        date_time_render_option: Optional[DateTimeRenderOption] = None,
    ):
        return self.__rests__.Values.get(
            spreadsheet_id,
            self.range,
            major_dimension=major_dimension,
            value_render_option=value_render_option,
            date_time_render_option=date_time_render_option,
        )

    def append(
        self,
        spreadsheet_id: str,
        range: str,
        /,
        *,
        value_input_option: Optional[ValueInputOption] = None,
        insert_data_option: Optional[InsertDataOption] = None,
        include_values_in_response: Optional[bool] = None,
        response_value_render_option: Optional[ValueRenderOption] = None,
        response_date_time_render_option: Optional[DateTimeRenderOption] = None,
    ):
        """Chain to :meth:`.Values.append`."""
        return self.__rests__.Values.append(
            spreadsheet_id,
            range,
            self,
            value_input_option=value_input_option,
            insert_data_option=insert_data_option,
            include_values_in_response=include_values_in_response,
            response_value_render_option=response_value_render_option,
            response_date_time_render_option=response_date_time_render_option,
        )
