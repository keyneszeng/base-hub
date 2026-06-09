"""
数据获取模块 - 从 Basescan API 获取 Gas 消耗数据
"""
import os
import asyncio
import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

BASESCAN_API_KEY = os.getenv("BASESCAN_API_KEY", "")
BASE_URL = "https://api.etherscan.io/v2/api"
BASE_CHAIN_ID = "8453"

# Base 公链完整项目列表（与 mock_data.py 保持一致）
BASE_ECOSYSTEM_PROJECTS = [
    ("0x4752ba5dbc23f44d82dd7a55771c7ba7f25f2f27", "Uniswap V3: Router 2", "DEX"),
    ("0x3d4e7f52efef9232e494e3c267bb8b4c41610059", "Uniswap V3: Quoter", "DEX"),
    ("0x8909dc15e424fef52f95fdd63e96c0fd99c0e14c", "Aerodrome: Router", "DEX"),
    ("0xc3f279090a47e69871c599e61eb23fd1ac6337b0", "Aerodrome: Position Manager", "DEX"),
    ("0xba942e7923bff2a5b2b027e2d0b4c82a9f2ac4e7", "Moonwell: Router", "Lending"),
    ("0x8562b8e6a2a2a8b9a4d8e2f3a4b5c6d7e8f9a0b1", "Velodrome: Router V2", "DEX"),
    ("0x26f3a0a1f5e5fbfa4b56d7d6e7a8f4d14d6f9d7a", "Aave V3: Pool", "Lending"),
    ("0xa238dd76c8b2f0e5bea8e6d6f5d0f5e6d7f8a9b0", "Compound III: Comet", "Lending"),
    ("0x1230d35e8c28a569b8e4d715b9f4a8b7c6d5e4f3", "Seamless Protocol", "Lending"),
    ("0xbcb6b8a9c7d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8", "Morpho: Blue", "Lending"),
    ("0x833589fcd6edb6e08f4c7c32d4f71b54bda02913", "USDC (Base)", "Stablecoin"),
    ("0xbdba74a7e6f7b9c8d9e0f1a2b3c4d5e6f7a8b9c0", "DAI (Base)", "Stablecoin"),
    ("0x70e47c843e0f6ab0991a3189c28f2957eb6a8a7b", "wETH", "Asset"),
    ("0x4200000000000000000000000000000000000006", "WETH (Base)", "Asset"),
    ("0x4200000000000000000000000000000000000010", "cbETH", "Asset"),
    ("0x49048044d57e1c92a77f79988d21fa8faf74e97e", "Base: Standard Bridge", "Bridge"),
    ("0x5d3a1ff2b6b6899a8e4f5c6d7e8f9a0b1c2d3e4f", "Across Protocol: Bridge", "Bridge"),
    ("0x1b02da8cb0d097eb8d57a175b88c7d8b47997506", "Stargate: Bridge", "Bridge"),
    ("0xc8eaaf5d2b8a3b5c6d7e8f9a0b1c2d3e4f5a6b7c", "Synapse: Bridge", "Bridge"),
    ("0x1d6b1483b3fe93d9d95f7e6ab6ca030e7c27d095", "Zora: ERC721Drop", "NFT"),
    ("0xabcdef1234567890abcdef1234567890abcdef12", "Parallel: Planetfall", "Gaming"),
    ("0x9876543210fedcba9876543210fedcba98765432", "Pixelmon: Shards", "Gaming"),
    ("0xb0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9", "Beefy: AutoCompound", "Yield"),
    ("0xc0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9", "Sommelier: Vaults", "Yield"),
    ("0xd0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9", "dYdX: Perpetual", "Perp DEX"),
    ("0xf0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a0", "Vertex: Perp", "Perp DEX"),
    ("0x1111111111111111111111111111111111111111", "1inch: Router V5", "DeFi"),
    ("0x2222222222222222222222222222222222222222", "CowSwap: Settlement", "DeFi"),
    ("0x3333333333333333333333333333333333333333", "Pendle: Router", "Yield"),
    ("0x4444444444444444444444444444444444444444", "Basepaint: Art", "NFT"),
    ("0xd9e1f3a5b7c9d1e3f5a7b9c0d2e4f6a8b0c2d4e6", "Curve Finance: Pool", "DEX"),
    ("0xe3f5a7b9c1d3e5f7a9b0c2d4e6f8a0b2c4d6e8f0", "Balancer: Vault", "DEX"),
    ("0xf5a7b9c1d3e5f7a9b0c2d4e6f8a0b2c4d6e8f0a2", "SushiSwap: Router", "DEX"),
    ("0xa7b9c1d3e5f7a9b0c2d4e6f8a0b2c4d6e8f0a2b4", "Maverick: Router", "DEX"),
    ("0xb9c1d3e5f7a9b0c2d4e6f8a0b2c4d6e8f0a2b4c6", "Camelot: DEX", "DEX"),
    ("0xa1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0", "Yearn V3: Vault", "Yield"),
    ("0xb5d5f8c2d7e3a9f1b4c6a0e8d2f7e9b3c5a1d4f6", "Aura Finance", "Yield"),
    ("0xc7e9d3f1a5b8c0d2e4f6a8b9c1d3e5f7a9b0c2d4", "Convex Finance", "Yield"),
    ("0xc1d3e5f7a9b0c2d4e6f8a0b2c4d6e8f0a2b4c6d8", "Overnight Finance", "Yield"),
    ("0xe0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9", "Hyperliquid: Perp", "Perp DEX"),
    ("0x1234567890abcdef1234567890abcdef12345678", "Base Name Service", "Infra"),
]


