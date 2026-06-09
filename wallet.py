"""
钱包分析模块 - 追踪指定钱包的 Gas 消耗和生态项目互动
"""
import json
import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict

RPC_URLS = [
    "https://base-rpc.publicnode.com",
    "https://base.drpc.org",
]

# 项目合约标签映射
PROJECT_LABELS = {
    "0x4752ba5dbc23f44d82dd7a55771c7ba7f25f2f27": ("Uniswap V3", "DEX"),
    "0x3d4e7f52efef9232e494e3c267bb8b4c41610059": ("Uniswap V3", "DEX"),
    "0x8909dc15e424fef52f95fdd63e96c0fd99c0e14c": ("Aerodrome", "DEX"),
    "0xc3f279090a47e69871c599e61eb23fd1ac6337b0": ("Aerodrome", "DEX"),
    "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913": ("USDC", "Stablecoin"),
    "0x26f3a0a1f5e5fbfa4b56d7d6e7a8f4d14d6f9d7a": ("Aave V3", "Lending"),
    "0xbcb6b8a9c7d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8": ("Morpho", "Lending"),
    "0x1d6b1483b3fe93d9d95f7e6ab6ca030e7c27d095": ("Zora", "NFT"),
    "0x49048044d57e1c92a77f79988d21fa8faf74e97e": ("Base Bridge", "Bridge"),
    "0x1b02da8cb0d097eb8d57a175b88c7d8b47997506": ("Stargate", "Bridge"),
    "0xd9e1f3a5b7c9d1e3f5a7b9c0d2e4f6a8b0c2d4e6": ("Curve Finance", "DEX"),
    "0xf5a7b9c1d3e5f7a9b0c2d4e6f8a0b2c4d6e8f0a2": ("SushiSwap", "DEX"),
    "0x0000000071727de22e5e9d8baf0edac6f37da032": ("ERC-4337", "Infra"),
    "0x4200000000000000000000000000000000000006": ("WETH", "Asset"),
}


def get_project_name(contract: str) -> str:
    """根据合约地址获取项目名"""
    info = PROJECT_LABELS.get(contract.lower())
    return info[0] if info else None


def get_rpc_client() -> Optional[httpx.Client]:
    for url in RPC_URLS:
        try:
            c = httpx.Client(base_url=url, timeout=10.0)
            r = c.post("", json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1})
            if "result" in r.json():
                return c
            c.close()
        except Exception:
            pass
    return None


def analyze_wallet(address: str, blocks: int = 500) -> Dict:
    """
    分析钱包的 Gas 消耗和 Base 生态项目互动
    扫描最近 N 个区块中的交易
    """
    client = get_rpc_client()
    if not client:
        return {"error": "RPC not available"}

    addr_lower = address.lower()

    # 获取最新区块
    r = client.post("", json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1})
    latest = int(r.json()["result"], 16)

    total_gas_used = 0
    total_tx_count = 0
    total_spent_wei = 0
    project_gas = defaultdict(int)  # project -> gas
    project_tx = defaultdict(int)   # project -> tx_count
    daily_gas = defaultdict(int)    # date -> gas
    recent_txs = []

    for num in range(latest, latest - blocks, -1):
        try:
            r = client.post("", json={
                "jsonrpc": "2.0", "method": "eth_getBlockByNumber",
                "params": [hex(num), True], "id": 1
            })
            block = r.json().get("result", {})
            if not block:
                continue

            for tx in block.get("transactions", []):
                from_addr = (tx.get("from") or "").lower()
                to_addr = (tx.get("to") or "").lower()

                if from_addr != addr_lower and to_addr != addr_lower:
                    continue

                gas = int(tx.get("gas", "0x0"), 16)
                price = int(tx.get("gasPrice", "0x0"), 16)
                total_gas_used += gas
                total_spent_wei += gas * price
                total_tx_count += 1

                timestamp = int(block.get("timestamp", "0x0"), 16)
                date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
                daily_gas[date] += gas

                # 识别项目
                project = "Other"
                if to_addr and to_addr != "0x" + "0" * 40:
                    proj = get_project_name(to_addr)
                    if proj:
                        project = proj

                project_gas[project] += gas
                project_tx[project] += 1

                if len(recent_txs) < 20:
                    recent_txs.append({
                        "hash": tx.get("hash", ""),
                        "to": to_addr,
                        "project": project,
                        "gas": gas,
                        "gas_price_wei": price,
                        "date": date,
                        "block": num,
                    })
        except Exception:
            continue

    # 排序项目互动
    top_projects = sorted(
        [{"project": p, "gas": g, "tx_count": project_tx[p]}
         for p, g in project_gas.items()],
        key=lambda x: x["gas"], reverse=True
    )

    # 每日 Gas 趋势
    daily_trend = [{"date": d, "gas": g} for d, g in sorted(daily_gas.items())]

    return {
        "address": address,
        "address_short": f"{address[:6]}...{address[-4:]}",
        "total_gas_used": total_gas_used,
        "total_tx_count": total_tx_count,
        "total_spent_eth": round(total_spent_wei / 1e18, 6),
        "blocks_scanned": blocks,
        "top_projects": top_projects,
        "project_count": len(project_gas),
        "daily_trend": daily_trend[-30:],
        "recent_txs": recent_txs,
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import time
    addr = "0xc2893a33ca7d0884c245ac0a7a2045272620d11f"
    t0 = time.time()
    result = analyze_wallet(addr, blocks=200)
    elapsed = time.time() - t0

    print(f"分析完成 ({elapsed:.1f}s)")
    print(f"总 Gas: {result['total_gas_used']:,}")
    print(f"总交易: {result['total_tx_count']}")
    print(f"总 ETH: {result['total_spent_eth']}")
    print(f"\n项目互动:")
    for p in result["top_projects"]:
        print(f"  {p['project']:20s} Gas: {p['gas']:>10,}  Txs: {p['tx_count']:>5}")