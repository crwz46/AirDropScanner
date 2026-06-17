import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Config:
    ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")
    CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))
    CACHE_DIR = os.getenv("CACHE_DIR", ".cache")
    PORT = int(os.getenv("PORT", "8000"))
    HOST = os.getenv("HOST", "0.0.0.0")

    @classmethod
    def has_etherscan_key(cls) -> bool:
        return bool(cls.ETHERSCAN_API_KEY)
