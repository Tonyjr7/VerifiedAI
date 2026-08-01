from decouple import config

class Settings:
    groq_api_key: str = config("groq_api_key")
    tavily_api_key: str = config("tavily_api_key", default="")

    database_url: str = config("database_url")
    yarngpt_api_key: str = config("yarngpt_api_key")

    model: str = config("model")