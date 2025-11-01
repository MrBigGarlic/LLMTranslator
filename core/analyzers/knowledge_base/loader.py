"""
知识库加载器 - 加载和管理知识库文件
"""
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path


class KnowledgeBaseLoader:
    """知识库加载器"""
    
    def __init__(self, knowledge_base_path: str = None):
        """
        初始化知识库加载器
        
        Args:
            knowledge_base_path: 知识库目录路径，默认为当前模块所在目录
        """
        if knowledge_base_path is None:
            # 默认使用当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.knowledge_base_path = current_dir
        else:
            self.knowledge_base_path = knowledge_base_path
        
        self._knowledge_bases: Dict[str, Dict[str, Any]] = {}
        self._load_all_knowledge_bases()
    
    def _load_all_knowledge_bases(self):
        """加载所有知识库文件"""
        knowledge_base_dir = Path(self.knowledge_base_path)
        
        # 加载所有JSON文件（排除__init__.py等）
        for json_file in knowledge_base_dir.glob("*.json"):
            scene = json_file.stem  # 文件名（不含扩展名）作为场景名
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    knowledge_base = json.load(f)
                    self._knowledge_bases[scene] = knowledge_base
            except Exception as e:
                print(f"加载知识库文件 {json_file} 失败: {str(e)}")
    
    def get_knowledge_base(self, scene: str) -> Optional[Dict[str, Any]]:
        """
        获取指定场景的知识库
        
        Args:
            scene: 场景名称（如 "daily_life"）
            
        Returns:
            知识库字典，如果不存在则返回None
        """
        return self._knowledge_bases.get(scene)
    
    def get_all_scenes(self) -> List[str]:
        """获取所有可用的场景"""
        return list(self._knowledge_bases.keys())
    
    def reload(self):
        """重新加载所有知识库"""
        self._knowledge_bases.clear()
        self._load_all_knowledge_bases()
