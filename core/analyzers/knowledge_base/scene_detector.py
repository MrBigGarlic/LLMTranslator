"""
场景识别模块 - 识别文本可能涉及的场景
"""
import re
from typing import Dict, List


class SceneDetector:
    """场景识别器 - 基于关键词和文本特征识别场景"""
    
    def __init__(self):
        # 场景关键词库
        self.scene_keywords = {
            "daily_life": {
                "keywords": ["三尖儿", "仨尖儿", "坐11路", "打酱油", "走亲戚", "遛弯", "打牌", 
                           "买菜", "做饭", "逛街", "聊天", "唠嗑", "串门"],
                "weight": 1.0
            },
            "business": {
                "keywords": ["落地", "闭环", "赋能", "抓手", "痛点", "打法", "布局", "赛道",
                           "盈利", "商业模式", "战略", "执行", "KPI", "ROI"],
                "weight": 1.0
            },
            "technology": {
                "keywords": ["接口", "API", "前端", "后端", "数据库", "部署", "上线", "代码",
                           "算法", "架构", "系统", "服务器", "客户端", "编程"],
                "weight": 1.0
            },
            "sports": {
                "keywords": ["比赛", "运动员", "得分", "进球", "训练", "教练", "球队", "冠军"],
                "weight": 1.0
            },
            "medical": {
                "keywords": ["患者", "诊断", "治疗", "药物", "症状", "医生", "医院", "手术"],
                "weight": 1.0
            },
            "academic": {
                "keywords": ["研究", "论文", "实验", "数据", "分析", "结论", "方法", "理论"],
                "weight": 1.0
            }
        }
    
    def detect_scenes(self, text: str) -> List[Dict[str, float]]:
        """
        识别文本中的场景
        
        Args:
            text: 输入文本
            
        Returns:
            [{"scene": "daily_life", "confidence": 0.8}, ...] 按置信度降序排列
        """
        scene_scores = {}
        
        # 统计每个场景的关键词匹配数
        for scene, config in self.scene_keywords.items():
            score = 0.0
            keywords = config["keywords"]
            weight = config["weight"]
            
            # 计算关键词匹配数
            matches = 0
            for keyword in keywords:
                # 简单匹配：如果关键词在文本中出现
                if keyword in text:
                    matches += 1
                    # 基础分数
                    score += 1.0 * weight
            
            if matches > 0:
                # 计算匹配比例（更重要的指标）
                match_ratio = matches / len(keywords)
                # 计算匹配关键词的平均权重
                avg_match_weight = score / matches if matches > 0 else 0
                # 最终分数：主要基于匹配比例，少量考虑权重
                final_score = match_ratio * 0.8 + min(avg_match_weight / 10, 0.2)
                scene_scores[scene] = final_score
        
        # 如果没有匹配到场景，返回空列表
        if not scene_scores:
            return []
        
        # 按置信度降序排列
        sorted_scenes = sorted(
            [{"scene": scene, "confidence": score} 
             for scene, score in scene_scores.items()],
            key=lambda x: x["confidence"],
            reverse=True
        )
        
        # 只返回置信度大于0.15的场景（降低阈值以便匹配）
        return [s for s in sorted_scenes if s["confidence"] >= 0.15]
    
    def get_scene_name(self, scene_code: str) -> str:
        """获取场景的中文名称"""
        scene_names = {
            "daily_life": "日常生活",
            "business": "商务",
            "technology": "科技",
            "sports": "体育",
            "medical": "医疗",
            "academic": "学术"
        }
        return scene_names.get(scene_code, scene_code)
