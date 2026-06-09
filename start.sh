#!/bin/bash
# Base Gas Dashboard 启动脚本

cd "$(dirname "$0")"

echo "🚀 启动 Base Gas Dashboard..."
echo "📊 数据模式: 配置 BASESCAN_API_KEY 使用真实数据，否则使用模拟数据"
echo ""

# 启动服务
HOST=0.0.0.0 PORT=8002 python3 main.py