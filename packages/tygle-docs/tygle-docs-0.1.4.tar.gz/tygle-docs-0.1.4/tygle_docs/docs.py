from aiogoogle import GoogleAPI
from tygle.base import API
from tygle.client import Client

from .rest import Documents


class Docs(API):
    api_name = "docs"
    api_version = "v1"

    def __init__(self, client: Client, api: GoogleAPI) -> None:
        super().__init__(client, api)
        self.files = Documents(client, self.api)
