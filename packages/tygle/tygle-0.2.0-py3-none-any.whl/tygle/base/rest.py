from aiogoogle import GoogleAPI
from tygle.client import Client


class REST:
    def __init__(self, client: Client, parent: GoogleAPI) -> None:
        self.client = client
        self.parent = parent
