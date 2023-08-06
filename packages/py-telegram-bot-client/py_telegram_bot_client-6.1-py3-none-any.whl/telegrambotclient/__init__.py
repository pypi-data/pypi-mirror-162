from typing import Optional
from telegrambotclient.api import TelegramBotAPI
from telegrambotclient.bot import TelegramBot
from telegrambotclient.router import TelegramRouter
from telegrambotclient.storage import TelegramStorage


class TelegramBotClient:
    __slots__ = ("bots", "routers", "name", "api_callers")

    def __init__(self, name: str = "default"):
        self.bots = {}
        self.routers = {}
        self.api_callers = {}
        self.name = name

    def router(self, name: str = "default") -> TelegramRouter:
        router = self.routers.get(name, None)
        if router is None:
            self.routers[name] = TelegramRouter(name)
            return self.routers[name]
        return router

    def create_bot(self,
                   token: str,
                   bot_api: Optional[TelegramBotAPI] = None,
                   storage: Optional[TelegramStorage] = None,
                   i18n_source=None,
                   session_expires: int = 1800) -> TelegramBot:

        bot_api = self.api_callers.get(
            bot_api.host if bot_api else "https://api.telegram.org", None)
        if bot_api is None:
            bot_api = TelegramBotAPI()
            self.api_callers[bot_api.host] = bot_api
        bot = TelegramBot(token, bot_api, storage, i18n_source,
                          session_expires)
        self.bots[token] = bot
        return bot


# a default client
bot_client = TelegramBotClient()

__all__ = ("bot_client", "TelegramBotClient", "TelegramBotAPI", "TelegramBot")
