from typing import Optional

from .config import Config
from .cache import Cache
from .engine import WalletProfile, WalletSimulator


class WalletFetcher:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.cache = Cache(self.config.CACHE_DIR, self.config.CACHE_TTL)

    def fetch(self, address: str, tier: Optional[int] = None) -> WalletProfile:
        addr = address.lower().strip()
        if not addr.startswith("0x"):
            addr = "0x" + addr

        cache_key = f"wallet_{addr}" if tier is None else f"wallet_{addr}_tier{tier}"
        cached = self.cache.get(cache_key)
        if cached:
            return WalletProfile(**cached)

        profile = WalletSimulator.generate(addr, tier=tier)

        self.cache.set(cache_key, {
            "address": profile.address,
            "chains": profile.chains,
            "total_tx": profile.total_tx,
            "total_volume_eth": profile.total_volume_eth,
            "protocols_used": profile.protocols_used,
            "bridge_volume_eth": profile.bridge_volume_eth,
            "wallet_age_days": profile.wallet_age_days,
            "unique_contracts": profile.unique_contracts,
            "token_count": profile.token_count,
            "estimated_value_eth": profile.estimated_value_eth,
        })

        return profile
