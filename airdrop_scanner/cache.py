import json
import os
import time


class Cache:
    def __init__(self, cache_dir: str = ".cache", ttl: int = 3600):
        self.cache_dir = cache_dir
        self.ttl = ttl
        os.makedirs(cache_dir, exist_ok=True)

    def get(self, key: str):
        path = os.path.join(self.cache_dir, f"{key}.json")
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r") as f:
                data = json.load(f)
            if time.time() - data.get("_ts", 0) > self.ttl:
                return None
            return data.get("_data")
        except (json.JSONDecodeError, KeyError, OSError):
            return None

    def set(self, key: str, data) -> None:
        path = os.path.join(self.cache_dir, f"{key}.json")
        payload = {"_ts": time.time(), "_data": data}
        try:
            with open(path, "w") as f:
                json.dump(payload, f)
        except OSError:
            pass
