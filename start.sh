#!/bin/bash

# 增强版DeepSeek翻译分析工具 - 快速启动脚本
# 支持智能prompt优化和特殊表达处理

echo "增强版DeepSeek翻译分析工具"
echo "================================"
echo "支持智能prompt优化的翻译质量分析"
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

# 显示功能说明
echo "功能特点："
echo "  ✓ 多语言支持（中文、英语、越南语、马来语、泰语等10种语言）"
echo "  ✓ 往返翻译（原语言→小语种→原语言的完整翻译链路）"
echo "  ✓ AI语义分析（使用DeepSeek大语言模型理解文本真实含义）"
echo "  ✓ 智能prompt优化（特殊表达处理、文化上下文分析）"
echo "  ✓ 长短文本支持（短文本终端输入和长文本文件输入）"
echo "  ✓ 详细报告（提供完整的分析结果和建议）"
echo ""

# 询问用户选择
echo "请选择运行模式："
echo "  1. 单引擎翻译 - DeepSeek + 智能prompt优化"
echo "  2. 多引擎翻译 - DeepL + DeepSeek 对比翻译"
echo "  3. 退出"
echo ""

while true; do
    read -p "请输入选择 (1-3): " choice
    case $choice in
        1)
            echo ""
            echo "启动单引擎翻译工具（DeepSeek + 智能prompt）..."
            echo ""
            echo "智能prompt优化功能："
            echo "  • 特殊表达识别 - 自动识别'仨尖儿'、'坐11路'等"
            echo "  • 文化上下文分析 - 理解文化特定表达的真实含义"
            echo "  • 智能prompt生成 - 动态生成最佳翻译指令"
            echo "  • 语义深度分析 - 区分字面意义与实际意义"
            echo ""
            python3 main.py
            break
            ;;
        2)
            echo ""
            echo "启动多引擎翻译工具（DeepL + DeepSeek）..."
            echo ""
            echo "多引擎对比功能："
            echo "  • 双引擎翻译对比 - DeepL和DeepSeek同时翻译"
            echo "  • 自动选择最佳引擎 - 智能选择最佳翻译结果"
            echo "  • 翻译质量评估 - 基于语义分析的质量评分"
            echo "  • 响应时间对比 - 显示两个引擎的性能差异"
            echo "  • 语义一致性分析 - 回译验证翻译准确性"
            echo ""
            python3 main_multi_engine.py
            break
            ;;
        3)
            echo "感谢使用！"
            exit 0
            ;;
        *)
            echo "无效选择，请输入 1、2 或 3"
            ;;
    esac
done