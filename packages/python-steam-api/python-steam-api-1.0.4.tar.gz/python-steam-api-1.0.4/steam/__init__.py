from .users import Users
from .client import Client
from .apps import Apps
from decouple import config

KEY = config("STEAM_API_KEY")
__all__ = ["Steam"]


class Steam:
    """Steam API client"""

    def __init__(self, key: str = KEY, headers: dict = {}):
        """Constructor for Steam API client"""
        client = Client(key, headers=headers)
        self.__users = Users(client)
        self.__apps = Apps(client)

    @property
    def users(self) -> Users:
        return self.__users

    @property
    def apps(self) -> Apps:
        return self.__apps
