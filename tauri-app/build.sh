#!/bin/bash
set -e

echo "🔨 开始自动构建流程..."

cd "$(dirname "$0")"

# 1. 打包 Python 桥接层
echo "📦 打包 Python 桥接层..."
python3 -m PyInstaller --onefile --name jmcomic-bridge bridge.py --distpath dist --workpath build --specpath .

# 2. 构建 Tauri 应用
echo "🚀 构建 Tauri 应用..."
cd src-tauri
cargo tauri build

echo "✅ 构建完成！"
echo "📦 应用包位于: target/release/bundle/"
