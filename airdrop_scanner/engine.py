from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from datetime import datetime, timedelta
import random


@dataclass
class RuleResult:
    name: str
    description: str
    passed: bool
    detail: str = ""


@dataclass
class EligibilityResult:
    protocol: str
    chain: str
    icon: str
    eligible: bool
    score: int
    passed: int
    total: int
    rules: List[RuleResult] = field(default_factory=list)

    @property
    def status_text(self) -> str:
        return "✅ ELIGIBLE" if self.eligible else "❌ NOT ELIGIBLE"

    @property
    def color(self) -> str:
        return "🟢" if self.eligible else "🔴"


@dataclass
class WalletProfile:
    address: str
    chains: Dict[str, dict]
    total_tx: int
    total_volume_eth: float
    protocols_used: Dict[str, List[str]]
    bridge_volume_eth: float
    wallet_age_days: int
    unique_contracts: int
    token_count: int
    estimated_value_eth: float


class Rule:
    def __init__(self, name: str, description: str, fn: Callable[[WalletProfile], RuleResult]):
        self.name = name
        self.description = description
        self.fn = fn

    def evaluate(self, profile: WalletProfile) -> RuleResult:
        return self.fn(profile)


class Airdrop:
    def __init__(self, name: str, chain: str, icon: str, rules: List[Rule]):
        self.name = name
        self.chain = chain
        self.icon = icon
        self.rules = rules

    def check(self, profile: WalletProfile) -> EligibilityResult:
        results = [r.evaluate(profile) for r in self.rules]
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        threshold = max(1, round(total * 0.6))
        eligible = passed >= threshold
        score = round((passed / total) * 100) if total > 0 else 0
        return EligibilityResult(
            protocol=self.name,
            chain=self.chain,
            icon=self.icon,
            eligible=eligible,
            score=score,
            passed=passed,
            total=total,
            rules=results,
        )


AIRDROP_REGISTRY: Dict[str, Airdrop] = {}


def register(airdrop: Airdrop):
    AIRDROP_REGISTRY[airdrop.name.upper()] = airdrop


def get_airdrop(name: str) -> Optional[Airdrop]:
    return AIRDROP_REGISTRY.get(name.upper())


def list_airdrops() -> List[Airdrop]:
    return list(AIRDROP_REGISTRY.values())


class PortfolioValuator:
    @staticmethod
    def rate(profile: WalletProfile) -> dict:
        score = 0

        tx_score = min(profile.total_tx / 200 * 25, 25)
        score += tx_score

        vol_score = min(profile.total_volume_eth / 50 * 25, 25)
        score += vol_score

        chain_div = len(profile.chains)
        prot_count = sum(len(v) for v in profile.protocols_used.values())
        diversity_score = min((chain_div * 5 + prot_count * 2), 25)
        score += diversity_score

        age_score = min(profile.wallet_age_days / 365 * 15, 15)
        score += age_score

        bridge_score = min(profile.bridge_volume_eth / 10 * 10, 10)
        score += bridge_score

        stars = max(1, round(score / 20))
        label = ["🥉 Bronze", "🥈 Silver", "🥇 Gold", "💎 Diamond", "👑 Legend"][stars - 1]

        return {
            "score": round(score, 1),
            "max_score": 100,
            "stars": stars,
            "max_stars": 5,
            "label": label,
            "breakdown": {
                "transactions": {"score": round(tx_score, 1), "max": 25},
                "volume": {"score": round(vol_score, 1), "max": 25},
                "diversity": {"score": round(diversity_score, 1), "max": 25},
                "age": {"score": round(age_score, 1), "max": 15},
                "bridges": {"score": round(bridge_score, 1), "max": 10},
            },
        }


class WalletSimulator:
    @staticmethod
    def generate(address: str, tier: Optional[int] = None) -> WalletProfile:
        raw = address.replace("0x", "").lower()
        seed = int(raw[:16], 16) if len(raw) >= 16 and all(c in "0123456789abcdef" for c in raw[:16]) else hash(address)
        random.seed(seed)

        if tier is None:
            tier = random.randint(0, 4)

        multipliers = {0: 0.1, 1: 0.3, 2: 0.6, 3: 1.0, 4: 2.0}
        mult = multipliers[tier]

        chains = {}
        all_chains = ["ethereum", "arbitrum", "optimism", "zksync", "polygon", "bsc", "avalanche", "base"]
        active_chains = random.sample(all_chains, max(1, random.randint(2, 6)))

        total_tx = 0
        total_vol = 0.0
        bridge_vol = 0.0
        protocols_used = {}
        all_protocols = {
            "ethereum": ["Uniswap", "Aave", "Compound", "MakerDAO", "Curve", "Lido", "Opensea", "Blur"],
            "arbitrum": ["Uniswap", "GMX", "Stargate", "Camelot", "Balancer", "Radiant", "JonesDAO"],
            "optimism": ["Uniswap", "Velodrome", "Synthetix", "Aave", "Hop", "Curve", "Perpetual"],
            "zksync": ["SyncSwap", "Mute", "SpaceFi", "Orbiter", "Across", "Maverick", "Izumi"],
            "polygon": ["Quickswap", "Aave", "Uniswap", "Curve", "Balancer", "SushiSwap"],
            "bsc": ["PancakeSwap", "Venus", "Alpaca", "BiSwap", "Stargate"],
            "avalanche": ["TraderJoe", "Benqi", "Platypus", "Aave", "Curve"],
            "base": ["Uniswap", "Aerodrome", "Maverick", "Seamless", "ExtraFi"],
        }

        for ch in active_chains:
            tx_count = int(random.randint(3, 80) * mult) + random.randint(0, 5)
            vol = round(random.uniform(0.1, 20) * mult + random.uniform(0, 2), 4)
            total_tx += tx_count
            total_vol += vol

            prots = all_protocols.get(ch, [])
            used = random.sample(prots, min(len(prots), max(1, random.randint(1, 5))))
            protocols_used[ch] = used

            days_active = int(random.randint(30, 800) * mult) + 7
            chains[ch] = {
                "tx_count": tx_count,
                "volume_eth": vol,
                "protocols": used,
                "days_active": days_active,
                "unique_contracts": int(tx_count * random.uniform(0.3, 0.8)),
            }

        bridge_vol = round(total_vol * random.uniform(0.1, 0.4), 4)
        unique_contracts = sum(c["unique_contracts"] for c in chains.values())
        token_count = random.randint(3, 30)
        estimated_value = round(total_vol * random.uniform(0.3, 0.8) + random.uniform(0.1, 2), 4)

        wallet_age = max(chains.get("ethereum", {}).get("days_active", 30),
                         max(c.get("days_active", 7) for c in chains.values()))

        return WalletProfile(
            address=address,
            chains=chains,
            total_tx=total_tx,
            total_volume_eth=round(total_vol, 4),
            protocols_used=protocols_used,
            bridge_volume_eth=bridge_vol,
            wallet_age_days=wallet_age,
            unique_contracts=unique_contracts,
            token_count=token_count,
            estimated_value_eth=round(estimated_value, 4),
        )
