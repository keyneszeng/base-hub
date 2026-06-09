"""
数据库操作模块
"""
import aiosqlite
from datetime import datetime
from typing import List, Dict, Optional
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "base.db")


async def init_db():
    """初始化数据库"""
    async with aiosqlite.connect(DB_PATH) as db:
        # 创建合约表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS contracts (
                address TEXT PRIMARY KEY,
                label TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建 Gas 统计表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS gas_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_address TEXT NOT NULL,
                contract_label TEXT,
                total_gas_used INTEGER DEFAULT 0,
                total_tx_count INTEGER DEFAULT 0,
                daily_gas_used INTEGER DEFAULT 0,
                daily_tx_count INTEGER DEFAULT 0,
                date TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(contract_address, date)
            )
        """)
        
        # 创建每日快照表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS daily_snapshots (
                date TEXT PRIMARY KEY,
                total_gas_used INTEGER,
                total_tx_count INTEGER,
                active_contracts INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_gas_stats_date 
            ON gas_stats(date)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_gas_stats_total 
            ON gas_stats(total_gas_used DESC)
        """)
        
        await db.commit()
    
    print(f"数据库初始化完成：{DB_PATH}")


async def update_gas_stats(stats: Dict) -> None:
    """更新 Gas 统计数据"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO gas_stats 
            (contract_address, contract_label, total_gas_used, total_tx_count, 
             daily_gas_used, daily_tx_count, date, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            stats["contract_address"],
            stats["contract_label"],
            stats["total_gas_used"],
            stats["total_tx_count"],
            stats["daily_gas_used"],
            stats["daily_tx_count"],
            stats["date"],
        ))
        await db.commit()


async def get_total_rankings(limit: int = 50) -> List[Dict]:
    """获取总 Gas 消耗排行榜"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT 
                contract_address,
                contract_label,
                SUM(total_gas_used) as total_gas_used,
                SUM(total_tx_count) as total_tx_count,
                MAX(date) as last_updated
            FROM gas_stats
            GROUP BY contract_address
            ORDER BY total_gas_used DESC
            LIMIT ?
        """, (limit,))
        
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_daily_rankings(date: str, limit: int = 50) -> List[Dict]:
    """获取指定日期的 Gas 消耗排行榜"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT 
                contract_address,
                contract_label,
                daily_gas_used,
                daily_tx_count
            FROM gas_stats
            WHERE date = ?
            ORDER BY daily_gas_used DESC
            LIMIT ?
        """, (date, limit))
        
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_latest_date() -> Optional[str]:
    """获取最新的数据日期"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT MAX(date) as latest_date FROM gas_stats
        """)
        row = await cursor.fetchone()
        return row[0] if row else None


async def save_daily_snapshot(date: str, total_gas: int, total_tx: int, active_contracts: int) -> None:
    """保存每日快照"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO daily_snapshots 
            (date, total_gas_used, total_tx_count, active_contracts, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (date, total_gas, total_tx, active_contracts))
        await db.commit()


async def get_daily_snapshots(days: int = 30) -> List[Dict]:
    """获取最近 N 天的快照数据"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT * FROM daily_snapshots
            ORDER BY date DESC
            LIMIT ?
        """, (days,))
        
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def update_contract_label(address: str, label: str) -> None:
    """更新合约标签"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO contracts (address, label, category)
            VALUES (?, ?, ?)
        """, (address, label, ""))
        await db.commit()


async def get_contract_label(address: str) -> Optional[str]:
    """获取合约标签"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT label FROM contracts WHERE address = ?
        """, (address,))
        row = await cursor.fetchone()
        return row[0] if row else None