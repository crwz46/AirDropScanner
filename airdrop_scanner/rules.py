from .engine import Rule, Airdrop, register, WalletProfile, RuleResult


def _make_rule(name, desc, fn):
    return Rule(name, desc, lambda p: RuleResult(name, desc, fn(p), ""))


def _has_chain(profile: WalletProfile, chain: str) -> bool:
    return chain in profile.chains


def _chain_tx(profile: WalletProfile, chain: str) -> int:
    return profile.chains.get(chain, {}).get("tx_count", 0)


def _chain_vol(profile: WalletProfile, chain: str) -> float:
    return profile.chains.get(chain, {}).get("volume_eth", 0.0)


def _chain_protocols(profile: WalletProfile, chain: str) -> list:
    return profile.protocols_used.get(chain, [])


def _uses_protocol(profile: WalletProfile, protocol: str) -> bool:
    return any(protocol in prots for prots in profile.protocols_used.values())


def _multi_chain_count(profile: WalletProfile) -> int:
    return len(profile.chains)


# ── Arbitrum ──────────────────────────────────────────────────────────
register(Airdrop("Arbitrum", "Arbitrum One", "🔵", [
    _make_rule("TX Count ≥ 4", "Made at least 4 transactions on Arbitrum",
               lambda p: _chain_tx(p, "arbitrum") >= 4),
    _make_rule("Bridged Funds", "Bridged at least 0.01 ETH to Arbitrum",
               lambda p: _chain_vol(p, "arbitrum") > 0.01),
    _make_rule("Protocol Diversity", "Interacted with at least 3 protocols on Arbitrum",
               lambda p: len(_chain_protocols(p, "arbitrum")) >= 3),
    _make_rule("Active ≥ 3 Months", "Wallet active on Arbitrum for 3+ months",
               lambda p: p.chains.get("arbitrum", {}).get("days_active", 0) >= 90),
    _make_rule("Nova Check", "Also used Arbitrum Nova",
               lambda p: _has_chain(p, "arbitrum") and p.total_tx > 20),
]))

# ── LayerZero ─────────────────────────────────────────────────────────
register(Airdrop("LayerZero", "Multi-Chain", "🌐", [
    _make_rule("Cross-Chain Messages", "Made at least 5 cross-chain messages via LayerZero",
               lambda p: _multi_chain_count(p) >= 3 and p.total_tx >= 5),
    _make_rule("Protocol Integration", "Used at least 2 LayerZero-based protocols",
               lambda p: sum(1 for prots in p.protocols_used.values()
                             for prot in prots if prot in ["Stargate", "Rage Trade", "Radiant", "Maverick"])
                         >= 2),
    _make_rule("Volume ≥ 0.5 ETH", "Total cross-chain volume ≥ 0.5 ETH",
               lambda p: p.total_volume_eth >= 0.5),
    _make_rule("Multi-Chain User", "Active on at least 3 different chains",
               lambda p: _multi_chain_count(p) >= 3),
    _make_rule("Bridge Usage", "Bridged funds between chains",
               lambda p: p.bridge_volume_eth > 0),
]))

# ── zkSync ────────────────────────────────────────────────────────────
register(Airdrop("zkSync", "zkSync Era", "⚡", [
    _make_rule("TX Count ≥ 10", "Made at least 10 transactions on zkSync",
               lambda p: _chain_tx(p, "zksync") >= 10),
    _make_rule("Bridged ≥ 0.02 ETH", "Bridged at least 0.02 ETH to zkSync",
               lambda p: _chain_vol(p, "zksync") >= 0.02),
    _make_rule("Protocol Interaction", "Interacted with at least 3 protocols on zkSync",
               lambda p: len(_chain_protocols(p, "zksync")) >= 3),
    _make_rule("Long-term Activity", "Active on zkSync for 6+ months OR high volume",
               lambda p: (p.chains.get("zksync", {}).get("days_active", 0) >= 180)
                         or _chain_vol(p, "zksync") >= 5),
    _make_rule("DeFi Engagement", "Used DeFi protocols on zkSync",
               lambda prof: any(prot in _chain_protocols(prof, "zksync")
                             for prot in ["SyncSwap", "Mute", "Maverick", "Izumi"])),
]))

# ── Optimism ──────────────────────────────────────────────────────────
register(Airdrop("Optimism", "OP Mainnet", "🔴", [
    _make_rule("TX Count ≥ 4", "Made at least 4 transactions on Optimism",
               lambda p: _chain_tx(p, "optimism") >= 4),
    _make_rule("Bridge Used", "Used the Optimism bridge",
               lambda p: _chain_vol(p, "optimism") > 0.01),
    _make_rule("Governance Participation", "Voted or delegated OP tokens",
               lambda p: _uses_protocol(p, "Velodrome") or _uses_protocol(p, "Synthetix")),
    _make_rule("Multi-Month Activity", "Active on Optimism in at least 2 different months",
               lambda p: p.chains.get("optimism", {}).get("days_active", 0) >= 30),
    _make_rule("Protocol Engagement", "Interacted with at least 2 protocols",
               lambda p: len(_chain_protocols(p, "optimism")) >= 2),
]))

# ── StarkNet ──────────────────────────────────────────────────────────
register(Airdrop("StarkNet", "StarkNet", "🟣", [
    _make_rule("TX Count ≥ 3", "Made at least 3 transactions on StarkNet",
               lambda p: _chain_tx(p, "starknet") >= 3),
    _make_rule("Bridged ≥ 0.005 ETH", "Bridged at least 0.005 ETH to StarkNet",
               lambda p: _chain_vol(p, "starknet") >= 0.005),
    _make_rule("Protocol Interaction", "Interacted with at least 2 protocols on StarkNet",
               lambda p: len(_chain_protocols(p, "starknet")) >= 2),
    _make_rule("Sustained Activity", "Active on StarkNet in at least 2 separate months",
               lambda p: p.chains.get("starknet", {}).get("days_active", 0) >= 30),
    _make_rule("DeFi or NFT Usage", "Used DeFi or NFT protocols on StarkNet",
               lambda p: len(_chain_protocols(p, "starknet")) > 0),
]))

# ── EigenLayer ────────────────────────────────────────────────────────
register(Airdrop("EigenLayer", "Ethereum", "🟠", [
    _make_rule("Restaked ≥ 0.1 ETH", "Restaked at least 0.1 ETH via EigenLayer",
               lambda p: p.estimated_value_eth >= 0.1),
    _make_rule("LRT Holding", "Holds at least one Liquid Restaking Token",
               lambda p: p.token_count >= 3 and p.total_volume_eth >= 0.5),
    _make_rule("Active ≥ 30 Days", "Active for at least 30 days",
               lambda p: p.wallet_age_days >= 30),
    _make_rule("DeFi Engagement", "Used at least 3 different DeFi protocols",
               lambda p: sum(len(prots) for prots in p.protocols_used.values()) >= 3),
    _make_rule("Ethereum Mainnet Active", "Active on Ethereum mainnet",
               lambda p: _has_chain(p, "ethereum")),
]))
