"""
模拟数据生成器 - 生成真实的 Base 生态 Gas 数据用于展示
当没有配置 API Key 时使用此模式
"""
import random
from datetime import datetime, timedelta

# Base 公链重点生态项目
BASE_ECOSYSTEM_PROJECTS = [
    # DEX / AMM
    ("0x4752ba5dbc23f44d82dd7a55771c7ba7f25f2f27", "Uniswap V3: Router 2", "DEX"),
    ("0x3d4e7f52efef9232e494e3c267bb8b4c41610059", "Uniswap V3: Quoter", "DEX"),
    ("0x8909dc15e424fef52f95fdd63e96c0fd99c0e14c", "Aerodrome: Router", "DEX"),
    ("0xc3f279090a47e69871c599e61eb23fd1ac6337b0", "Aerodrome: Position Manager", "DEX"),
    ("0xba942e7923bff2a5b2b027e2d0b4c82a9f2ac4e7", "Moonwell: Router", "Lending"),
    ("0x8562b8e6a2a2a8b9a4d8e2f3a4b5c6d7e8f9a0b1", "Velodrome: Router V2", "DEX"),
    
    # Lending / Money Markets
    ("0x26f3a0a1f5e5fbfa4b56d7d6e7a8f4d14d6f9d7a", "Aave V3: Pool", "Lending"),
    ("0xa238dd76c8b2f0e5bea8e6d6f5d0f5e6d7f8a9b0", "Compound III: Comet", "Lending"),
    ("0x1230d35e8c28a569b8e4d715b9f4a8b7c6d5e4f3", "Seamless Protocol", "Lending"),
    ("0xbcb6b8a9c7d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8", "Morpho: Blue", "Lending"),
    
    # Stablecoin / Bridged Assets
    ("0x833589fcd6edb6e08f4c7c32d4f71b54bda02913", "USDC (Bridged)", "Stablecoin"),
    ("0xbdba74a7e6f7b9c8d9e0f1a2b3c4d5e6f7a8b9c0", "DAI (Bridged)", "Stablecoin"),
    ("0x70e47c843e0f6ab0991a3189c28f2957eb6a8a7b", "wETH", "Asset"),
    ("0x4200000000000000000000000000000000000006", "WETH (Base)", "Asset"),
    ("0x4200000000000000000000000000000000000010", "cbETH", "Asset"),
    
    # Bridge
    ("0x49048044d57e1c92a77f79988d21fa8faf74e97e", "Base: Standard Bridge", "Bridge"),
    ("0x5d3a1ff2b6b6899a8e4f5c6d7e8f9a0b1c2d3e4f", "Across Protocol: Bridge", "Bridge"),
    ("0x1b02da8cb0d097eb8d57a175b88c7d8b47997506", "Stargate: Bridge", "Bridge"),
    ("0xc8eaaf5d2b8a3b5c6d7e8f9a0b1c2d3e4f5a6b7c", "Synapse: Bridge", "Bridge"),
    
    # NFT / Social / Gaming
    ("0x1d6b1483b3fe93d9d95f7e6ab6ca030e7c27d095", "Zora: ERC721Drop", "NFT"),
    ("0x3a2d3e4e8b9d8b9a5e5f8c8d8e8f8g8h8i8j8k8l", "Friend.tech: Shares", "Social"),
    ("0x1234567890abcdef1234567890abcdef12345678", "Base Name Service", "Infra"),
    ("0xabcdef1234567890abcdef1234567890abcdef12", "Parallel: Planetfall", "Gaming"),
    ("0x9876543210fedcba9876543210fedcba98765432", "Pixelmon: Shards", "Gaming"),
    
    # Yield / Vaults
    ("0xa1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0", "Yearn V3: Vault", "Yield"),
    ("0xb0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9", "Beefy: AutoCompound", "Yield"),
    ("0xc0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9", "Sommelier: Vaults", "Yield"),
    
    # Perp DEX
    ("0xd0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9", "dYdX: Perpetual", "Perp DEX"),
    ("0xe0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9", "Hyperliquid: Perp", "Perp DEX"),
    ("0xf0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a0", "Vertex: Perp", "Perp DEX"),
    
    # DeFi Infra
    ("0x1111111111111111111111111111111111111111", "1inch: Router V5", "DeFi"),
    ("0x2222222222222222222222222222222222222222", "CowSwap: Settlement", "DeFi"),
    ("0x3333333333333333333333333333333333333333", "Pendle: Router", "Yield"),
    
    # New Popular Projects
    ("0x4444444444444444444444444444444444444444", "Basepaint: Art", "NFT"),
    ("0x5555555555555555555555555555555555555555", "Flooring Protocol", "NFT"),
    ("0x6666666666666666666666666666666666666666", "RPS League", "Gaming"),
    
    # Additional Active Projects
    ("0xb5d5f8c2d7e3a9f1b4c6a0e8d2f7e9b3c5a1d4f6", "Aura Finance", "Yield"),
    ("0xc7e9d3f1a5b8c0d2e4f6a8b9c1d3e5f7a9b0c2d4", "Convex Finance", "Yield"),
    ("0xd9e1f3a5b7c9d1e3f5a7b9c0d2e4f6a8b0c2d4e6", "Curve Finance: Pool", "DEX"),
    ("0xe3f5a7b9c1d3e5f7a9b0c2d4e6f8a0b2c4d6e8f0", "Balancer: Vault", "DEX"),
    ("0xf5a7b9c1d3e5f7a9b0c2d4e6f8a0b2c4d6e8f0a2", "SushiSwap: Router", "DEX"),
    ("0xa7b9c1d3e5f7a9b0c2d4e6f8a0b2c4d6e8f0a2b4", "Maverick: Router", "DEX"),
    ("0xb9c1d3e5f7a9b0c2d4e6f8a0b2c4d6e8f0a2b4c6", "Camelot: DEX", "DEX"),
    ("0xc1d3e5f7a9b0c2d4e6f8a0b2c4d6e8f0a2b4c6d8", "Overnight Finance", "Yield"),
]

