"""
多引擎翻译器
结合DeepL和DeepSeek的优势，提供最佳翻译体验
"""
import time
import sys
import os
from typing import Dict, List, Optional, Tuple, Any

# 添加路径
sys.path.append(os.path.dirname(__file__))

from enhanced_deepseek_client import EnhancedDeepSeekClient
from deepl_client import DeepLClient
from deepseek_semantic_analyzer import DeepSeekSemanticAnalyzer
from mixed_language_processor import MixedLanguageProcessor

class MultiEngineTranslator:
    """多引擎翻译器 - 结合DeepL和DeepSeek"""
    
    def __init__(self, deepseek_api_key: str = None, deepl_api_key: str = None, use_enhanced_prompts: bool = True):
        self.deepseek_client = EnhancedDeepSeekClient(deepseek_api_key)
        self.deepl_client = DeepLClient(deepl_api_key)
        self.analyzer = DeepSeekSemanticAnalyzer(deepseek_api_key)
        self.mixed_language_processor = MixedLanguageProcessor()
        self.use_enhanced_prompts = use_enhanced_prompts
        
        # 长文本处理配置
        self.max_chunk_size = 1000
        self.overlap_size = 100
    
    def translate_with_dual_engines(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """
        使用双引擎进行翻译
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            翻译结果字典
        """
        result = {
            "original_text": text,
            "source_language": source_lang,
            "target_language": target_lang,
            "deepl_translation": None,
            "deepseek_translation": None,
            "best_translation": None,
            "translation_method": None,
            "confidence": 0.0,
            "error": None
        }
        
        try:
            # 并行调用两个翻译引擎
            print("正在使用DeepL和DeepSeek进行翻译...")
            
            # DeepL翻译
            deepl_start_time = time.time()
            deepl_translation = self.deepl_client.translate_text(text, source_lang, target_lang)
            deepl_time = time.time() - deepl_start_time
            
            # DeepSeek翻译
            deepseek_start_time = time.time()
            deepseek_result = self.deepseek_client.translate_text_with_analysis(
                text, source_lang, target_lang, use_enhanced_prompts=self.use_enhanced_prompts
            )
            deepseek_translation = deepseek_result.get("translation") if deepseek_result else None
            deepseek_time = time.time() - deepseek_start_time
            
            result["deepl_translation"] = deepl_translation
            result["deepseek_translation"] = deepseek_translation
            result["deepl_time"] = deepl_time
            result["deepseek_time"] = deepseek_time
            
            # 选择最佳翻译
            best_translation, method, confidence = self._select_best_translation(
                text, deepl_translation, deepseek_translation, source_lang, target_lang
            )
            
            result["best_translation"] = best_translation
            result["translation_method"] = method
            result["confidence"] = confidence
            
            return result
            
        except Exception as e:
            result["error"] = str(e)
            return result
    
    def _select_best_translation(self, original_text: str, deepl_translation: str, 
                                deepseek_translation: str, source_lang: str, target_lang: str) -> Tuple[str, str, float]:
        """
        智能选择最佳翻译结果 - 增强版算法
        
        Args:
            original_text: 原始文本
            deepl_translation: DeepL翻译结果
            deepseek_translation: DeepSeek翻译结果
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            (最佳翻译, 方法, 置信度)
        """
        # 如果只有一个翻译成功，直接返回
        if deepl_translation and not deepseek_translation:
            return deepl_translation, "deepl_only", 0.8
        elif deepseek_translation and not deepl_translation:
            return deepseek_translation, "deepseek_only", 0.8
        elif not deepl_translation and not deepseek_translation:
            return "", "failed", 0.0
        
        # 两个翻译都成功，进行智能分析
        try:
            # 第一步：文本特征分析
            text_features = self._analyze_text_features(original_text)
            
            # 第二步：多维度质量评估
            quality_scores = self._comprehensive_quality_assessment(
                original_text, deepl_translation, deepseek_translation, source_lang, target_lang, text_features
            )
            
            # 第三步：智能选择策略
            return self._intelligent_selection(
                deepl_translation, deepseek_translation, quality_scores, text_features
            )
            
        except Exception as e:
            print(f"智能翻译分析失败: {str(e)}")
            # 降级策略：基于文本特征选择
            return self._fallback_selection(original_text, deepl_translation, deepseek_translation)
    
    def _analyze_text_features(self, text: str) -> Dict[str, Any]:
        """分析文本特征，包括混合语言检测"""
        features = {
            "length": len(text),
            "complexity": "simple",
            "cultural_elements": False,
            "technical_terms": False,
            "idioms": False,
            "formality": "neutral",
            "mixed_language": False,
            "english_words": [],
            "chinese_words": []
        }
        
        # 混合语言分析
        mixed_analysis = self.mixed_language_processor.preprocess_for_translation(text, "中文", "英语")
        features["mixed_language"] = mixed_analysis["is_mixed_language"]
        features["english_words"] = mixed_analysis["english_words"]
        features["chinese_words"] = mixed_analysis["chinese_words"]
        
        # 长度分析
        if len(text) > 200:
            features["complexity"] = "complex"
        elif len(text) > 50:
            features["complexity"] = "medium"
        
        # 文化元素检测
        cultural_indicators = ['仨尖儿', '坐11路', '打酱油', '吃瓜', '躺平', '内卷', '凡尔赛', 'yyds', '绝绝子', '破防']
        if any(indicator in text for indicator in cultural_indicators):
            features["cultural_elements"] = True
            features["idioms"] = True
        
        # 技术术语检测（包括英语技术术语）
        technical_indicators = ['API', 'HTTP', 'JSON', 'XML', '数据库', '算法', '编程', '代码', 'CPU', 'GPU', 'AI', 'ML', 'NLP']
        if any(indicator in text for indicator in technical_indicators):
            features["technical_terms"] = True
        
        # 正式性检测
        formal_indicators = ['请', '您', '敬', '谨', '此致', '敬礼']
        if any(indicator in text for indicator in formal_indicators):
            features["formality"] = "formal"
        
        return features
    
    def _comprehensive_quality_assessment(self, original_text: str, deepl_translation: str, 
                                        deepseek_translation: str, source_lang: str, 
                                        target_lang: str, text_features: Dict[str, Any]) -> Dict[str, Any]:
        """多维度质量评估"""
        try:
            # 使用DeepSeek进行详细质量分析
            analysis_prompt = f"""请对以下两个翻译进行详细的质量评估：

原文 ({source_lang}): {original_text}

DeepL翻译: {deepl_translation}
DeepSeek翻译: {deepseek_translation}

文本特征: {text_features}

请从以下维度分别评分（0.0-1.0）：
1. 准确性 - 是否准确传达原文含义
2. 流畅性 - 是否自然流畅
3. 文化适应性 - 是否符合目标语言文化
4. 完整性 - 是否完整传达所有信息

请按以下格式回答：
DeepL评分:
- 准确性: [分数]
- 流畅性: [分数]
- 文化适应性: [分数]
- 完整性: [分数]

DeepSeek评分:
- 准确性: [分数]
- 流畅性: [分数]
- 文化适应性: [分数]
- 完整性: [分数]

推荐引擎: [DeepL/DeepSeek/混合]
推荐理由: [详细说明]"""

            analysis_result = self.deepseek_client._call_deepseek_api(analysis_prompt)
            
            if analysis_result:
                return self._parse_quality_scores(analysis_result)
            
        except Exception as e:
            print(f"质量评估失败: {str(e)}")
        
        # 使用基于特征的默认评分
        return self._default_quality_scoring(text_features)
    
    def _parse_quality_scores(self, analysis_result: str) -> Dict[str, Any]:
        """解析质量评分结果"""
        scores = {
            "deepl": {"accuracy": 0.5, "fluency": 0.5, "cultural_adaptation": 0.5, "completeness": 0.5, "overall": 0.5},
            "deepseek": {"accuracy": 0.5, "fluency": 0.5, "cultural_adaptation": 0.5, "completeness": 0.5, "overall": 0.5}
        }
        
        try:
            lines = analysis_result.split('\n')
            current_engine = None
            
            for line in lines:
                line = line.strip()
                if 'DeepL评分:' in line:
                    current_engine = 'deepl'
                elif 'DeepSeek评分:' in line:
                    current_engine = 'deepseek'
                elif current_engine and ':' in line:
                    if '准确性:' in line:
                        score = float(line.split(':')[1].strip())
                        scores[current_engine]['accuracy'] = score
                    elif '流畅性:' in line:
                        score = float(line.split(':')[1].strip())
                        scores[current_engine]['fluency'] = score
                    elif '文化适应性:' in line:
                        score = float(line.split(':')[1].strip())
                        scores[current_engine]['cultural_adaptation'] = score
                    elif '完整性:' in line:
                        score = float(line.split(':')[1].strip())
                        scores[current_engine]['completeness'] = score
            
            # 计算总体评分
            for engine in ['deepl', 'deepseek']:
                scores[engine]['overall'] = (
                    scores[engine]['accuracy'] * 0.3 +
                    scores[engine]['fluency'] * 0.25 +
                    scores[engine]['cultural_adaptation'] * 0.25 +
                    scores[engine]['completeness'] * 0.2
                )
                
        except Exception as e:
            print(f"评分解析失败: {str(e)}")
        
        return scores
    
    def _default_quality_scoring(self, text_features: Dict[str, Any]) -> Dict[str, Any]:
        """基于文本特征的默认评分"""
        scores = {
            "deepl": {"accuracy": 0.7, "fluency": 0.8, "cultural_adaptation": 0.6, "completeness": 0.7, "overall": 0.7},
            "deepseek": {"accuracy": 0.7, "fluency": 0.7, "cultural_adaptation": 0.8, "completeness": 0.7, "overall": 0.7}
        }
        
        # 根据文本特征调整评分
        if text_features.get("technical_terms"):
            scores["deepl"]["accuracy"] += 0.1
            scores["deepl"]["overall"] += 0.1
        elif text_features.get("cultural_elements"):
            scores["deepseek"]["cultural_adaptation"] += 0.1
            scores["deepseek"]["overall"] += 0.1
        
        if text_features.get("formality") == "formal":
            scores["deepl"]["fluency"] += 0.1
            scores["deepl"]["overall"] += 0.1
        
        return scores
    
    def _intelligent_selection(self, deepl_translation: str, deepseek_translation: str, 
                             quality_scores: Dict[str, Any], text_features: Dict[str, Any]) -> Tuple[str, str, float]:
        """智能选择策略，支持混合语言处理"""
        deepl_score = quality_scores["deepl"]["overall"]
        deepseek_score = quality_scores["deepseek"]["overall"]
        
        # 如果分数差距很大，选择高分引擎
        if abs(deepl_score - deepseek_score) > 0.2:
            if deepl_score > deepseek_score:
                return deepl_translation, "deepl_selected", deepl_score
            else:
                return deepseek_translation, "deepseek_selected", deepseek_score
        
        # 分数接近时，使用特征导向策略
        if text_features.get("mixed_language"):
            # 混合语言文本优先使用DeepSeek（更好的上下文理解）
            return deepseek_translation, "deepseek_mixed_language", 0.9
        elif text_features.get("cultural_elements") or text_features.get("idioms"):
            # 文化内容优先使用DeepSeek
            return deepseek_translation, "deepseek_cultural", 0.9
        elif text_features.get("technical_terms"):
            # 技术内容优先使用DeepL
            return deepl_translation, "deepl_technical", 0.9
        elif text_features.get("formality") == "formal":
            # 正式文本优先使用DeepL
            return deepl_translation, "deepl_formal", 0.9
        else:
            # 默认选择总体评分更高的
            if deepl_score >= deepseek_score:
                return deepl_translation, "deepl_default", deepl_score
            else:
                return deepseek_translation, "deepseek_default", deepseek_score
    
    def _fallback_selection(self, original_text: str, deepl_translation: str, deepseek_translation: str) -> Tuple[str, str, float]:
        """降级选择策略"""
        # 基于文本长度和特征选择
        if len(original_text) < 50:
            # 短文本优先使用DeepL
            return deepl_translation, "deepl_short_text", 0.7
        else:
            # 长文本优先使用DeepSeek
            return deepseek_translation, "deepseek_long_text", 0.7
    
    def translate_chunks_with_dual_engines(self, chunks: List[str], source_lang: str, target_lang: str) -> List[Dict[str, Any]]:
        """
        分段翻译文本
        
        Args:
            chunks: 文本段落列表
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            翻译结果列表
        """
        results = []
        
        for i, chunk in enumerate(chunks):
            print(f"正在翻译第{i+1}/{len(chunks)}段...")
            result = self.translate_with_dual_engines(chunk, source_lang, target_lang)
            results.append(result)
            
            if result.get("error"):
                print(f"第{i+1}段翻译失败: {result['error']}")
            else:
                print(f"第{i+1}段翻译完成 - 方法: {result['translation_method']}")
        
        return results
    
    def back_translate_with_dual_engines(self, translated_chunks: List[Dict[str, Any]], 
                                       source_lang: str, target_lang: str) -> List[Dict[str, Any]]:
        """
        回译文本段落
        
        Args:
            translated_chunks: 已翻译的文本段落
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            回译结果列表
        """
        back_translated_chunks = []
        
        for i, chunk_result in enumerate(translated_chunks):
            best_translation = chunk_result.get("best_translation")
            if not best_translation:
                continue
            
            print(f"正在回译第{i+1}/{len(translated_chunks)}段...")
            
            # 智能回译策略：使用不同的引擎进行回译以获得不同视角
            method = chunk_result.get("translation_method", "")
            
            if "deepl" in method:
                # 如果原翻译主要来自DeepL，回译时使用DeepSeek以获得不同视角
                back_result = self.deepseek_client.translate_text_with_analysis(
                    best_translation, target_lang, source_lang, use_enhanced_prompts=self.use_enhanced_prompts
                )
                back_translation = back_result.get("translation") if back_result else None
            else:
                # 如果原翻译主要来自DeepSeek，回译时使用DeepL
                back_translation = self.deepl_client.translate_text(best_translation, target_lang, source_lang)
            
            back_translated_chunks.append({
                "original_translation": best_translation,
                "back_translation": back_translation,
                "method": method
            })
            
            if back_translation:
                print(f"第{i+1}段回译完成")
            else:
                print(f"第{i+1}段回译失败")
        
        return back_translated_chunks
    
    def test_connections(self) -> Dict[str, bool]:
        """
        测试两个翻译引擎的连接
        
        Returns:
            连接测试结果
        """
        print("正在测试翻译引擎连接...")
        
        deepl_connected = self.deepl_client.test_connection()
        deepseek_connected = self.deepseek_client.test_connection()
        
        return {
            "deepl": deepl_connected,
            "deepseek": deepseek_connected,
            "both_connected": deepl_connected and deepseek_connected
        }
    
    def get_engine_status(self) -> Dict[str, Any]:
        """
        获取引擎状态信息
        
        Returns:
            引擎状态信息
        """
        return {
            "deepl": {
                "available": True,
                "supported_languages": self.deepl_client.get_supported_languages(),
                "mcp_tools": False
            },
            "deepseek": {
                "available": True,
                "supported_languages": "All languages in LANGUAGE_MAPPING",
                "enhanced_prompts": self.use_enhanced_prompts
            }
        }