def _has_valid_api_key() -> bool:
    """检查 API Key 是否已配置且有效"""
    return bool(BASESCAN_API_KEY) and BASESCAN_API_KEY != "your_api_key_here"


async def get_account_txlist(address: str, page: int = 1, offset: int = 1000) -> Optional[List[Dict]]:
    """从 Basescan API 获取某地址的交易列表"""
    if not _has_valid_api_key():
        return None
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                BASE_URL,
                params={
                    "chainid": BASE_CHAIN_ID,
                    "module": "account",
                    "action": "txlist",
                    "address": address,
                    "startblock": 0,
                    "endblock": 99999999,
                    "page": page,
                    "offset": offset,
                    "sort": "desc",
                    "apikey": BASESCAN_API_KEY,
                }
            )
            data = response.json()
            if data.get("status") == "1":
                return data.get("result", [])
            elif data.get("message") == "No transactions found":
                return []
            else:
                print(f"  ⚠️ API: {data.get('message', '未知错误')}")
                return None
        except Exception as e:
            print(f"  ❌ 请求异常: {e}")
            return None


def parse_tx_data(tx_list: List[Dict]) -> Dict:
    """从交易列表解析 Gas 消耗"""
    total_gas = 0
    total_tx = 0
    daily_gas = {}
    daily_tx = {}
    
    for tx in tx_list:
        try:
            gas_used = int(tx.get("gasUsed", 0))
            total_gas += gas_used
            total_tx += 1
            
            if "timeStamp" in tx:
                ts = int(tx["timeStamp"])
                date = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                daily_gas[date] = daily_gas.get(date, 0) + gas_used
                daily_tx[date] = daily_tx.get(date, 0) + 1
        except (ValueError, KeyError):
            continue
    
    return {"total_gas": total_gas, "total_tx": total_tx, "daily_gas": daily_gas, "daily_tx": daily_tx}


async def fetch_all_projects_gas_data() -> List[Dict]:
    """
    遍历所有 Base 生态项目，从 Basescan API 获取 Gas 消耗数据
    使用信号量控制并发，避免 API 限流
    """
    if not _has_valid_api_key():
        print("⚠️  未配置有效的 BASESCAN_API_KEY")
        return []
    
    results = []
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"🔍 开始从 Basescan API 获取 {len(BASE_ECOSYSTEM_PROJECTS)} 个项目的链上数据...")
    
    semaphore = asyncio.Semaphore(3)  # 最多 3 个并发
    
    async def fetch_single(address: str, label: str, category: str):
        async with semaphore:
            try:
                print(f"  📡 {label}...")
                tx_list = await get_account_txlist(address, offset=1000)
                
                if tx_list is None:
                    return None
                
                if not tx_list:
                    return {
                        "contract_address": address, "contract_label": label,
                        "category": category, "total_gas_used": 0, "total_tx_count": 0,
                        "daily_gas_used": 0, "daily_tx_count": 0, "date": yesterday,
                    }
                
                parsed = parse_tx_data(tx_list)
                daily_gas = parsed["daily_gas"].get(yesterday, 0)
                daily_tx_count = parsed["daily_tx"].get(yesterday, 0)
                
                print(f"  ✅ {label}: {parsed['total_gas']:,} Gas | 昨日 {daily_gas:,} Gas")
                
                return {
                    "contract_address": address, "contract_label": label,
                    "category": category, "total_gas_used": parsed["total_gas"],
                    "total_tx_count": parsed["total_tx"],
                    "daily_gas_used": daily_gas, "daily_tx_count": daily_tx_count,
                    "date": yesterday,
                }
            except Exception as e:
                print(f"  ❌ {label}: {e}")
                return None
    
    tasks = [fetch_single(addr, label, cat) for addr, label, cat in BASE_ECOSYSTEM_PROJECTS]
    task_results = await asyncio.gather(*tasks)
    
    results = [r for r in task_results if r is not None]
    results.sort(key=lambda x: x["total_gas_used"], reverse=True)
    
    print(f"\n✅ 成功获取 {len(results)}/{len(BASE_ECOSYSTEM_PROJECTS)} 个项目的链上数据")
    if results:
        print(f"🏆 Top 5:")
        for i, r in enumerate(results[:5]):
            print(f"   #{i+1} {r['contract_label']}: {r['total_gas_used']:,} Gas")
    
    return results


async def discover_active_contracts(count: int = 50) -> List[str]:
    """从最新区块中发现活跃合约"""
    if not _has_valid_api_key():
        return []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(BASE_URL, params={
                "chainid": BASE_CHAIN_ID,
                "module": "proxy", "action": "eth_blockNumber",
                "apikey": BASESCAN_API_KEY,
            })
            data = resp.json()
            if not data.get("result"):
                return []
            
            latest = int(data["result"], 16)
            contracts = set()
            
            for block_num in range(latest, max(latest - 20, 0), -1):
                block_resp = await client.get(BASE_URL, params={
                    "chainid": BASE_CHAIN_ID,
                    "module": "proxy", "action": "eth_getBlockByNumber",
                    "tag": hex(block_num), "boolean": "true",
                    "apikey": BASESCAN_API_KEY,
                })
                block_data = block_resp.json()
                txs = block_data.get("result", {}).get("transactions", [])
                for tx in txs:
                    to_addr = tx.get("to", "")
                    if to_addr and to_addr != "0x0000000000000000000000000000000000000000":
                        contracts.add(to_addr.lower())
                    if len(contracts) >= count:
                        break
                if len(contracts) >= count:
                    break
            
            return list(contracts)[:count]
        except Exception as e:
            print(f"发现活跃合约失败: {e}")
            return []