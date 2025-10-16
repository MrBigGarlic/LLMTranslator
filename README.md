# DeepSeek翻译分析工具

一个基于DeepSeek API的智能翻译质量评估工具，支持多语言翻译、语义一致性检测和智能prompt优化。

## 🚀 快速开始

### 一键启动
```bash
./start.sh
```

启动脚本会自动：
- 检查Python环境
- 安装所需依赖（requests、python-dotenv）
- 提供运行模式选择

### 运行模式
- **1. 单引擎翻译** - DeepSeek + 智能prompt优化
- **2. 多引擎翻译** - DeepL + DeepSeek 对比翻译
- **3. 退出**

## ✨ 核心功能

### 单引擎翻译（DeepSeek + 智能prompt）
- **多语言支持**：中文、英语、越南语、马来语、泰语、印尼语、菲律宾语、缅甸语、老挝语、柬埔寨语
- **往返翻译**：原语言→小语种→原语言的完整翻译链路
- **AI语义分析**：使用DeepSeek大语言模型理解文本真实含义
- **智能评估**：多维度语义相似度分析算法
- **动态阈值**：根据文本特点自动调整判断标准
- **智能prompt优化**：自动识别特殊表达、文化上下文分析
- **特殊表达处理**：准确翻译"仨尖儿"、"坐11路"等文化特定表达
- **混合语言处理**：智能识别和处理中英文混合文本（如"NBA"、"CPU"、"iPhone"等）

### 多引擎翻译（DeepL + DeepSeek）
- **双引擎对比**：DeepL和DeepSeek同时翻译，智能选择最佳结果
- **性能对比**：显示两个引擎的响应时间和翻译质量
- **自动选择**：基于语义分析自动选择最佳翻译
- **混合语言优化**：针对混合语言文本优先使用DeepSeek引擎（更好的上下文理解）
- **质量评估**：综合评估翻译准确性和流畅度
- **回译验证**：通过回译确保翻译一致性

## 🛠️ 技术特点

### 智能prompt优化
- **特殊表达识别**：自动检测文化特定表达和习语
- **上下文分析**：理解字面意义与实际意义的差异
- **动态prompt生成**：根据文本特点生成最佳翻译指令
- **文化适配**：针对不同文化背景优化翻译策略

### 混合语言处理
- **自动识别**：智能识别中英文混合文本
- **词汇分离**：准确分离英语和中文词汇
- **翻译建议**：为英语词汇提供标准翻译建议
- **引擎优化**：针对混合语言文本优化翻译引擎选择
- **支持类型**：技术术语、品牌名、缩写、拟音词等

### 语义一致性分析
- **多维度评估**：从语义、语法、文化等多个角度分析
- **相似度计算**：精确的语义相似度评分算法
- **动态阈值**：根据文本复杂度自动调整判断标准
- **详细报告**：提供完整的分析结果和改进建议

### 长文本处理
- **智能分段**：自动将长文本分割为合适的段落
- **重叠处理**：确保分段边界的语义完整性
- **批量处理**：高效处理大量文本内容
- **结果合并**：智能合并分段翻译结果

## 📁 项目结构

```
LLMTranslator_02/
├── main.py                          # 单引擎翻译主程序
├── main_multi_engine.py             # 多引擎翻译主程序
├── start.sh                         # 启动脚本
├── config.py                        # 配置文件
├── requirements.txt                 # 依赖包列表
├── input.txt                        # 长文本输入文件
├── output.txt                       # 分析结果输出文件
├── core/
│   ├── analyzers/
│   │   ├── enhanced_deepseek_client.py    # 增强版DeepSeek客户端
│   │   ├── deepl_client.py               # DeepL客户端
│   │   ├── multi_engine_translator.py    # 多引擎翻译器
│   │   └── deepseek_semantic_analyzer.py # 语义分析器
│   └── utils/
│       └── simple_input_handler.py       # 输入处理器
└── README.md                        # 项目说明文档
```

## 🔧 安装和配置

### 环境要求
- Python 3.7+
- 网络连接（用于API调用）

### 依赖包
```bash
pip install -r requirements.txt
```

主要依赖：
- `requests>=2.25.0` - HTTP请求库
- `python-dotenv>=0.19.0` - 环境变量管理

### API配置
- **DeepSeek API**：已在 `config.py` 中配置
- **DeepL API**：需要在 `config.py` 中设置您的DeepL API密钥

## 🎯 使用示例

### 单引擎翻译
```bash
./start.sh
# 选择 1. 单引擎翻译
# 输入要翻译的文本
# 查看智能prompt优化的翻译结果
```

### 多引擎翻译
```bash
./start.sh
# 选择 2. 多引擎翻译
# 输入要翻译的文本
# 查看双引擎对比结果
```

### 长文本处理
1. 将长文本放入 `input.txt` 文件
2. 运行翻译工具
3. 选择"长文本输入"选项
4. 系统自动分段处理并合并结果

## 📊 输出示例

### 翻译结果
```
原始文本 (中文): 你好世界
最佳翻译 (英语): Hello world.
回译文本 (中文): 你好世界。

语义一致性分析:
相似度分数: 0.950
一致性等级: 几乎完全一致
是否一致: 是
动态阈值: 0.500
语义含义: identical
置信度: 0.900
```

### 多引擎对比
```
DeepL翻译: Hello world.
DeepSeek翻译: Hello world
最佳选择: Hello world. (DeepL)
选择原因: 标点符号更完整
响应时间: DeepL 0.88s, DeepSeek 1.84s
```

## 🔍 特殊表达处理

系统内置了常见的中文特殊表达数据库，包括：

- **仨尖儿** → three aces (best cards in poker)
- **坐11路** → walk (take the "number 11 bus")
- **打酱油** → just passing by / not getting involved
- **吃瓜** → watch the drama / be a spectator
- **躺平** → lie flat / give up striving
- **内卷** → involution / excessive competition
- **凡尔赛** → Versailles (showing off subtly)
- **yyds** → eternal god (slang for "amazing")
- **绝绝子** → absolutely amazing (slang)
- **破防** → break through defense (moved/touched)

## 🚨 注意事项

1. **API密钥安全**：请妥善保管您的API密钥，不要泄露给他人
2. **网络连接**：确保网络连接稳定，API调用需要网络访问
3. **文本长度**：超长文本会自动分段处理，可能需要较长时间
4. **语言支持**：不同API对语言的支持程度可能不同
5. **使用限制**：请注意API的使用限制和配额

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

本项目采用MIT许可证。

## 📞 支持

如果您在使用过程中遇到问题，请：
1. 检查网络连接和API密钥配置
2. 查看错误日志和输出信息
3. 提交Issue描述问题详情

---

**享受智能翻译的便利！** 🎉