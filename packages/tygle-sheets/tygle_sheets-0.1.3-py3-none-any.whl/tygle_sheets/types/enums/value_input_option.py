from enum import Enum


class ValueInputOption(str, Enum):
    """
    Determines how input data should be interpreted.

    https://developers.google.com/sheets/api/reference/rest/v4/ValueInputOption
    """

    INPUT_VALUE_OPTION_UNSPECIFIED = "INPUT_VALUE_OPTION_UNSPECIFIED"  #: Default input value. This value must not be used.
    RAW = "RAW"  #: The values the user has entered will not be parsed and will be stored as-is.
    USER_ENTERED = "USER_ENTERED"  #: The values will be parsed as if the user typed them into the UI.
