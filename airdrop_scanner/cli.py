import argparse
import sys
import json

from .engine import list_airdrops, get_airdrop, PortfolioValuator
from .fetcher import WalletFetcher
from .config import Config


LEGEND = """
╔══════════════════════════════════════════════════╗
║            🪂 AirDropScanner v1.0                ║
║  Multi-protocol airdrop eligibility checker      ║
╚══════════════════════════════════════════════════╝
"""


def display_wallet(profile, results, portfolio, show_json=False):
    if show_json:
        output = {
            "wallet": profile.address,
            "total_tx": profile.total_tx,
            "total_volume_eth": profile.total_volume_eth,
            "chains": list(profile.chains.keys()),
            "protocols_used": profile.protocols_used,
            "portfolio": portfolio,
            "results": [
                {
                    "protocol": r.protocol,
                    "chain": r.chain,
                    "eligible": r.eligible,
                    "score": r.score,
                    "passed": r.passed,
                    "total": r.total,
                    "rules": [
                        {"name": r2.name, "passed": r2.passed, "detail": r2.detail}
                        for r2 in r.rules
                    ],
                }
                for r in results
            ],
        }
        print(json.dumps(output, indent=2))
        return

    print(LEGEND)
    print(f"\n  📋 Wallet: {profile.address}")
    print(f"  {'─' * 60}")

    chains_list = list(profile.chains.keys())
    print(f"  🌐 Chains: {', '.join(c.upper() for c in sorted(chains_list))}")
    print(f"  🔄 Total TX: {profile.total_tx:,}")
    print(f"  💰 Volume: {profile.total_volume_eth:.4f} ETH")
    print(f"  🏗️  Protocols: {sum(len(v) for v in profile.protocols_used.values())}")
    print(f"  📅 Wallet Age: {profile.wallet_age_days} days")
    print(f"  {'─' * 60}")

    for r in results:
        badge = "✅ ELIGIBLE" if r.eligible else "❌ NOT ELIGIBLE"
        bar_len = 20
        filled = int((r.score / 100) * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"\n  {r.icon} {r.protocol:<12s} ({r.chain})")
        print(f"     {badge:>16s}  [{bar}] {r.score}%  ({r.passed}/{r.total} rules met)")
        for rule in r.rules:
            icon = "✅" if rule.passed else "❌"
            print(f"     {icon} {rule.name:<35s} {rule.description}")

    p = portfolio
    stars_str = "⭐" * p["stars"] + "☆" * (p["max_stars"] - p["stars"])
    print(f"\n  {'═' * 60}")
    print(f"  📊 PORTFOLIO VALUE: {stars_str}  ({p['label']})")
    print(f"  {'═' * 60}")
    print(f"     Overall Score: {p['score']}/{p['max_score']}")
    for k, v in p["breakdown"].items():
        sub_bar = "█" * int(v["score"]) + "░" * int(v["max"] - v["score"])
        print(f"     {k:<15s} [{sub_bar}] {v['score']}/{v['max']}")
    print(f"  {'═' * 60}")
    print(f"  💎 Est. Portfolio Value: ~{profile.estimated_value_eth:.4f} ETH\n")


def main():
    parser = argparse.ArgumentParser(
        description="AirDropScanner — Multi-protocol airdrop eligibility checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  scanner 0x1234...                    Check wallet against all protocols
  scanner 0x1234... --protocol arbitrum Check specific protocol
  scanner 0x1234... --json             JSON output
  scanner 0x1234... --tier 4           Force high-activity tier (0-4)
  scanner --list                       List supported protocols
  scanner --server                     Start web server
        """,
    )
    parser.add_argument("address", nargs="?", help="Wallet address (0x...)")
    parser.add_argument("--protocol", "-p", help="Check specific protocol only")
    parser.add_argument("--tier", type=int, choices=range(0, 5),
                        help="Simulation tier (0=low, 4=high activity)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--list", action="store_true", help="List supported protocols")
    parser.add_argument("--server", action="store_true", help="Start web server")

    args = parser.parse_args()

    if args.server:
        start_server()
        return

    if args.list:
        print("\n  🪂 Supported Airdrop Protocols:\n")
        for a in sorted(list_airdrops(), key=lambda x: x.name):
            print(f"  {a.icon} {a.name:<12s} ({a.chain}) — {len(a.rules)} criteria")
        print()
        return

    if not args.address:
        parser.print_help()
        return

    addr = args.address.strip()
    fetcher = WalletFetcher()
    profile = fetcher.fetch(addr, tier=args.tier)

    if args.protocol:
        airdrop = get_airdrop(args.protocol)
        if not airdrop:
            print(f"Protocol '{args.protocol}' not found. Use --list to see available.")
            sys.exit(1)
        results = [airdrop.check(profile)]
    else:
        results = [a.check(profile) for a in list_airdrops()]

    portfolio = PortfolioValuator.rate(profile)
    display_wallet(profile, results, portfolio, show_json=args.json)


def start_server():
    try:
        import uvicorn
        cfg = Config()
        print(f"\n  🚀 AirDropScanner API running at http://{cfg.HOST}:{cfg.PORT}")
        print(f"  📖 Docs at http://{cfg.HOST if cfg.HOST != '0.0.0.0' else 'localhost'}:{cfg.PORT}/docs\n")
        uvicorn.run("airdrop_scanner.api:app", host=cfg.HOST, port=cfg.PORT, log_level="info")
    except ImportError:
        print("pip install 'airdrop-scanner[server]'")
        sys.exit(1)


def run():
    main()


if __name__ == "__main__":
    main()
