"""
基于DeepSeek API的语义分析器
"""
import re
from typing import Dict
from config import SIMILARITY_THRESHOLD
from enhanced_deepseek_client import EnhancedDeepSeekClient as DeepSeekClient


class DeepSeekSemanticAnalyzer:
    """基于DeepSeek API的语义一致性分析器"""
    
    def __init__(self, api_key: str = None):
        self.client = DeepSeekClient(api_key)
    
    def analyze_semantic_consistency_with_deepseek(self, original_text: str, back_translated_text: str, source_lang: str = "中文") -> Dict:
        """
        使用DeepSeek API分析语义一致性
        
        Args:
            original_text: 原始文本
            back_translated_text: 回译文本
            source_lang: 源语言
            
        Returns:
            分析结果字典
        """
        try:
            # 首先检查是否完全相同
            if original_text == back_translated_text:
                return {
                    'similarity_score': 1.0,
                    'is_consistent': True,
                    'threshold': 0.5,
                    'consistency_level': '完全一致',
                    'deepseek_analysis': '文本完全相同',
                    'semantic_meaning': 'identical',
                    'confidence': 1.0,
                    'is_identical': True
                }
            
            # 使用DeepSeek分析语义相似度
            deepseek_result = self._get_deepseek_semantic_analysis(original_text, back_translated_text, source_lang)
            
            # 解析DeepSeek分析结果
            similarity_score = deepseek_result.get('similarity_score', 0.0)
            semantic_meaning = deepseek_result.get('semantic_meaning', 'unknown')
            confidence = deepseek_result.get('confidence', 0.0)
            
            # 动态阈值调整
            threshold = self._get_dynamic_threshold(original_text, back_translated_text, semantic_meaning)
            
            # 判断是否一致
            is_consistent = similarity_score >= threshold
            
            # 分析结果
            result = {
                'similarity_score': similarity_score,
                'is_consistent': is_consistent,
                'threshold': threshold,
                'consistency_level': self._get_consistency_level(similarity_score),
                'deepseek_analysis': deepseek_result.get('analysis', ''),
                'semantic_meaning': semantic_meaning,
                'confidence': confidence,
                'original_length': len(original_text),
                'back_translated_length': len(back_translated_text),
                'is_identical': original_text == back_translated_text
            }
            
            return result
            
        except Exception as e:
            print(f"DeepSeek语义分析过程中发生错误: {str(e)}")
            # 降级到基础分析
            return self._fallback_analysis(original_text, back_translated_text)
    
    def _get_deepseek_semantic_analysis(self, text1: str, text2: str, source_lang: str) -> Dict:
        """
        使用DeepSeek API分析两个文本的语义相似度
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
            source_lang: 源语言
            
        Returns:
            DeepSeek分析结果
        """
        try:
            # 构建DeepSeek分析提示
            prompt = f"""请分析以下两个{source_lang}文本的语义相似度：

文本1: "{text1}"
文本2: "{text2}"

请从语义角度分析这两个文本是否表达相同的含义，忽略：
- 量词差异（如"一只"vs"一条"）
- 标点符号差异
- 语序轻微变化
- 同义词替换
- 表达方式差异

请按以下格式回答：
相似度分数: [0.0-1.0之间的数字]
语义含义: [identical/similar/different]
分析说明: [详细说明为什么给出这个分数]
置信度: [0.0-1.0之间的数字]

示例：
相似度分数: 0.95
语义含义: identical
分析说明: 两个文本表达完全相同的含义，只是量词从"一只"变为"一条"，在中文中都是正确的表达方式
置信度: 0.9"""

            # 调用DeepSeek API进行分析
            response = self.client._call_deepseek_api(prompt)
            
            if not response:
                return self._fallback_analysis(text1, text2)
            
            # 解析DeepSeek响应
            return self._parse_deepseek_response(response)
            
        except Exception as e:
            print(f"DeepSeek分析调用失败: {str(e)}")
            return self._fallback_analysis(text1, text2)
    
    def _parse_deepseek_response(self, response: str) -> Dict:
        """
        解析DeepSeek响应
        
        Args:
            response: DeepSeek的响应文本
            
        Returns:
            解析后的结果字典
        """
        try:
            result = {
                'similarity_score': 0.0,
                'semantic_meaning': 'unknown',
                'analysis': response,
                'confidence': 0.0,
                'is_identical': False
            }
            
            # 提取相似度分数
            similarity_match = re.search(r'相似度分数:\s*([0-9.]+)', response)
            if similarity_match:
                result['similarity_score'] = float(similarity_match.group(1))
            
            # 提取语义含义
            meaning_match = re.search(r'语义含义:\s*(\w+)', response)
            if meaning_match:
                result['semantic_meaning'] = meaning_match.group(1)
            
            # 提取置信度
            confidence_match = re.search(r'置信度:\s*([0-9.]+)', response)
            if confidence_match:
                result['confidence'] = float(confidence_match.group(1))
            
            return result
            
        except Exception as e:
            print(f"解析DeepSeek响应失败: {str(e)}")
            return {
                'similarity_score': 0.0,
                'semantic_meaning': 'unknown',
                'analysis': response,
                'confidence': 0.0,
                'is_identical': False
            }
    
    def _get_dynamic_threshold(self, text1: str, text2: str, semantic_meaning: str) -> float:
        """
        根据语义含义动态调整阈值
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
            semantic_meaning: 语义含义类型
            
        Returns:
            调整后的阈值
        """
        # 如果DeepSeek判断为identical，使用更低的阈值
        if semantic_meaning == 'identical':
            return 0.5
        
        # 如果DeepSeek判断为similar，使用中等阈值
        if semantic_meaning == 'similar':
            return 0.6
        
        # 如果文本很短，使用较低阈值
        if len(text1) <= 3 or len(text2) <= 3:
            return 0.6
        
        # 默认阈值
        return SIMILARITY_THRESHOLD
    
    def _get_consistency_level(self, similarity_score: float) -> str:
        """
        根据相似度分数获取一致性等级
        
        Args:
            similarity_score: 相似度分数
            
        Returns:
            一致性等级描述
        """
        if similarity_score >= 0.95:
            return "几乎完全一致"
        elif similarity_score >= 0.9:
            return "高度一致"
        elif similarity_score >= 0.8:
            return "基本一致"
        elif similarity_score >= 0.7:
            return "部分一致"
        elif similarity_score >= 0.5:
            return "低度一致"
        else:
            return "不一致"
    
    def _fallback_analysis(self, text1: str, text2: str) -> Dict:
        """
        降级分析（当DeepSeek分析失败时使用）
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
            
        Returns:
            基础分析结果
        """
        # 简单的文本相似度计算
        if text1 == text2:
            similarity = 1.0
        else:
            # 基于字符重叠的简单相似度
            set1 = set(text1.lower())
            set2 = set(text2.lower())
            if not set1 and not set2:
                similarity = 1.0
            elif not set1 or not set2:
                similarity = 0.0
            else:
                intersection = len(set1.intersection(set2))
                union = len(set1.union(set2))
                similarity = intersection / union if union > 0 else 0.0
        
        return {
            'similarity_score': similarity,
            'is_consistent': similarity >= 0.7,
            'threshold': 0.7,
            'consistency_level': self._get_consistency_level(similarity),
            'deepseek_analysis': 'DeepSeek分析不可用，使用基础文本相似度',
            'semantic_meaning': 'unknown',
            'confidence': 0.3,
            'is_identical': text1 == text2
        }
    
    def get_detailed_analysis(self, original_text: str, back_translated_text: str, source_lang: str = "中文") -> Dict:
        """
        获取详细的DeepSeek分析报告
        
        Args:
            original_text: 原始文本
            back_translated_text: 回译文本
            source_lang: 源语言
            
        Returns:
            详细分析报告
        """
        basic_analysis = self.analyze_semantic_consistency_with_deepseek(original_text, back_translated_text, source_lang)
        
        # 添加更多分析维度
        detailed_analysis = basic_analysis.copy()
        
        # 添加智能建议
        if basic_analysis['is_identical']:
            detailed_analysis['suggestion'] = "文本完全相同，翻译质量优秀"
        elif basic_analysis['semantic_meaning'] == 'identical':
            detailed_analysis['suggestion'] = "DeepSeek分析：语义完全相同，翻译质量优秀"
        elif basic_analysis['semantic_meaning'] == 'similar':
            detailed_analysis['suggestion'] = "DeepSeek分析：语义相似，翻译质量良好"
        elif basic_analysis['is_consistent']:
            detailed_analysis['suggestion'] = "翻译质量良好，语义保持一致"
        else:
            detailed_analysis['suggestion'] = "DeepSeek分析：翻译可能存在语义偏差，建议检查翻译质量"
        
        return detailed_analysis
