#!/usr/bin/env python3
"""
多引擎翻译分析工具
结合DeepL和DeepSeek的优势，保留MCP工具增强功能
"""
import os
import sys
from typing import List

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'core', 'analyzers'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'core', 'utils'))

from multi_engine_translator import MultiEngineTranslator
from deepseek_semantic_analyzer import DeepSeekSemanticAnalyzer
from simple_input_handler import SimpleInputHandler
from config import LANGUAGE_MAPPING, DEEPSEEK_API_KEY, DEEPL_API_KEY


class MultiEngineTranslationAnalyzer:
    """多引擎翻译分析器"""
    
    def __init__(self, deepseek_api_key: str = None, deepl_api_key: str = None, use_enhanced_prompts: bool = True):
        self.translator = MultiEngineTranslator(deepseek_api_key, deepl_api_key, use_enhanced_prompts)
        self.analyzer = DeepSeekSemanticAnalyzer(deepseek_api_key)
        self.input_handler = SimpleInputHandler()
        self.use_enhanced_prompts = use_enhanced_prompts
        
        # 长文本处理配置
        self.max_chunk_size = 1000
        self.overlap_size = 100
    
    def split_text_into_chunks(self, text: str) -> List[str]:
        """将长文本分割成较小的段落"""
        if len(text) <= self.max_chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.max_chunk_size
            
            if end < len(text):
                # 寻找最近的句子结束符
                for i in range(end, max(start + self.max_chunk_size // 2, end - 200), -1):
                    if text[i] in '。！？.!?':
                        end = i + 1
                        break
                else:
                    # 在空格处分割
                    for i in range(end, max(start + self.max_chunk_size // 2, end - 100), -1):
                        if text[i] in ' \n\t':
                            end = i
                            break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = max(start + 1, end - self.overlap_size)
        
        return chunks
    
    def run_multi_engine_analysis(self, text: str, source_lang: str, target_lang: str) -> dict:
        """运行多引擎翻译分析流程"""
        
        print("=" * 60)
        print("多引擎翻译分析工具")
        print("=" * 60)
        print(f"文本长度: {len(text)} 字符")
        print(f"翻译引擎: DeepL + DeepSeek")
        print(f"智能prompt: {'启用' if self.use_enhanced_prompts else '禁用'}")
        
        # 验证输入
        if source_lang not in LANGUAGE_MAPPING:
            error_msg = f"不支持的源语言: {source_lang}"
            return {"error": error_msg}
        
        if target_lang not in LANGUAGE_MAPPING:
            error_msg = f"不支持的目标语言: {target_lang}"
            return {"error": error_msg}
        
        try:
            # 检查是否需要分段处理
            is_long_text = len(text) > self.max_chunk_size
            
            if is_long_text:
                print(f"\n检测到长文本，正在分割...")
                chunks = self.split_text_into_chunks(text)
                print(f"文本已分割为 {len(chunks)} 段")
                
                # 分段翻译
                print(f"\n开始分段翻译...")
                translated_chunks = self.translator.translate_chunks_with_dual_engines(chunks, source_lang, target_lang)
                if not translated_chunks:
                    return {"error": "翻译失败"}
                
                # 分段回译
                print(f"\n开始分段回译...")
                back_translated_chunks = self.translator.back_translate_with_dual_engines(translated_chunks, source_lang, target_lang)
                if not back_translated_chunks:
                    return {"error": "回译失败"}
                
                # 合并结果
                best_translations = [chunk["best_translation"] for chunk in translated_chunks if chunk.get("best_translation")]
                back_translations = [chunk["back_translation"] for chunk in back_translated_chunks if chunk.get("back_translation")]
                
                target_translation = "".join(best_translations)
                back_translation = "".join(back_translations)
                
                # 合并MCP分析结果
                combined_mcp_analysis = self._combine_mcp_analyses(translated_chunks)
            else:
                # 直接翻译
                print(f"\n开始双引擎翻译...")
                translation_result = self.translator.translate_with_dual_engines(text, source_lang, target_lang)
                
                if not translation_result.get("best_translation"):
                    return {"error": f"翻译失败: {translation_result.get('error', '未知错误')}"}
                
                target_translation = translation_result["best_translation"]
                combined_mcp_analysis = translation_result.get("mcp_analysis", {})
                
                print(f"\n开始回译...")
                back_translation_result = self.translator.translate_with_dual_engines(
                    target_translation, target_lang, source_lang
                )
                
                if not back_translation_result.get("best_translation"):
                    return {"error": f"回译失败: {back_translation_result.get('error', '未知错误')}"}
                
                back_translation = back_translation_result["best_translation"]
            
            # 进行语义一致性分析
            analysis_result = None
            try:
                print(f"\n正在进行DeepSeek AI语义一致性分析...")
                analysis_result = self.analyzer.get_detailed_analysis(text, back_translation, source_lang)
            except Exception as e:
                analysis_result = {
                    "similarity_score": 0.0,
                    "is_consistent": False,
                    "threshold": 0.7,
                    "consistency_level": "分析失败",
                    "deepseek_analysis": f"语义分析失败: {str(e)}",
                    "semantic_meaning": "unknown",
                    "confidence": 0.0,
                    "suggestion": "语义分析失败，请检查网络连接或API状态"
                }
            
            # 整理结果
            result = {
                "original_text": text,
                "source_language": source_lang,
                "target_language": target_lang,
                "target_translation": target_translation,
                "back_translation": back_translation,
                "semantic_analysis": analysis_result,
                "enhancement_info": combined_mcp_analysis,
                "is_long_text": is_long_text,
                "text_length": len(text),
                "enhanced_prompts_used": self.use_enhanced_prompts,
                "translation_engines": "DeepL + DeepSeek"
            }
            
            if is_long_text:
                result["chunks_count"] = len(chunks)
            
            return result
            
        except Exception as e:
            error_msg = f"分析过程中发生错误: {str(e)}"
            return {"error": error_msg}
    
    def _combine_mcp_analyses(self, chunks: List[dict]) -> dict:
        """合并多个chunk的MCP分析结果"""
        combined = {
            "semantic_analysis": None,
            "rhythm_analysis": None,
            "optimization_applied": False,
            "special_expressions_found": [],
            "cultural_context_found": False
        }
        
        for chunk in chunks:
            mcp_analysis = chunk.get("mcp_analysis", {})
            
            # 合并语义分析
            if mcp_analysis.get("semantic_analysis"):
                if not combined["semantic_analysis"]:
                    combined["semantic_analysis"] = mcp_analysis["semantic_analysis"]
                else:
                    # 合并特殊表达
                    special_exprs = mcp_analysis["semantic_analysis"].get("special_expressions", [])
                    combined["special_expressions_found"].extend(special_exprs)
                    
                    # 检查文化上下文
                    if mcp_analysis["semantic_analysis"].get("cultural_context"):
                        combined["cultural_context_found"] = True
            
            # 合并韵律分析
            if mcp_analysis.get("rhythm_analysis"):
                if not combined["rhythm_analysis"]:
                    combined["rhythm_analysis"] = mcp_analysis["rhythm_analysis"]
            
            # 检查是否使用了优化
            if chunk.get("optimization_applied"):
                combined["optimization_applied"] = True
        
        # 去重特殊表达
        combined["special_expressions_found"] = list(set(combined["special_expressions_found"]))
        
        return combined
    
    def print_multi_engine_results(self, result: dict):
        """打印多引擎分析结果"""
        if "error" in result:
            print(f"\n错误: {result['error']}")
            print(f"建议: 请检查网络连接、API密钥或稍后重试")
            return
        
        print("\n" + "=" * 60)
        print("多引擎翻译分析结果")
        print("=" * 60)
        
        print(f"\n文本统计:")
        print(f"   原始长度: {result.get('text_length', 0)} 字符")
        print(f"   是否长文本: {'是' if result.get('is_long_text', False) else '否'}")
        print(f"   翻译引擎: {result.get('translation_engines', 'Unknown')}")
        print(f"   智能prompt: {'启用' if result.get('enhanced_prompts_used', False) else '禁用'}")
        if result.get('is_long_text'):
            print(f"   分段数量: {result.get('chunks_count', 1)} 段")
        
        # 显示增强信息
        if result.get('enhancement_info'):
            self._print_enhancement_info(result['enhancement_info'])
        
        print(f"\n原始文本 ({result['source_language']}):")
        original_text = result['original_text']
        if len(original_text) > 200:
            print(f"   {original_text[:200]}...")
            print(f"   [显示前200字符，完整文本长度: {len(original_text)} 字符]")
        else:
            print(f"   {original_text}")
        
        print(f"\n最佳翻译 ({result['target_language']}):")
        target_text = result['target_translation']
        if len(target_text) > 200:
            print(f"   {target_text[:200]}...")
            print(f"   [显示前200字符，完整文本长度: {len(target_text)} 字符]")
        else:
            print(f"   {target_text}")
        
        print(f"\n回译文本 ({result['source_language']}):")
        back_text = result['back_translation']
        if len(back_text) > 200:
            print(f"   {back_text[:200]}...")
            print(f"   [显示前200字符，完整文本长度: {len(back_text)} 字符]")
        else:
            print(f"   {back_text}")
        
        # 语义分析结果
        if result.get('semantic_analysis'):
            analysis = result['semantic_analysis']
            print(f"\nDeepSeek语义一致性分析:")
            print(f"   相似度分数: {analysis['similarity_score']:.3f}")
            print(f"   一致性等级: {analysis['consistency_level']}")
            print(f"   是否一致: {'是' if analysis['is_consistent'] else '否'}")
            print(f"   动态阈值: {analysis['threshold']:.3f}")
            print(f"   语义含义: {analysis['semantic_meaning']}")
            print(f"   置信度: {analysis['confidence']:.3f}")
            
            print(f"\n分析说明:")
            print(f"   {analysis['deepseek_analysis']}")
            
            print(f"\n建议: {analysis['suggestion']}")
        
        print("\n" + "=" * 60)
    
    def _print_enhancement_info(self, enhancement_info: dict):
        """打印增强信息"""
        print(f"\n智能prompt增强信息:")
        
        # 特殊表达处理
        if enhancement_info.get('special_expressions_found'):
            print(f"   发现特殊表达: {', '.join(enhancement_info['special_expressions_found'])}")
        
        if enhancement_info.get('cultural_context_found'):
            print(f"   文化特定内容: 是")
        
        # 优化应用
        if enhancement_info.get('optimization_applied'):
            print(f"   翻译优化: 已应用")
    
    def test_connections(self) -> bool:
        """测试连接"""
        results = self.translator.test_connections()
        return results["both_connected"]


def get_user_input():
    """获取用户输入"""
    print("多引擎翻译分析工具")
    print("=" * 60)
    print("结合DeepL和DeepSeek的优势，提供最佳翻译体验")
    
    input_handler = SimpleInputHandler()
    
    # 显示支持的语言
    print("\n支持的语言:")
    for i, lang in enumerate(LANGUAGE_MAPPING.keys(), 1):
        print(f"  {i}. {lang}")
    
    # 获取源语言
    while True:
        try:
            source_choice = input(f"\n请选择源语言 (1-{len(LANGUAGE_MAPPING)}): ").strip()
            source_index = int(source_choice) - 1
            if 0 <= source_index < len(LANGUAGE_MAPPING):
                source_lang = list(LANGUAGE_MAPPING.keys())[source_index]
                break
            else:
                print("无效选择，请重新输入")
        except ValueError:
            print("请输入有效数字")
    
    # 获取目标语言
    while True:
        try:
            target_choice = input(f"请选择目标语言 (1-{len(LANGUAGE_MAPPING)}): ").strip()
            target_index = int(target_choice) - 1
            if 0 <= target_index < len(LANGUAGE_MAPPING):
                target_lang = list(LANGUAGE_MAPPING.keys())[target_index]
                if target_lang == source_lang:
                    print("目标语言不能与源语言相同")
                    continue
                break
            else:
                print("无效选择，请重新输入")
        except ValueError:
            print("请输入有效数字")
    
    # 智能prompt已默认启用
    use_enhanced_prompts = True
    print("\n智能prompt已启用，将提供特殊表达处理和文化上下文分析")
    
    # 获取文本
    text = input_handler.get_text_input(source_lang)
    
    return text, source_lang, target_lang, use_enhanced_prompts


def main():
    """主函数"""
    print("启动多引擎翻译分析工具")
    print("结合DeepL和DeepSeek的优势，提供最佳翻译体验")
    
    # 检查API密钥
    deepseek_api_key = DEEPSEEK_API_KEY or os.getenv('DEEPSEEK_API_KEY')
    deepl_api_key = DEEPL_API_KEY or os.getenv('DEEPL_API_KEY')
    
    if not deepseek_api_key:
        print("警告: 未找到DeepSeek API密钥")
        print("请在config.py中设置DEEPSEEK_API_KEY或设置环境变量")
        print("请设置您的DeepSeek API密钥:")
        deepseek_api_key = input("DeepSeek API密钥: ").strip()
        
        if not deepseek_api_key:
            print("未提供DeepSeek API密钥，程序退出")
            return
    
    if not deepl_api_key or deepl_api_key == "your_deepl_api_key_here":
        print("警告: 未找到DeepL API密钥")
        print("请在config.py中设置DEEPL_API_KEY或设置环境变量")
        print("请设置您的DeepL API密钥:")
        deepl_api_key = input("DeepL API密钥: ").strip()
        
        if not deepl_api_key:
            print("未提供DeepL API密钥，程序退出")
            return
    
    try:
        while True:
            # 获取用户输入
            text, source_lang, target_lang, use_enhanced_prompts = get_user_input()
            
            if not text:
                print("未获取到文本，请重试")
                continue
            
            # 创建翻译器
            analyzer = MultiEngineTranslationAnalyzer(deepseek_api_key, deepl_api_key, use_enhanced_prompts=use_enhanced_prompts)
            
            # 测试连接
            print(f"\n正在测试翻译引擎连接...")
            if not analyzer.test_connections():
                print(f"翻译引擎连接失败，请检查网络连接和配置")
                continue
            print(f"翻译引擎连接成功")
            
            # 运行分析
            result = analyzer.run_multi_engine_analysis(text, source_lang, target_lang)
            
            # 显示结果
            analyzer.print_multi_engine_results(result)
            
            # 保存结果到文件
            if "error" not in result:
                analyzer.input_handler.save_results(
                    result['original_text'],
                    result['target_translation'],
                    result['back_translation'],
                    result['source_language'],
                    result['target_language'],
                    result.get('semantic_analysis'),
                    result.get('is_long_text', False),
                    result.get('chunks_count', 1)
                )
            
            # 询问是否继续
            continue_choice = input("\n是否继续分析其他文本? (y/n): ").strip().lower()
            if continue_choice not in ['y', 'yes', '是']:
                break
                
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        error_msg = f"程序运行出错: {str(e)}"
        print(f"\n{error_msg}")


if __name__ == "__main__":
    main()
