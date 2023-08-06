from aiogoogle import GoogleAPI
from tygle.base import API
from tygle.client import Client

from .rest import Spreadsheets


class Sheets(API):
    api_name = "sheets"
    api_version = "v4"

    def __init__(self, client: Client, api: GoogleAPI) -> None:
        super().__init__(client, api)
        self.spreadsheets = Spreadsheets(client, self.api)
