"""
Base 生态 Gas 消耗看板 - FastAPI 应用
"""
import os
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import database as db
from data_fetcher import fetch_all_projects_gas_data
from mock_data import generate_historical_gas_data, generate_aggregated_stats

load_dotenv()

# API Key 检查
RAW_KEY = os.getenv("BASESCAN_API_KEY", "").strip()
USE_MOCK = True  # 默认使用模拟数据（Base 链需要 Etherscan 付费计划才能获取数据）

if RAW_KEY and RAW_KEY != "your_api_key_here":
    print("ℹ️  BASESCAN_API_KEY 已配置，但 Base 链数据需要 Etherscan 付费计划")
    print("ℹ️  当前使用模拟数据展示 44 个 Base 项目 × 90 天历史")
else:
    print("ℹ️  未配置 BASESCAN_API_KEY，使用模拟数据展示")

# 全局数据缓存
cache = {
    "total_rankings": [],
    "daily_rankings": [],
    "snapshots": [],
    "last_update": None,
    "data_source": "mock" if USE_MOCK else "basescan",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    await db.init_db()
    
    if USE_MOCK:
        print("⚠️  未配置 BASESCAN_API_KEY，使用模拟数据展示")
        print("💡 要获取真实数据，请配置 .env 文件中的 BASESCAN_API_KEY")
    else:
        print("✅ 已配置 BASESCAN_API_KEY，将获取真实链上数据")
    
    # 启动时立即填充数据
    asyncio.create_task(initial_data_load())
    
    # 定时数据获取任务
    asyncio.create_task(periodic_data_fetch())
    
    yield
    
    print("应用关闭")


async def initial_data_load():
    """初始数据加载"""
    if USE_MOCK:
        await load_mock_data()
    else:
        await fetch_live_data()


async def periodic_data_fetch():
    """定期获取数据"""
    while True:
        await asyncio.sleep(300)  # 5分钟
        try:
            if USE_MOCK:
                # 模拟数据定时刷新（添加随机波动）
                await load_mock_data()
            else:
                await fetch_live_data()
            print(f"[{datetime.now()}] 数据更新完成")
        except Exception as e:
            print(f"数据更新失败：{e}")


async def load_mock_data():
    """加载模拟数据"""
    global cache
    
    historical = generate_historical_gas_data(days_back=90)
    stats = generate_aggregated_stats(historical)
    
    cache["total_rankings"] = stats["total_rankings"]
    cache["daily_rankings"] = stats["daily_rankings"]
    cache["snapshots"] = stats["snapshots"]
    cache["last_update"] = datetime.now()
    cache["data_source"] = "mock"
    
    # 同时保存到数据库
    for record in historical:
        await db.update_gas_stats({
            "contract_address": record["contract_address"],
            "contract_label": record["contract_label"],
            "total_gas_used": sum(r["daily_gas_used"] for r in historical if r["contract_address"] == record["contract_address"]),
            "total_tx_count": sum(r["daily_tx_count"] for r in historical if r["contract_address"] == record["contract_address"]),
            "daily_gas_used": record["daily_gas_used"],
            "daily_tx_count": record["daily_tx_count"],
            "date": record["date"],
        })
    
    print(f"模拟数据已加载: {len(cache['total_rankings'])} 个项目, {len(cache['snapshots'])} 天趋势")


async def fetch_live_data():
    """获取真实链上数据"""
    global cache
    
    contracts = await fetch_all_projects_gas_data()
    
    if not contracts:
        print("⚠️  真实数据获取失败，使用模拟数据兜底")
        await load_mock_data()
        return
    
    for stat in contracts:
        await db.update_gas_stats(stat)
    
    cache["total_rankings"] = await db.get_total_rankings(limit=50)
    
    latest_date = await db.get_latest_date()
    if latest_date:
        cache["daily_rankings"] = await db.get_daily_rankings(latest_date, limit=50)
    
    cache["last_update"] = datetime.now()
    cache["data_source"] = "basescan"


app = FastAPI(
    title="Base 生态 Gas 消耗看板",
    description="展示 Base 链上生态项目的 Gas 消耗排行榜",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def root():
    """返回看板页面"""
    with open(os.path.join(os.path.dirname(__file__), "templates", "index.html"), "r", encoding="utf-8") as f:
        html = f.read()
    return html


@app.get("/api/gas-stats/total")
async def get_total_gas_stats(limit: int = Query(50, ge=1, le=100)):
    """获取总 Gas 消耗排行榜"""
    if not cache["total_rankings"]:
        if USE_MOCK:
            await load_mock_data()
        else:
            await fetch_live_data()
    
    return cache["total_rankings"][:limit]


@app.get("/api/gas-stats/daily")
async def get_daily_gas_stats(date: Optional[str] = None, limit: int = Query(50, ge=1, le=100)):
    """获取每日 Gas 消耗排行榜"""
    if not cache["daily_rankings"]:
        if USE_MOCK:
            await load_mock_data()
        else:
            await fetch_live_data()
            return await get_daily_gas_stats(date, limit)
    
    return cache["daily_rankings"][:limit]


@app.get("/api/gas-stats/trend")
async def get_gas_trend(days: int = Query(30, ge=1, le=90)):
    """获取 Gas 消耗趋势"""
    if not cache["snapshots"]:
        if USE_MOCK:
            await load_mock_data()
    
    return cache["snapshots"][-days:]


@app.get("/api/gas-stats/by-category")
async def get_gas_by_category():
    """按类别统计 Gas 消耗"""
    if not cache["total_rankings"]:
        if USE_MOCK:
            await load_mock_data()
    
    from collections import defaultdict
    category_data = defaultdict(lambda: {"total_gas": 0, "total_tx": 0, "count": 0})
    
    for item in cache["total_rankings"]:
        cat = item.get("category", "Uncategorized")
        category_data[cat]["total_gas"] += item["total_gas_used"]
        category_data[cat]["total_tx"] += item["total_tx_count"]
        category_data[cat]["count"] += 1
    
    return [
        {
            "category": cat,
            "total_gas": data["total_gas"],
            "total_tx": data["total_tx"],
            "count": data["count"],
        }
        for cat, data in sorted(category_data.items(), key=lambda x: x[1]["total_gas"], reverse=True)
    ]


@app.post("/api/fetch")
async def trigger_fetch():
    """手动触发数据获取"""
    try:
        if USE_MOCK:
            await load_mock_data()
        else:
            await fetch_live_data()
        return {
            "status": "success",
            "message": "数据获取完成",
            "source": cache["data_source"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def get_status():
    """获取服务状态"""
    return {
        "status": "running",
        "last_update": cache["last_update"].isoformat() if cache["last_update"] else None,
        "total_rankings_count": len(cache["total_rankings"]),
        "daily_rankings_count": len(cache["daily_rankings"]),
        "data_source": cache["data_source"],
        "mock_data": USE_MOCK,
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8002))
    
    print(f"🚀 Base Gas Dashboard 启动中...")
    print(f"📊 数据模式: {'模拟数据' if USE_MOCK else 'Basescan 实时数据'}")
    if USE_MOCK:
        print(f"💡 提示: 配置 BASESCAN_API_KEY 后重启即可使用真实数据")
    print(f"🌐 访问地址: http://localhost:{port}")
    
    uvicorn.run(app, host=host, port=port)