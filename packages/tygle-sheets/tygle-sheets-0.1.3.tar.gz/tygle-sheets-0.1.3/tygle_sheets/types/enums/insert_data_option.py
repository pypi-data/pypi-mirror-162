from enum import Enum


# todo: move
class InsertDataOption(str, Enum):
    """
    Determines how existing data is changed when new data is input.

    https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append#InsertDataOption
    """

    OVERWRITE = "OVERWRITE"  #: The new data overwrites existing data in the areas it is written.
    INSERT_ROWS = "INSERT_ROWS"  #: Rows are inserted for the new data.