# Gas 范围配置（按类别）
CATEGORY_GAS_RANGES = {
    "DEX": {"min": 500000, "max": 500000000},
    "Lending": {"min": 200000, "max": 300000000},
    "Stablecoin": {"min": 100000, "max": 100000000},
    "Asset": {"min": 50000, "max": 80000000},
    "Bridge": {"min": 300000, "max": 200000000},
    "NFT": {"min": 100000, "max": 150000000},
    "Social": {"min": 50000, "max": 80000000},
    "Infra": {"min": 50000, "max": 30000000},
    "Gaming": {"min": 100000, "max": 90000000},
    "Yield": {"min": 100000, "max": 120000000},
    "Perp DEX": {"min": 200000, "max": 300000000},
    "DeFi": {"min": 100000, "max": 150000000},
}


def generate_historical_gas_data(days_back: int = 90) -> list:
    """
    生成模拟的 Gas 消耗历史数据
    
    返回格式：[{contract_address, contract_label, category, date, gas_used, tx_count}, ...]
    """
    records = []
    today = datetime.now().strftime("%Y-%m-%d")
    
    for addr, label, category in BASE_ECOSYSTEM_PROJECTS:
        gas_range = CATEGORY_GAS_RANGES.get(category, {"min": 10000, "max": 50000000})
        
        # 基础日 Gas 消耗量
        base_daily_gas = random.randint(gas_range["min"], gas_range["max"])
        base_daily_tx = random.randint(50, 5000)
        
        # 过去 days_back 天的数据
        daily_data = []
        for day_offset in range(days_back):
            date = (datetime.now() - timedelta(days=day_offset)).strftime("%Y-%m-%d")
            
            # 按天变化 - 添加 20% 随机波动和增长趋势
            trend_factor = 1 + (days_back - day_offset) * 0.001  # 早期数据稍微低一些
            random_factor = random.uniform(0.7, 1.3)
            daily_gas = int(base_daily_gas * trend_factor * random_factor)
            daily_tx = int(base_daily_tx * random_factor)
            
            daily_data.append({
                "contract_address": addr,
                "contract_label": label,
                "category": category,
                "date": date,
                "daily_gas_used": daily_gas,
                "daily_tx_count": daily_tx,
            })
        
        records.extend(daily_data)
    
    return records


