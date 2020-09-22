# Global variables #

from intratime_slack_bot.config import settings


# URLS
PROTOCOL = "http"
MONGO_DB_SERVER = f"mongodb://{settings.MONGO_DB_USER}:{settings.MONGO_DB_PASSWORD}@{settings.MONGO_DB_HOST}:"\
                  f"{settings.MONGO_DB_PORT}/"
