"""
外部API集成 - 用于增强RAG知识库的外部资源
"""
import requests
import time
import json
from typing import Dict, List, Optional, Any
from functools import lru_cache


class ConceptNetAPI:
    """ConceptNet知识图谱API客户端（免费，无需API密钥）"""
    
    def __init__(self, timeout: int = 5):
        self.base_url = "http://api.conceptnet.io"
        self.timeout = timeout
    
    @lru_cache(maxsize=100)
    def query_concept(self, text: str, language: str = "zh") -> Optional[Dict[str, Any]]:
        """
        查询ConceptNet中的概念
        
        Args:
            text: 查询文本
            language: 语言代码（zh=中文, en=英文）
            
        Returns:
            概念信息字典，包含关系、定义等
        """
        try:
            # ConceptNet API格式
            url = f"{self.base_url}/c/{language}/{text}"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_conceptnet_response(data)
            return None
        except Exception as e:
            print(f"ConceptNet查询失败: {str(e)}")
            return None
    
    def _parse_conceptnet_response(self, data: Dict) -> Dict[str, Any]:
        """解析ConceptNet响应"""
        result = {
            "concept": data.get("id", ""),
            "edges": [],
            "definitions": [],
            "related_concepts": []
        }
        
        # 提取边（关系）
        edges = data.get("edges", [])
        for edge in edges[:10]:  # 只取前10个关系
            relation = edge.get("rel", {}).get("label", "")
            end = edge.get("end", {}).get("label", "")
            weight = edge.get("weight", 0)
            
            if weight > 1.0:  # 只保留权重较高的关系
                result["edges"].append({
                    "relation": relation,
                    "related_concept": end,
                    "weight": weight
                })
        
        # 提取定义
        # ConceptNet的定义通常在其他字段中，这里简化处理
        
        return result
    
    def get_related_concepts(self, text: str, language: str = "zh", 
                           limit: int = 5) -> List[str]:
        """
        获取相关概念列表
        
        Args:
            text: 查询文本
            language: 语言代码
            limit: 返回数量限制
            
        Returns:
            相关概念列表
        """
        concept_data = self.query_concept(text, language)
        if not concept_data:
            return []
        
        related = []
        for edge in concept_data.get("edges", [])[:limit]:
            related_concept = edge.get("related_concept", "")
            if related_concept:
                related.append(related_concept)
        
        return related


class YoudaoDictAPI:
    """有道词典API客户端（需要API密钥）"""
    
    def __init__(self, app_key: str = None, app_secret: str = None, timeout: int = 5):
        self.app_key = app_key
        self.app_secret = app_secret
        # 有道词典API端点（注意：您申请的是文本翻译服务，这里使用词典查询API）
        self.base_url = "https://openapi.youdao.com/api"
        self.timeout = timeout
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    def lookup_word(self, word: str, from_lang: str = "zh-CHS", 
                   to_lang: str = "en") -> Optional[Dict[str, Any]]:
        """
        查询单词
        
        Args:
            word: 查询单词
            from_lang: 源语言
            to_lang: 目标语言
            
        Returns:
            词典结果，包含释义、例句等
        """
        if not self.app_key or not self.app_secret:
            return None
        
        try:
            import hashlib
            import uuid
            import time
            
            # 生成签名（有道API要求：sha256(appKey + input + salt + curtime + appSecret)）
            salt = str(uuid.uuid1())
            curtime = str(int(time.time()))
            sign_str = self.app_key + word + salt + curtime + self.app_secret
            sign = hashlib.sha256(sign_str.encode()).hexdigest()
            
            params = {
                "q": word,
                "from": from_lang,
                "to": to_lang,
                "appKey": self.app_key,
                "salt": salt,
                "curtime": curtime,
                "sign": sign,
                "signType": "v3"
            }
            
            response = requests.post(
                self.base_url, 
                data=params, 
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"有道词典查询失败: {str(e)}")
            return None


class ExternalKnowledgeEnhancer:
    """外部知识增强器 - 整合多个外部API"""
    
    def __init__(self, enable_conceptnet: bool = True, 
                 youdao_key: str = None, youdao_secret: str = None):
        """
        初始化外部知识增强器
        
        Args:
            enable_conceptnet: 是否启用ConceptNet（免费）
            youdao_key: 有道词典API密钥（可选）
            youdao_secret: 有道词典API密钥（可选）
        """
        self.conceptnet = ConceptNetAPI() if enable_conceptnet else None
        self.youdao = YoudaoDictAPI(youdao_key, youdao_secret) if (youdao_key and youdao_secret) else None
    
    def enhance_knowledge(self, text: str, language: str = "zh") -> Dict[str, Any]:
        """
        使用外部资源增强知识
        
        Args:
            text: 查询文本
            language: 语言代码
            
        Returns:
            增强后的知识字典
        """
        enhanced = {
            "conceptnet_data": None,
            "youdao_data": None,
            "related_concepts": []
        }
        
        # 查询ConceptNet（免费）
        if self.conceptnet:
            try:
                concept_data = self.conceptnet.query_concept(text, language)
                enhanced["conceptnet_data"] = concept_data
                if concept_data:
                    enhanced["related_concepts"] = concept_data.get("related_concepts", [])
            except Exception as e:
                print(f"ConceptNet查询失败: {str(e)}")
        
        # 查询有道词典（需要API密钥）
        if self.youdao:
            try:
                dict_data = self.youdao.lookup_word(text)
                enhanced["youdao_data"] = dict_data
            except Exception as e:
                print(f"有道词典查询失败: {str(e)}")
        
        return enhanced
    
    def get_translation_hints(self, text: str, language: str = "zh") -> List[str]:
        """
        从外部资源获取翻译提示
        
        Args:
            text: 查询文本
            language: 语言代码
            
        Returns:
            翻译提示列表
        """
        hints = []
        
        # 从ConceptNet获取相关概念提示
        if self.conceptnet:
            related = self.conceptnet.get_related_concepts(text, language, limit=3)
            if related:
                hints.append(f"相关概念: {', '.join(related)}")
        
        # 从有道词典获取释义提示
        if self.youdao:
            dict_data = self.youdao.lookup_word(text)
            if dict_data and dict_data.get("basic"):
                translation = dict_data["basic"].get("explains", [])
                if translation:
                    hints.append(f"词典释义: {translation[0]}")
        
        return hints