def generate_aggregated_stats(historical_data: list) -> dict:
    """
    从历史数据生成聚合统计
    返回 {total_rankings, daily_rankings, snapshots}
    """
    from collections import defaultdict
    
    # 按合约地址 + 标签聚合
    contract_agg = defaultdict(lambda: {
        "total_gas_used": 0, "total_tx_count": 0, 
        "label": "", "category": "",
        "daily": defaultdict(lambda: {"gas": 0, "tx": 0})
    })
    
    for record in historical_data:
        addr = record["contract_address"]
        agg = contract_agg[addr]
        agg["label"] = record["contract_label"]
        agg["category"] = record["category"]
        agg["total_gas_used"] += record["daily_gas_used"]
        agg["total_tx_count"] += record["daily_tx_count"]
        agg["daily"][record["date"]]["gas"] += record["daily_gas_used"]
        agg["daily"][record["date"]]["tx"] += record["daily_tx_count"]
    
    # 按日期聚合快照
    date_agg = defaultdict(lambda: {"total_gas": 0, "total_tx": 0})
    for record in historical_data:
        date_agg[record["date"]]["total_gas"] += record["daily_gas_used"]
        date_agg[record["date"]]["total_tx"] += record["daily_tx_count"]
    
    # 总排行榜
    total_rankings = [
        {
            "contract_address": addr,
            "contract_label": data["label"],
            "total_gas_used": data["total_gas_used"],
            "total_tx_count": data["total_tx_count"],
            "category": data["category"],
            "contract_address_url": f"https://basescan.org/address/{addr}",
        }
        for addr, data in contract_agg.items()
    ]
    total_rankings.sort(key=lambda x: x["total_gas_used"], reverse=True)
    
    # 每日排行榜（最新日期）
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    latest_date = yesterday  # 最新有数据的是昨天
    
    daily_rankings = [
        {
            "contract_address": addr,
            "contract_label": data["label"],
            "daily_gas_used": data["daily"][latest_date]["gas"],
            "daily_tx_count": data["daily"][latest_date]["tx"],
            "category": data["category"],
        }
        for addr, data in contract_agg.items()
    ]
    daily_rankings.sort(key=lambda x: x["daily_gas_used"], reverse=True)
    
    # 每日快照（用于趋势图）
    snapshots = [
        {
            "date": date,
            "total_gas_used": agg["total_gas"],
            "total_tx_count": agg["total_tx"],
            "active_contracts": sum(1 for r in historical_data if r["date"] == date and r["daily_gas_used"] > 0),
        }
        for date, agg in sorted(date_agg.items(), key=lambda x: x[0])
    ]
    
    return {
        "total_rankings": total_rankings,
        "daily_rankings": daily_rankings,
        "snapshots": snapshots,
        "generated_at": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import json
    data = generate_historical_gas_data(90)
    stats = generate_aggregated_stats(data)
    print(f"生成了 {len(data)} 条历史记录")
    print(f"总排行榜: {len(stats['total_rankings'])} 个项目")
    print(f"每日排行榜: {len(stats['daily_rankings'])} 个项目")
    print(f"趋势快照: {len(stats['snapshots'])} 天")
    
    # 打印 Top 5
    for i, item in enumerate(stats["total_rankings"][:5]):
        print(f"  #{i+1} {item['contract_label']}: {item['total_gas_used']:,} Gas")