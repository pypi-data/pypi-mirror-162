from enum import Enum


class DateTimeRenderOption(str, Enum):
    """
    Determines how dates should be rendered in the output.

    https://developers.google.com/sheets/api/reference/rest/v4/DateTimeRenderOption
    """

    SERIAL_NUMBER = "SERIAL_NUMBER"  #: Instructs date, time, datetime, and duration fields to be output as doubles in "serial number" format.
    FORMATTED_STRING = "FORMATTED_STRING"  #: Instructs date, time, datetime, and duration fields to be output as strings in their given number format.
