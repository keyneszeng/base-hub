# Base 生态 Gas 消耗看板

Base 公链生态项目 Gas 消耗排行榜看板，展示生态项目的总 Gas 消耗和每日 Gas 消耗。

## 功能特性

- 📊 总 Gas 消耗排行榜（所有时间）
- 📈 每日 Gas 消耗排行榜
- 🏷️ 智能合约标签识别
- 🔄 自动数据更新
- 📱 响应式设计

## 技术栈

- **后端**: Python FastAPI
- **数据库**: SQLite
- **数据源**: Basescan API
- **前端**: HTML + TailwindCSS + Alpine.js

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

在 `.env` 文件中设置你的 Basescan API Key：

```
BASESCAN_API_KEY=your_api_key_here
```

获取 API Key: https://basescan.org/myapikey

### 3. 运行服务

```bash
python main.py
```

访问 http://localhost:8000 查看看板

## 项目结构

```
base-gas-dashboard/
├── main.py              # FastAPI 应用入口
├── data_fetcher.py      # 数据获取模块
├── database.py          # 数据库操作
├── models.py            # 数据模型
├── requirements.txt     # Python 依赖
├── .env                 # 环境变量配置
├── base.db              # SQLite 数据库
└── templates/
    └── index.html       # 前端看板页面
```

## API 端点

- `GET /` - 看板页面
- `GET /api/gas-stats/total` - 总 Gas 消耗统计
- `GET /api/gas-stats/daily` - 每日 Gas 消耗统计
- `POST /api/fetch` - 手动触发数据获取

## 数据来源

使用 Basescan API (Etherscan API for Base) 获取链上数据：
- Base 链 ID: 8453
- API 文档：https://docs.basescan.org/

## 许可证

MIT