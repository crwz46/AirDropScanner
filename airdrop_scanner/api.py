from typing import Optional, List

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .engine import list_airdrops, get_airdrop, PortfolioValuator
from .fetcher import WalletFetcher
from .config import Config

app = FastAPI(
    title="AirDropScanner API",
    description="Multi-protocol airdrop eligibility checker — scan any Ethereum wallet",
    version="1.0.0",
    contact={"name": "crwz46"},
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    airdrops = [{"name": a.name, "chain": a.chain, "icon": a.icon, "rules": len(a.rules)}
                for a in list_airdrops()]
    return {
        "service": "AirDropScanner",
        "version": "1.0.0",
        "protocols": len(airdrops),
        "airdrops": airdrops,
        "endpoints": {
            "scan": "/scan/{address}?protocol=arbitrum&tier=2&json=true",
            "protocols": "/protocols",
            "docs": "/docs",
        },
    }


def _serialize_eligibility(result) -> dict:
    return {
        "protocol": result.protocol,
        "chain": result.chain,
        "icon": result.icon,
        "eligible": result.eligible,
        "score": result.score,
        "passed": result.passed,
        "total": result.total,
        "rules": [
            {"name": r.name, "description": r.description,
             "passed": r.passed, "detail": r.detail}
            for r in result.rules
        ],
    }


@app.get("/scan/{address}")
async def scan_address(
    address: str,
    protocol: Optional[str] = Query(None),
    tier: Optional[int] = Query(None, ge=0, le=4),
    json_format: bool = Query(True, alias="json"),
):
    if not address.startswith("0x"):
        address = "0x" + address

    fetcher = WalletFetcher()
    try:
        profile = fetcher.fetch(address, tier=tier)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if protocol:
        airdrop = get_airdrop(protocol)
        if not airdrop:
            raise HTTPException(status_code=404,
                                detail=f"Protocol '{protocol}' not found")
        results = [airdrop.check(profile)]
    else:
        results = [a.check(profile) for a in list_airdrops()]

    portfolio = PortfolioValuator.rate(profile)

    return {
        "wallet": profile.address,
        "total_tx": profile.total_tx,
        "total_volume_eth": profile.total_volume_eth,
        "chains": list(profile.chains.keys()),
        "protocols_used": profile.protocols_used,
        "wallet_age_days": profile.wallet_age_days,
        "portfolio": portfolio,
        "results": [_serialize_eligibility(r) for r in results],
    }


@app.get("/protocols")
async def list_protocols():
    airdrops = list_airdrops()
    return {
        "count": len(airdrops),
        "protocols": [
            {
                "name": a.name,
                "chain": a.chain,
                "icon": a.icon,
                "criteria_count": len(a.rules),
                "criteria": [{"name": r.name, "description": r.description} for r in a.rules],
            }
            for a in sorted(airdrops, key=lambda x: x.name)
        ],
    }


@app.get("/health")
async def health():
    cfg = Config()
    return {
        "status": "ok",
        "live_data": cfg.has_etherscan_key(),
        "protocols": len(list_airdrops()),
    }
