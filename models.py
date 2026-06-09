"""
数据模型定义
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class ContractInfo:
    """合约信息"""
    address: str
    label: str
    category: str = ""  # 类别：DEX, NFT, Lending, 等


@dataclass
class GasStat:
    """Gas 消耗统计"""
    contract_address: str
    contract_label: str
    total_gas_used: int
    total_tx_count: int
    daily_gas_used: int
    daily_tx_count: int
    date: str  # YYYY-MM-DD
    
    def to_dict(self):
        return {
            "contract_address": self.contract_address,
            "contract_label": self.contract_label,
            "total_gas_used": self.total_gas_used,
            "total_tx_count": self.total_tx_count,
            "daily_gas_used": self.daily_gas_used,
            "daily_tx_count": self.daily_tx_count,
            "date": self.date,
        }


@dataclass
class DailySnapshot:
    """每日快照"""
    date: str
    total_gas_used: int
    total_tx_count: int
    active_contracts: int
    created_at: datetime = None