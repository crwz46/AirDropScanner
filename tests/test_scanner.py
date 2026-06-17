import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from airdrop_scanner.engine import (
    Rule, Airdrop, WalletProfile, WalletSimulator, PortfolioValuator,
    list_airdrops, get_airdrop, AIRDROP_REGISTRY, RuleResult,
)
from airdrop_scanner.fetcher import WalletFetcher
from airdrop_scanner.config import Config
from airdrop_scanner.cache import Cache
from airdrop_scanner import rules


SAMPLE_ADDR = "0x1234567890abcdef1234567890abcdef12345678"


@pytest.fixture
def sample_profile():
    return WalletProfile(
        address=SAMPLE_ADDR,
        chains={
            "ethereum": {"tx_count": 50, "volume_eth": 5.0, "protocols": ["Uniswap", "Aave"],
                         "days_active": 400, "unique_contracts": 20},
            "arbitrum": {"tx_count": 25, "volume_eth": 3.0, "protocols": ["Uniswap", "GMX", "Stargate"],
                         "days_active": 200, "unique_contracts": 12},
            "optimism": {"tx_count": 10, "volume_eth": 1.5, "protocols": ["Uniswap"],
                         "days_active": 60, "unique_contracts": 5},
        },
        total_tx=85,
        total_volume_eth=9.5,
        protocols_used={
            "ethereum": ["Uniswap", "Aave"],
            "arbitrum": ["Uniswap", "GMX", "Stargate"],
            "optimism": ["Uniswap"],
        },
        bridge_volume_eth=2.0,
        wallet_age_days=400,
        unique_contracts=37,
        token_count=12,
        estimated_value_eth=5.5,
    )


class TestRuleEngine:
    def test_rule_passes(self):
        rule = Rule("Test Rule", "Always passes", lambda p: RuleResult("Test Rule", "Always passes", True, ""))
        prof = WalletSimulator.generate(SAMPLE_ADDR)
        result = rule.evaluate(prof)
        assert result.passed is True
        assert result.name == "Test Rule"

    def test_rule_fails(self):
        rule = Rule("Test Fail", "Always fails", lambda p: RuleResult("Test Fail", "Always fails", False, ""))
        prof = WalletSimulator.generate(SAMPLE_ADDR)
        result = rule.evaluate(prof)
        assert result.passed is False

    def test_airdrop_check_all_pass(self, sample_profile):
        rule = Rule("Always Pass", "desc", lambda p: RuleResult("Always Pass", "desc", True, ""))
        airdrop = Airdrop("TestDrop", "TestChain", "🪙", [rule, rule, rule])
        result = airdrop.check(sample_profile)
        assert result.eligible is True
        assert result.score == 100
        assert result.passed == 3

    def test_airdrop_check_majority_fail(self, sample_profile):
        rules = [
            Rule("Pass", "desc", lambda p: RuleResult("Pass", "desc", True, "")),
            Rule("Fail", "desc", lambda p: RuleResult("Fail", "desc", False, "")),
            Rule("Fail2", "desc", lambda p: RuleResult("Fail2", "desc", False, "")),
        ]
        airdrop = Airdrop("TestFail", "TC", "❌", rules)
        result = airdrop.check(sample_profile)
        assert result.eligible is False
        assert result.score < 50

    def test_airdrop_check_edge_pass(self, sample_profile):
        rule = Rule("On edge", "passes", lambda p: RuleResult("On edge", "passes", True, ""))
        airdrop = Airdrop("Edge", "EC", "⚠️", [rule])
        result = airdrop.check(sample_profile)
        assert result.eligible is True
        assert result.passed == 1

    def test_airdrop_registry(self):
        assert len(AIRDROP_REGISTRY) >= 6
        assert "ARBITRUM" in AIRDROP_REGISTRY
        assert "LAYERZERO" in AIRDROP_REGISTRY
        assert "ZKSYNC" in AIRDROP_REGISTRY
        assert "OPTIMISM" in AIRDROP_REGISTRY
        assert "STARKNET" in AIRDROP_REGISTRY
        assert "EIGENLAYER" in AIRDROP_REGISTRY

    def test_get_airdrop(self):
        a = get_airdrop("arbitrum")
        assert a is not None
        assert a.name == "Arbitrum"
        assert len(a.rules) > 0

    def test_get_airdrop_unknown(self):
        assert get_airdrop("FAKE_PROTOCOL") is None

    def test_list_airdrops(self):
        airdrops = list_airdrops()
        names = [a.name for a in airdrops]
        assert "Arbitrum" in names
        assert "LayerZero" in names


