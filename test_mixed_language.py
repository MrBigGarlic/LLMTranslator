#!/usr/bin/env python3
"""
混合语言处理测试脚本
测试混合语言识别和翻译功能
"""
import sys
import os

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'core', 'analyzers'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'core', 'utils'))

from mixed_language_processor import MixedLanguageProcessor
from enhanced_deepseek_client import EnhancedDeepSeekClient
from multi_engine_translator import MultiEngineTranslator


def test_mixed_language_processor():
    """测试混合语言处理器"""
    print("=" * 60)
    print("测试混合语言处理器")
    print("=" * 60)
    
    processor = MixedLanguageProcessor()
    
    # 测试用例
    test_cases = [
        "我喜欢看NBA比赛，特别是湖人队的表现",
        "这个API接口的CPU使用率很高",
        "我们需要使用JavaScript和Python来开发这个项目",
        "苹果公司的iPhone和iPad都很受欢迎",
        "这个soga的设计很AppleU",
        "请使用HTTP协议访问这个URL",
        "我们的AI系统使用了ML和NLP技术",
        "这个项目的ROI和KPI都很不错"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {text}")
        print("-" * 40)
        
        # 分析混合语言
        analysis = processor.preprocess_for_translation(text, "中文", "英语")
        
        print(f"是否混合语言: {analysis['is_mixed_language']}")
        print(f"包含英语词汇: {analysis['english_words']}")
        print(f"包含中文词汇: {analysis['chinese_words']}")
        
        if analysis['translation_hints']:
            print("翻译提示:")
            for hint in analysis['translation_hints']:
                print(f"  - {hint}")
        
        # 生成翻译提示
        prompt = processor.generate_mixed_language_prompt(text, "中文", "英语")
        print(f"\n生成的翻译提示长度: {len(prompt)} 字符")


def test_enhanced_deepseek_with_mixed_language():
    """测试增强DeepSeek客户端的混合语言处理"""
    print("\n" + "=" * 60)
    print("测试增强DeepSeek客户端混合语言处理")
    print("=" * 60)
    
    client = EnhancedDeepSeekClient()
    
    # 测试用例
    test_cases = [
        "我喜欢看NBA比赛",
        "这个API接口的CPU使用率很高",
        "苹果公司的iPhone很受欢迎"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {text}")
        print("-" * 40)
        
        # 生成增强提示
        prompt = client._generate_enhanced_prompt(text, "中文", "英语")
        print(f"生成的提示包含混合语言处理: {'混合语言' in prompt}")
        print(f"提示长度: {len(prompt)} 字符")


def test_multi_engine_with_mixed_language():
    """测试多引擎翻译器的混合语言处理"""
    print("\n" + "=" * 60)
    print("测试多引擎翻译器混合语言处理")
    print("=" * 60)
    
    translator = MultiEngineTranslator()
    
    # 测试用例
    test_cases = [
        "我喜欢看NBA比赛",
        "这个API接口的CPU使用率很高",
        "苹果公司的iPhone很受欢迎"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {text}")
        print("-" * 40)
        
        # 分析文本特征
        features = translator._analyze_text_features(text)
        print(f"混合语言特征: {features['mixed_language']}")
        print(f"英语词汇: {features['english_words']}")
        print(f"中文词汇: {features['chinese_words']}")


def main():
    """主函数"""
    print("混合语言处理功能测试")
    print("测试混合语言识别、翻译提示生成和智能选择策略")
    
    try:
        # 测试混合语言处理器
        test_mixed_language_processor()
        
        # 测试增强DeepSeek客户端
        test_enhanced_deepseek_with_mixed_language()
        
        # 测试多引擎翻译器
        test_multi_engine_with_mixed_language()
        
        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
