#!/usr/bin/env python3
"""
增强版DeepSeek翻译分析工具
支持智能prompt优化和特殊表达处理
"""
import os
import sys
from typing import List

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'core', 'analyzers'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'core', 'utils'))

from enhanced_deepseek_client import EnhancedDeepSeekClient
from deepseek_semantic_analyzer import DeepSeekSemanticAnalyzer
from simple_input_handler import SimpleInputHandler
from config import LANGUAGE_MAPPING, DEEPSEEK_API_KEY


class EnhancedDeepSeekTranslator:
    """增强版DeepSeek翻译器 - 支持智能prompt优化"""
    
    def __init__(self, api_key: str = None, use_enhanced_prompts: bool = True):
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.translator = EnhancedDeepSeekClient(self.api_key)
        self.analyzer = DeepSeekSemanticAnalyzer(self.api_key)
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
    
    def _process_chunks_with_enhanced_prompts(self, chunks: List[str], source_lang: str, target_lang: str, operation: str) -> List[dict]:
        """使用增强prompt处理文本段落"""
        result_chunks = []
        
        for i, chunk in enumerate(chunks):
            print(f"正在{operation}第{i+1}/{len(chunks)}段...")
            
            # 使用增强版翻译
            result = self.translator.translate_text_with_analysis(
                chunk, source_lang, target_lang, use_enhanced_prompts=self.use_enhanced_prompts
            )
            if result.get("translation"):
                result_chunks.append(result)
                print(f"第{i+1}段{operation}完成 (使用增强prompt)")
            else:
                print(f"第{i+1}段{operation}失败: {result.get('error', '未知错误')}")
                return []
        
        return result_chunks
    
    def translate_chunks(self, chunks: List[str], source_lang: str, target_lang: str) -> List[dict]:
        """翻译文本段落"""
        return self._process_chunks_with_enhanced_prompts(chunks, source_lang, target_lang, "翻译")
    
    def back_translate_chunks(self, translated_chunks: List[dict], source_lang: str, target_lang: str) -> List[dict]:
        """回译文本段落"""
        # 提取翻译文本进行回译
        texts = [chunk["translation"] for chunk in translated_chunks]
        return self._process_chunks_with_enhanced_prompts(texts, target_lang, source_lang, "回译")
    
    def run_enhanced_translation_analysis(self, text: str, source_lang: str, target_lang: str) -> dict:
        """运行增强版翻译分析流程"""
        
        print("=" * 60)
        print("增强版DeepSeek翻译和语义一致性分析")
        print("=" * 60)
        print(f"文本长度: {len(text)} 字符")
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
                translated_chunks = self.translate_chunks(chunks, source_lang, target_lang)
                if not translated_chunks:
                    return {"error": "翻译失败"}
                
                # 分段回译
                print(f"\n开始分段回译...")
                back_translated_chunks = self.back_translate_chunks(translated_chunks, source_lang, target_lang)
                if not back_translated_chunks:
                    return {"error": "回译失败"}
                
                # 合并结果
                target_translation = "".join([chunk["translation"] for chunk in translated_chunks])
                back_translation = "".join([chunk["translation"] for chunk in back_translated_chunks])
                
                # 合并增强信息
                combined_enhancement_info = self._combine_enhancement_info(translated_chunks)
            else:
                # 直接翻译
                print(f"\n开始翻译...")
                translation_result = self.translator.translate_text_with_analysis(
                    text, source_lang, target_lang, use_enhanced_prompts=self.use_enhanced_prompts
                )
                
                if not translation_result.get("translation"):
                    return {"error": f"翻译失败: {translation_result.get('error', '未知错误')}"}
                
                target_translation = translation_result["translation"]
                enhancement_info = translation_result.get("enhancement_info", {})
                
                print(f"\n开始回译...")
                back_translation_result = self.translator.translate_text_with_analysis(
                    target_translation, target_lang, source_lang, use_enhanced_prompts=self.use_enhanced_prompts
                )
                
                if not back_translation_result.get("translation"):
                    return {"error": f"回译失败: {back_translation_result.get('error', '未知错误')}"}
                
                back_translation = back_translation_result["translation"]
            
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
                "enhancement_info": combined_enhancement_info if is_long_text else enhancement_info,
                "is_long_text": is_long_text,
                "text_length": len(text),
                "enhanced_prompts_used": self.use_enhanced_prompts
            }
            
            if is_long_text:
                result["chunks_count"] = len(chunks)
            
            return result
            
        except Exception as e:
            error_msg = f"分析过程中发生错误: {str(e)}"
            return {"error": error_msg}
    
    def _combine_enhancement_info(self, chunks: List[dict]) -> dict:
        """合并多个chunk的增强信息"""
        combined = {
            "semantic_analysis": None,
            "rhythm_analysis": None,
            "optimization_applied": False,
            "special_expressions_found": [],
            "cultural_context_found": False
        }
        
        for chunk in chunks:
            enhancement_info = chunk.get("enhancement_info", {})
            
            # 合并特殊表达
            if enhancement_info.get("special_expressions_found"):
                combined["special_expressions_found"].extend(enhancement_info["special_expressions_found"])
            
            # 检查文化上下文
            if enhancement_info.get("cultural_context_found"):
                combined["cultural_context_found"] = True
            
            # 检查是否使用了优化
            if enhancement_info.get("optimization_applied"):
                combined["optimization_applied"] = True
        
        # 去重特殊表达
        combined["special_expressions_found"] = list(set(combined["special_expressions_found"]))
        
        return combined
    
    def print_enhanced_results(self, result: dict):
        """打印增强版分析结果"""
        if "error" in result:
            print(f"\n错误: {result['error']}")
            print(f"建议: 请检查网络连接、API密钥或稍后重试")
            return
        
        print("\n" + "=" * 60)
        print("增强版DeepSeek翻译分析结果")
        print("=" * 60)
        
        print(f"\n文本统计:")
        print(f"   原始长度: {result.get('text_length', 0)} 字符")
        print(f"   是否长文本: {'是' if result.get('is_long_text', False) else '否'}")
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
        
        print(f"\n小语种翻译 ({result['target_language']}):")
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
    
    def test_connection(self) -> bool:
        """测试连接"""
        return self.translator.test_connection()


