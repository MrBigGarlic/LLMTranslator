"""
知识库学习器 - 自动学习并更新知识库
"""
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from .loader import KnowledgeBaseLoader
from .scene_detector import SceneDetector


class KnowledgeBaseLearner:
    """知识库学习器 - 从翻译过程中学习新表达"""
    
    def __init__(self, knowledge_base_path: str = None, auto_save: bool = True):
        """
        初始化知识库学习器
        
        Args:
            knowledge_base_path: 知识库目录路径
            auto_save: 是否自动保存（True=自动保存，False=需要手动确认）
        """
        if knowledge_base_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.knowledge_base_path = current_dir
        else:
            self.knowledge_base_path = knowledge_base_path
        
        self.loader = KnowledgeBaseLoader(knowledge_base_path)
        self.scene_detector = SceneDetector()
        self.auto_save = auto_save
        self.pending_updates: Dict[str, List[Dict[str, Any]]] = {}  # 待保存的更新
    
    def detect_new_expression(self, original_text: str, translated_text: str,
                             source_lang: str = "中文", target_lang: str = "英语") -> Optional[Dict[str, Any]]:
        """
        检测文本中可能的新表达
        
        Args:
            original_text: 原文
            translated_text: 译文
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            如果检测到新表达，返回表达信息，否则返回None
        """
        # 检测场景
        scenes = self.scene_detector.detect_scenes(original_text)
        if not scenes:
            return None
        
        primary_scene = scenes[0]["scene"]
        
        # 检查知识库中是否已有匹配
        knowledge_base = self.loader.get_knowledge_base(primary_scene)
        if not knowledge_base:
            return None
        
        existing_expressions = [expr.get("source", "") for expr in knowledge_base.get("expressions", [])]
        existing_keywords = knowledge_base.get("keywords", [])
        
        # 简单的启发式规则：查找可能的特殊表达
        # 1. 短文本（2-6字符）可能是特殊表达
        # 2. 包含特定字符模式
        # 3. 翻译与字面意思明显不同
        
        potential_expressions = self._extract_potential_expressions(
            original_text, translated_text, existing_expressions
        )
        
        if not potential_expressions:
            return None
        
        # 选择最可能的新表达
        best_candidate = potential_expressions[0]
        
        return {
            "source": best_candidate["text"],
            "scene": primary_scene,
            "translated_text": translated_text,
            "original_text": original_text,
            "confidence": best_candidate["confidence"],
            "detected_at": datetime.now().isoformat()
        }
    
    def _extract_potential_expressions(self, original_text: str, translated_text: str,
                                     existing_expressions: List[str]) -> List[Dict[str, Any]]:
        """
        提取可能的特殊表达
        
        Returns:
            候选表达列表，按置信度排序
        """
        candidates = []
        
        # 规则1：查找2-6字符的短语（可能是习语）
        import re
        # 简单的中文短语提取（2-6个中文字符）
        chinese_phrases = re.findall(r'[\u4e00-\u9fff]{2,6}', original_text)
        
        for phrase in chinese_phrases:
            # 跳过已知表达
            if phrase in existing_expressions:
                continue
            
            # 检查是否可能是特殊表达（不是常见词汇）
            # 简单启发式：如果包含"儿"、"子"等后缀，可能是口语表达
            confidence = 0.3  # 基础置信度
            
            if any(char in phrase for char in ['儿', '子', '打', '坐', '走']):
                confidence += 0.3
            
            # 如果短语较短（2-4字符），置信度更高
            if len(phrase) <= 4:
                confidence += 0.2
            
            candidates.append({
                "text": phrase,
                "confidence": min(confidence, 1.0),
                "position": original_text.find(phrase)
            })
        
        # 按置信度排序
        candidates.sort(key=lambda x: x["confidence"], reverse=True)
        
        return candidates
    
    def learn_from_translation(self, original_text: str, translated_text: str,
                             source_lang: str = "中文", target_lang: str = "英语",
                             ai_analysis: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        从翻译结果中学习
        
        Args:
            original_text: 原文
            translated_text: 译文
            source_lang: 源语言
            target_lang: 目标语言
            ai_analysis: AI的分析说明（可选）
            
        Returns:
            如果学习到新表达，返回新表达信息
        """
        new_expression = self.detect_new_expression(original_text, translated_text, source_lang, target_lang)
        
        if not new_expression:
            return None
        
        # 使用AI分析来丰富表达信息
        if ai_analysis:
            new_expression["ai_analysis"] = ai_analysis
        
        # 提取翻译建议
        new_expression["translation_en"] = translated_text
        new_expression["meaning"] = self._extract_meaning_from_analysis(ai_analysis) if ai_analysis else None
        
        # 保存到待更新列表
        scene = new_expression["scene"]
        if scene not in self.pending_updates:
            self.pending_updates[scene] = []
        
        self.pending_updates[scene].append(new_expression)
        
        # 如果启用自动保存，立即保存
        if self.auto_save:
            self.save_updates()
        
        return new_expression
    
    def _extract_meaning_from_analysis(self, analysis: str) -> Optional[str]:
        """从AI分析中提取含义"""
        # 简单的关键词提取
        if "含义" in analysis or "意思" in analysis:
            # 尝试提取含义部分
            import re
            patterns = [
                r'含义[：:]\s*([^。]+)',
                r'意思[：:]\s*([^。]+)',
                r'指的是\s*([^。]+)',
            ]
            for pattern in patterns:
                match = re.search(pattern, analysis)
                if match:
                    return match.group(1).strip()
        return None
    
    def add_expression_manually(self, scene: str, expression: Dict[str, Any]) -> bool:
        """
        手动添加表达到知识库
        
        Args:
            scene: 场景名称
            expression: 表达信息字典
            
        Returns:
            是否添加成功
        """
        if scene not in self.pending_updates:
            self.pending_updates[scene] = []
        
        self.pending_updates[scene].append(expression)
        
        if self.auto_save:
            return self.save_updates()
        
        return True
    
    def save_updates(self) -> bool:
        """
        保存所有待更新的表达到知识库文件
        
        Returns:
            是否保存成功
        """
        if not self.pending_updates:
            return True
        
        try:
            for scene, expressions in self.pending_updates.items():
                scene_file = Path(self.knowledge_base_path) / f"{scene}.json"
                
                # 读取现有知识库
                if scene_file.exists():
                    with open(scene_file, 'r', encoding='utf-8') as f:
                        knowledge_base = json.load(f)
                else:
                    # 创建新的知识库
                    knowledge_base = {
                        "scene": scene,
                        "description": self.scene_detector.get_scene_name(scene),
                        "keywords": [],
                        "expressions": [],
                        "translation_guidelines": []
                    }
                
                # 添加新表达
                existing_sources = {expr.get("source", "") for expr in knowledge_base.get("expressions", [])}
                
                for new_expr in expressions:
                    source = new_expr.get("source", "")
                    
                    # 避免重复
                    if source in existing_sources:
                        continue
                    
                    # 转换为标准格式
                    expression_entry = {
                        "source": source,
                        "variants": new_expr.get("variants", []),
                        "meaning": new_expr.get("meaning", "待完善"),
                        "translation_en": new_expr.get("translation_en", new_expr.get("translated_text", "")),
                        "translation_hint": new_expr.get("translation_hint", "AI自动学习"),
                        "context": new_expr.get("context", "待分类"),
                        "example_source": new_expr.get("original_text", ""),
                        "example_target": new_expr.get("translated_text", ""),
                        "cultural_note": new_expr.get("cultural_note", new_expr.get("ai_analysis", "自动学习")),
                        "learned_at": new_expr.get("detected_at", datetime.now().isoformat()),
                        "auto_learned": True
                    }
                    
                    knowledge_base["expressions"].append(expression_entry)
                    
                    # 添加到关键词列表（如果不存在）
                    if source not in knowledge_base["keywords"]:
                        knowledge_base["keywords"].append(source)
                    
                    existing_sources.add(source)
                
                # 保存到文件
                with open(scene_file, 'w', encoding='utf-8') as f:
                    json.dump(knowledge_base, f, ensure_ascii=False, indent=2)
                
                print(f"✓ 已更新知识库: {scene} ({len(expressions)} 条新表达)")
            
            # 清空待更新列表
            self.pending_updates.clear()
            
            # 重新加载知识库
            self.loader.reload()
            
            return True
            
        except Exception as e:
            print(f"保存知识库更新失败: {str(e)}")
            return False
    
    def get_pending_updates(self) -> Dict[str, List[Dict[str, Any]]]:
        """获取待保存的更新"""
        return self.pending_updates.copy()
    
    def clear_pending_updates(self):
        """清空待保存的更新"""
        self.pending_updates.clear()
