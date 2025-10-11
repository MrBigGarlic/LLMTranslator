"""
增强版DeepSeek API客户端
提供优化的翻译功能和智能prompt生成
"""
import requests
import time
from typing import Optional, Dict, Any
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

class EnhancedDeepSeekClient:
    """增强版DeepSeek API客户端"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.base_url = DEEPSEEK_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.max_retries = 3
        self.retry_delay = 1
        self.timeout = 60
    
    def translate_text_with_analysis(self, text: str, source_lang: str, target_lang: str, 
                                   use_enhanced_prompts: bool = True) -> Dict[str, Any]:
        """
        使用增强prompt的翻译方法
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言
            target_lang: 目标语言
            use_enhanced_prompts: 是否使用增强prompt
            
        Returns:
            翻译结果和分析信息
        """
        result = {
            "original_text": text,
            "source_language": source_lang,
            "target_language": target_lang,
            "translation": None,
            "enhancement_applied": False,
            "enhancement_info": {
                "special_expressions_found": [],
                "cultural_context_found": False,
                "optimization_applied": False
            },
            "error": None
        }
        
        try:
            # 生成优化的翻译prompt
            if use_enhanced_prompts:
                optimized_prompt = self._generate_enhanced_prompt(text, source_lang, target_lang)
                result["enhancement_applied"] = True
                result["enhancement_info"]["optimization_applied"] = True
                
                # 检测特殊表达
                special_expressions = self._detect_special_expressions(text)
                if special_expressions:
                    result["enhancement_info"]["special_expressions_found"] = special_expressions
                    result["enhancement_info"]["cultural_context_found"] = True
            else:
                optimized_prompt = self._generate_basic_prompt(text, source_lang, target_lang)
            
            # 执行翻译
            translation = self._call_deepseek_api(optimized_prompt)
            result["translation"] = translation
            
            return result
            
        except Exception as e:
            result["error"] = str(e)
            return result
    
    def _generate_enhanced_prompt(self, text: str, source_lang: str, target_lang: str) -> str:
        """生成增强的翻译prompt"""
        # 检测特殊表达
        special_expressions = self._detect_special_expressions(text)
        
        base_prompt = f"请将以下{source_lang}文本翻译成{target_lang}，"
        
        if special_expressions:
            base_prompt += "注意以下特殊要求：\n\n"
            base_prompt += "特殊表达处理：\n"
            for expr in special_expressions:
                if expr in self._get_special_expressions_db():
                    suggestion = self._get_special_expressions_db()[expr]
                    base_prompt += f"- '{expr}': {suggestion}\n"
            base_prompt += "\n"
        
        base_prompt += f"翻译要求：\n"
        base_prompt += f"1. 保持原文的语调和情感\n"
        base_prompt += f"2. 确保翻译自然流畅\n"
        base_prompt += f"3. 如有文化差异，请提供适当的解释\n"
        base_prompt += f"4. 只返回翻译结果，不要添加解释\n\n"
        base_prompt += f"原文：{text}"
        
        return base_prompt
    
    def _detect_special_expressions(self, text: str) -> list:
        """检测特殊表达"""
        special_expressions = []
        expressions_db = self._get_special_expressions_db()
        
        for expr in expressions_db.keys():
            if expr in text:
                special_expressions.append(expr)
        
        return special_expressions
    
    def _get_special_expressions_db(self) -> dict:
        """获取特殊表达数据库"""
        return {
            '仨尖儿': 'three aces (best cards in poker)',
            '坐11路': 'walk (take the "number 11 bus" - meaning walk on two legs)',
            '打酱油': 'just passing by / not getting involved',
            '吃瓜': 'watch the drama / be a spectator',
            '躺平': 'lie flat / give up striving',
            '内卷': 'involution / excessive competition',
            '凡尔赛': 'Versailles (referring to showing off in a subtle way)',
            'yyds': 'eternal god (slang for "amazing")',
            '绝绝子': 'absolutely amazing (slang)',
            '破防': 'break through defense (slang for being moved/touched)',
            'emo': 'emotional (feeling sad/depressed)',
            '社死': 'social death (extreme embarrassment)'
        }
    
    def _generate_basic_prompt(self, text: str, source_lang: str, target_lang: str) -> str:
        """生成基础翻译prompt"""
        return f"""请将以下{source_lang}文本翻译成{target_lang}，只返回翻译结果，不要添加任何解释：

{text}"""
    
    def _call_deepseek_api(self, prompt: str) -> Optional[str]:
        """调用DeepSeek API"""
        for attempt in range(self.max_retries):
            try:
                payload = {
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000
                }
                
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content'].strip()
                elif response.status_code == 429:
                    wait_time = self.retry_delay * (2 ** attempt)
                    print(f"请求频率限制，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                elif response.status_code == 401:
                    print("API密钥无效")
                    return None
                elif response.status_code == 403:
                    print("API访问被拒绝，请检查权限")
                    return None
                else:
                    print(f"翻译请求失败: {response.status_code} - {response.text}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    return None
                    
            except requests.exceptions.Timeout:
                print(f"请求超时 (尝试 {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                return None
            except requests.exceptions.ConnectionError:
                print(f"网络连接错误 (尝试 {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                return None
            except Exception as e:
                print(f"翻译过程中发生错误: {str(e)}")
                return None
        
        return None
    
    def test_connection(self) -> bool:
        """测试API连接"""
        for attempt in range(self.max_retries):
            try:
                payload = {
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "user",
                            "content": "Hello"
                        }
                    ],
                    "max_tokens": 10
                }
                
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    return True
                else:
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return False
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return False
        
        return False