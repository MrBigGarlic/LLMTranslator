#!/bin/bash

# 智能翻译工具 - 启动脚本
# 整合DeepSeek和DeepL双引擎翻译

echo "智能翻译工具"
echo "=============="
echo ""

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到python3，请先安装Python 3.7+"
    exit 1
fi

python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "错误: Python版本过低，需要3.7+，当前版本: $python_version"
    exit 1
fi

echo "Python版本检查通过: $python_version"

# 检查依赖包
echo "检查依赖..."
missing_packages=()

if ! python3 -c "import requests" 2>/dev/null; then
    missing_packages+=("requests")
fi

if ! python3 -c "import dotenv" 2>/dev/null; then
    missing_packages+=("python-dotenv")
fi

if [ ${#missing_packages[@]} -ne 0 ]; then
    echo "安装缺失的依赖包: ${missing_packages[*]}"
    pip3 install "${missing_packages[@]}"
    if [ $? -ne 0 ]; then
        echo "依赖包安装失败，请手动安装: pip3 install ${missing_packages[*]}"
        exit 1
    fi
fi

echo "所有依赖已就绪"
echo ""

# 启动智能翻译工具
echo "启动智能翻译工具..."
echo "整合DeepSeek和DeepL双引擎，智能选择最佳翻译结果"
echo ""

python3 main_multi_engine.py