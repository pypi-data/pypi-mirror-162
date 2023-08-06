from typing import Optional

from pydantic import BaseModel, Field
from tygle_sheets.types.resources.values import ValueRange


class UpdateValuesResponse(BaseModel):
    spreadsheet_id: str = Field(alias="spreadsheetId")
    updated_range: str = Field(alias="updatedRange")
    updated_rows: int = Field(alias="updatedRows")
    updated_columns: int = Field(alias="updatedColumns")
    updated_cells: int = Field(alias="updatedCells")
    updated_data: Optional[ValueRange] = Field(alias="updatedData")