def get_user_input():
    """获取用户输入"""
    print("增强版DeepSeek翻译分析工具")
    print("=" * 60)
    print("支持智能prompt优化的翻译质量分析")
    
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
    print("启动增强版DeepSeek翻译分析工具")
    print("支持智能prompt优化的翻译质量分析")
    
    # 检查API密钥
    api_key = DEEPSEEK_API_KEY or os.getenv('DEEPSEEK_API_KEY')
    
    if not api_key:
        print("警告: 未找到DeepSeek API密钥")
        print("请在config.py中设置DEEPSEEK_API_KEY或设置环境变量")
        print("请设置您的DeepSeek API密钥:")
        api_key = input("API密钥: ").strip()
        
        if not api_key:
            print("未提供API密钥，程序退出")
            return
    
    try:
        while True:
            # 获取用户输入
            text, source_lang, target_lang, use_enhanced_prompts = get_user_input()
            
            if not text:
                print("未获取到文本，请重试")
                continue
            
            # 创建翻译器
            translator = EnhancedDeepSeekTranslator(api_key, use_enhanced_prompts=use_enhanced_prompts)
            
            # 测试连接
            print(f"\n正在测试DeepSeek连接...")
            if not translator.test_connection():
                print(f"DeepSeek连接失败，请检查网络连接和配置")
                continue
            print(f"DeepSeek连接成功")
            
            # 运行分析
            result = translator.run_enhanced_translation_analysis(text, source_lang, target_lang)
            
            # 显示结果
            translator.print_enhanced_results(result)
            
            # 保存结果到文件
            if "error" not in result:
                translator.input_handler.save_results(
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
