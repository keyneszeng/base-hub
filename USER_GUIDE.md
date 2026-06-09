# Base 生态 Gas 消耗看板

## 关于 API Key 的说明

✅ **当前看板使用模拟数据** — 已包含 44 个 Base 生态项目 × 90 天历史

你已配置的 `BASESCAN_API_KEY`（5E9YT...TMN1）是 Basescan API Key，由于以下原因无法直接获取实时数据：

1. **Basescan API V1 已于 2025年8月15日完全关闭**
2. **Etherscan API V2 支持 Base 链，但需要付费计划**
3. Basescan API Key ≠ Etherscan API Key（需重新注册）

### 如需获取真实链上数据

1. 升级到 **Etherscan 付费计划**: https://etherscan.io/apis
2. 将 `.env` 中的 Key 替换为你的 **Etherscan API Key**
3. 重启服务即可

## 快速启动

```bash
cd ~/base-gas-dashboard
pip install -r requirements.txt
python3 main.py
```

访问 http://localhost:8002