"""
知识检索器 - 根据场景和文本检索相关知识
"""
import re
from typing import Dict, List, Any, Optional
from difflib import SequenceMatcher
from .loader import KnowledgeBaseLoader
from .scene_detector import SceneDetector

# 可选的外部API支持
try:
    from .external_apis import ExternalKnowledgeEnhancer
    EXTERNAL_APIS_AVAILABLE = True
except ImportError:
    EXTERNAL_APIS_AVAILABLE = False
    ExternalKnowledgeEnhancer = None


class KnowledgeRetriever:
    """知识检索器 - 根据场景和文本内容检索相关知识"""
    
    def __init__(self, knowledge_base_path: str = None, use_external_apis: bool = False):
        """
        初始化知识检索器
        
        Args:
            knowledge_base_path: 知识库目录路径
            use_external_apis: 是否使用外部API增强（默认False，因为ConceptNet响应较慢）
        """
        self.loader = KnowledgeBaseLoader(knowledge_base_path)
        self.scene_detector = SceneDetector()
        self.use_external_apis = use_external_apis and EXTERNAL_APIS_AVAILABLE
        self.external_enhancer = None
        if self.use_external_apis:
            try:
                # 从config读取有道API密钥（如果可用）
                try:
                    from config import YOUDAO_APP_KEY, YOUDAO_APP_SECRET
                    youdao_key = YOUDAO_APP_KEY
                    youdao_secret = YOUDAO_APP_SECRET
                except ImportError:
                    youdao_key = None
                    youdao_secret = None
                
                # 启用ConceptNet（免费）和有道词典（如果有密钥）
                self.external_enhancer = ExternalKnowledgeEnhancer(
                    enable_conceptnet=True,
                    youdao_key=youdao_key,
                    youdao_secret=youdao_secret
                )
            except Exception as e:
                print(f"外部API初始化失败: {str(e)}")
                self.use_external_apis = False
    
    def retrieve(self, text: str, scenes: List[str] = None, top_k: int = 5, 
                 min_confidence: float = 0.15) -> List[Dict[str, Any]]:
        """
        根据文本和场景检索相关知识
        
        Args:
            text: 输入文本
            scenes: 场景列表（如果为None，则自动识别场景）
            top_k: 返回最相关的K条知识
            min_confidence: 最小相关性阈值
            
        Returns:
            相关知识条目列表，包含表达、翻译建议等信息
        """
        # 如果没有提供场景，则自动识别
        if scenes is None:
            detected_scenes = self.scene_detector.detect_scenes(text)
            scenes = [s["scene"] for s in detected_scenes if s["confidence"] >= min_confidence]
        
        if not scenes:
            return []
        
        # 从所有相关场景中检索知识
        all_expressions = []
        
        for scene in scenes:
            knowledge_base = self.loader.get_knowledge_base(scene)
            if not knowledge_base:
                continue
            
            expressions = knowledge_base.get("expressions", [])
            keywords = knowledge_base.get("keywords", [])
            
            # 对每个表达计算相关性
            for expr in expressions:
                relevance_score = self._calculate_relevance(text, expr, keywords, scene)
                
                if relevance_score >= min_confidence:
                    all_expressions.append({
                        "expression": expr,
                        "scene": scene,
                        "scene_name": self.scene_detector.get_scene_name(scene),
                        "relevance_score": relevance_score,
                        "source": expr.get("source", ""),
                        "variants": expr.get("variants", [])
                    })
        
        # 按相关性降序排列，返回Top-K
        all_expressions.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        results = all_expressions[:top_k]
        
        # 如果启用外部API且本地知识库匹配较少，尝试外部增强
        if self.use_external_apis and len(results) < top_k:
            # 提取文本中的关键词，尝试从外部API获取补充信息
            # 注意：这里只是示例，实际使用时可能需要更智能的提取策略
            pass
        
        return results
    
    def _calculate_relevance(self, text: str, expression: Dict[str, Any], 
                            keywords: List[str], scene: str) -> float:
        """
        计算表达与文本的相关性分数
        
        Args:
            text: 输入文本
            expression: 知识库中的表达条目
            keywords: 场景关键词列表
            scene: 场景名称
            
        Returns:
            相关性分数（0.0-1.0）
        """
        source = expression.get("source", "")
        variants = expression.get("variants", [])
        
        score = 0.0
        
        # 1. 检查源词是否在文本中（权重最高）
        if source in text:
            # 完整匹配权重更高
            if re.search(r'\b' + re.escape(source) + r'\b', text):
                score += 0.6
            else:
                score += 0.4
        
        # 2. 检查变体是否在文本中
        for variant in variants:
            if variant in text:
                if re.search(r'\b' + re.escape(variant) + r'\b', text):
                    score += 0.5
                else:
                    score += 0.3
        
        # 3. 计算文本相似度（使用简单的序列匹配）
        if source:
            similarity = SequenceMatcher(None, source, text[:len(source)*2]).ratio()
            score += similarity * 0.2
        
        # 4. 检查是否包含场景关键词（轻微提升）
        context_keywords = [kw for kw in keywords if kw in text]
        if context_keywords:
            score += min(len(context_keywords) * 0.05, 0.2)
        
        return min(score, 1.0)
    
    def get_translation_guidelines(self, scenes: List[str]) -> List[str]:
        """
        获取指定场景的翻译指导原则
        
        Args:
            scenes: 场景列表
            
        Returns:
            翻译指导原则列表
        """
        all_guidelines = []
        
        for scene in scenes:
            knowledge_base = self.loader.get_knowledge_base(scene)
            if knowledge_base:
                guidelines = knowledge_base.get("translation_guidelines", [])
                all_guidelines.extend(guidelines)
        
        # 去重
        return list(dict.fromkeys(all_guidelines))
