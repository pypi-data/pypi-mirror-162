from enum import Enum


class Dimension(str, Enum):
    """
    Indicates which dimension an operation should apply to.

    https://developers.google.com/sheets/api/reference/rest/v4/Dimension
    """

    DIMENSION_UNSPECIFIED = "DIMENSION_UNSPECIFIED"  #: The default value, do not use.
    ROWS = "ROWS"  #: Operates on the rows of a sheet.
    COLUMNS = "COLUMNS"  #: Operates on the columns of a sheet.
