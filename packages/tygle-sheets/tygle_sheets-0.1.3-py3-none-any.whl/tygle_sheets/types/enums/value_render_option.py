from enum import Enum


class ValueRenderOption(str, Enum):
    """
    Determines how values should be rendered in the output.

    https://developers.google.com/sheets/api/reference/rest/v4/ValueRenderOption
    """

    FORMATTED_VALUE = "FORMATTED_VALUE"  #: Values will be calculated & formatted in the reply according to the cell's formatting.
    UNFORMATTED_VALUE = "UNFORMATTED_VALUE"  #: Values will be calculated, but not formatted in the reply.
    FORMULA = "FORMULA"  #: Values will not be calculated. The reply will include the formulas.
