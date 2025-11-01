"""
RAG增强的Prompt生成器 - 将检索到的知识整合到翻译prompt中
"""
from typing import List, Dict, Any
from .retriever import KnowledgeRetriever
from .scene_detector import SceneDetector


class RAGPromptEnhancer:
    """RAG增强的Prompt生成器"""
    
    def __init__(self, knowledge_base_path: str = None):
        """
        初始化RAG Prompt增强器
        
        Args:
            knowledge_base_path: 知识库目录路径
        """
        self.retriever = KnowledgeRetriever(knowledge_base_path)
        self.scene_detector = SceneDetector()
    
    def generate_enhanced_prompt(self, text: str, source_lang: str, target_lang: str,
                                  use_rag: bool = True, top_k: int = 5) -> str:
        """
        生成包含RAG知识的增强prompt
        
        Args:
            text: 输入文本
            source_lang: 源语言
            target_lang: 目标语言
            use_rag: 是否使用RAG增强
            top_k: 检索的知识条目数量
            
        Returns:
            增强后的prompt
        """
        base_prompt = f"请将以下{source_lang}文本翻译成{target_lang}。\n\n"
        
        if not use_rag:
            base_prompt += f"原文：{text}"
            return base_prompt
        
        # 场景识别
        detected_scenes = self.scene_detector.detect_scenes(text)
        
        # 知识检索
        retrieved_knowledge = self.retriever.retrieve(text, top_k=top_k)
        
        # 构建增强prompt
        if detected_scenes:
            base_prompt += "【场景识别】\n"
            scene_names = [f"{self.scene_detector.get_scene_name(s['scene'])} (置信度: {s['confidence']:.2f})" 
                          for s in detected_scenes[:3]]  # 只显示前3个场景
            base_prompt += f"检测到以下场景：{', '.join(scene_names)}\n\n"
        
        if retrieved_knowledge:
            base_prompt += "【相关知识库】\n"
            base_prompt += "以下是与文本相关的场景知识，请参考：\n\n"
            
            for i, item in enumerate(retrieved_knowledge, 1):
                expr = item["expression"]
                scene_name = item["scene_name"]
                relevance = item["relevance_score"]
                
                base_prompt += f"{i}. 场景：{scene_name}（相关性：{relevance:.2f}）\n"
                base_prompt += f"   特殊表达：\"{expr.get('source', '')}\"\n"
                
                if expr.get("variants"):
                    base_prompt += f"   变体：{', '.join(expr.get('variants', []))}\n"
                
                if expr.get("meaning"):
                    base_prompt += f"   实际含义：{expr.get('meaning')}\n"
                
                if expr.get(f"translation_{target_lang.lower()[:2]}") or expr.get("translation_en"):
                    # 优先使用目标语言的翻译，如果没有则使用英文
                    translation = expr.get(f"translation_{target_lang.lower()[:2]}") or expr.get("translation_en", "")
                    if translation:
                        base_prompt += f"   翻译建议：{translation}\n"
                
                if expr.get("translation_hint"):
                    base_prompt += f"   翻译提示：{expr.get('translation_hint')}\n"
                
                if expr.get("context"):
                    base_prompt += f"   上下文：{expr.get('context')}\n"
                
                if expr.get("example_source") and expr.get("example_target"):
                    base_prompt += f"   示例：\n"
                    base_prompt += f"     原文：{expr.get('example_source')}\n"
                    base_prompt += f"     译文：{expr.get('example_target')}\n"
                
                base_prompt += "\n"
        
        # 获取翻译指导原则
        if detected_scenes:
            scenes_list = [s["scene"] for s in detected_scenes]
            guidelines = self.retriever.get_translation_guidelines(scenes_list)
            if guidelines:
                base_prompt += "【翻译指导原则】\n"
                for guideline in guidelines[:5]:  # 最多显示5条
                    base_prompt += f"- {guideline}\n"
                base_prompt += "\n"
        
        # 添加翻译要求
        base_prompt += "【翻译要求】\n"
        base_prompt += "1. 仔细分析文本中的场景特定表达，参考上述知识库提供的翻译指导\n"
        base_prompt += "2. 对于文化特定表达，要理解其实际含义而非字面意思\n"
        base_prompt += "3. 确保翻译准确且符合目标语言习惯\n"
        base_prompt += "4. 保持原文的语调和情感\n"
        base_prompt += "5. 只返回翻译结果，不要添加解释\n\n"
        
        base_prompt += f"原文：{text}"
        
        return base_prompt