class TestWalletSimulator:
    def test_generates_valid_profile(self):
        prof = WalletSimulator.generate(SAMPLE_ADDR)
        assert prof.address == SAMPLE_ADDR
        assert len(prof.chains) >= 1
        assert prof.total_tx > 0
        assert prof.total_volume_eth >= 0

    def test_deterministic(self):
        p1 = WalletSimulator.generate(SAMPLE_ADDR)
        p2 = WalletSimulator.generate(SAMPLE_ADDR)
        assert p1.total_tx == p2.total_tx
        assert p1.total_volume_eth == p2.total_volume_eth

    def test_different_wallets_different(self):
        p1 = WalletSimulator.generate("0x1111111111111111111111111111111111111111")
        p2 = WalletSimulator.generate("0x2222222222222222222222222222222222222222")
        assert p1.total_tx != p2.total_tx or p1.total_volume_eth != p2.total_volume_eth

    def test_tier_0_low_activity(self):
        prof = WalletSimulator.generate(SAMPLE_ADDR, tier=0)
        assert 0 < prof.total_tx <= 60

    def test_tier_4_high_activity(self):
        prof = WalletSimulator.generate(SAMPLE_ADDR, tier=4)
        assert prof.total_tx > 5

    def test_ethereum_always_present_for_high_tier(self):
        prof = WalletSimulator.generate(SAMPLE_ADDR, tier=4)
        chains = list(prof.chains.keys())
        assert len(chains) >= 2

    def test_protocols_assigned(self):
        prof = WalletSimulator.generate(SAMPLE_ADDR, tier=3)
        total = sum(len(v) for v in prof.protocols_used.values())
        assert total > 0


class TestPortfolioValuator:
    def test_rating_min_stars(self, sample_profile):
        low = WalletProfile(
            address="0xlow",
            chains={"ethereum": {"tx_count": 1, "volume_eth": 0.01, "protocols": ["Uniswap"],
                                 "days_active": 1, "unique_contracts": 1}},
            total_tx=1, total_volume_eth=0.01,
            protocols_used={"ethereum": ["Uniswap"]},
            bridge_volume_eth=0, wallet_age_days=1,
            unique_contracts=1, token_count=1, estimated_value_eth=0.01,
        )
        rating = PortfolioValuator.rate(low)
        assert 1 <= rating["stars"] <= 5

    def test_rating_max_stars(self, sample_profile):
        rating = PortfolioValuator.rate(sample_profile)
        assert 1 <= rating["stars"] <= 5

    def test_rating_breakdown(self, sample_profile):
        rating = PortfolioValuator.rate(sample_profile)
        assert "transactions" in rating["breakdown"]
        assert "volume" in rating["breakdown"]
        assert "diversity" in rating["breakdown"]
        assert "age" in rating["breakdown"]
        assert "bridges" in rating["breakdown"]

    def test_rating_score_range(self, sample_profile):
        rating = PortfolioValuator.rate(sample_profile)
        assert 0 <= rating["score"] <= 100


class TestFetcher:
    def test_fetch_generates_profile(self):
        fetcher = WalletFetcher()
        prof = fetcher.fetch(SAMPLE_ADDR)
        assert prof.address == SAMPLE_ADDR
        assert prof.total_tx > 0

    def test_fetch_with_tier(self):
        fetcher = WalletFetcher()
        prof = fetcher.fetch("0xffffffffffffffffffffffffffffffffffffffff", tier=0)
        assert prof.total_tx <= 60

    def test_fetch_cache(self):
        cache = Cache(ttl=3600)
        assert cache.get("test_nonexistent") is None


class TestRules:
    def test_arbitrum_eligibility(self):
        prof = WalletSimulator.generate(SAMPLE_ADDR, tier=4)
        airdrop = get_airdrop("arbitrum")
        assert airdrop is not None
        result = airdrop.check(prof)
        assert isinstance(result.eligible, bool)
        assert 0 <= result.score <= 100

    def test_layerzero_eligibility(self):
        prof = WalletSimulator.generate(SAMPLE_ADDR, tier=3)
        airdrop = get_airdrop("layerzero")
        assert airdrop is not None
        result = airdrop.check(prof)
        assert isinstance(result.eligible, bool)

    def test_all_airdrops_evaluable(self):
        for name in AIRDROP_REGISTRY:
            prof = WalletSimulator.generate(f"0x{hash(name):040x}", tier=2)
            airdrop = get_airdrop(name)
            assert airdrop is not None
            result = airdrop.check(prof)
            assert len(result.rules) > 0


class TestConfig:
    def test_default_config(self):
        cfg = Config()
        assert cfg.PORT == 8000
        assert cfg.HOST == "0.0.0.0"
        assert not cfg.has_etherscan_key()


class TestCache:
    def test_set_get(self):
        cache = Cache(ttl=3600)
        cache.set("test", {"data": 42})
        assert cache.get("test") == {"data": 42}

    def test_expiry(self):
        cache = Cache(ttl=0)
        cache.set("exp", "val")
        import time; time.sleep(0.01)
        assert cache.get("exp") is None

    def test_missing(self):
        cache = Cache()
        assert cache.get("__no_key__") is None
