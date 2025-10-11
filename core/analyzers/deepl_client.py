"""
DeepL API客户端
支持高质量翻译服务
"""
import requests
import time
from typing import Optional, Dict, Any
from config import DEEPL_API_KEY

class DeepLClient:
    """DeepL API客户端类"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or DEEPL_API_KEY
        # 根据API密钥判断使用免费版还是付费版端点
        if self.api_key and self.api_key.endswith(':fx'):
            self.base_url = "https://api-free.deepl.com/v2"
        else:
            self.base_url = "https://api.deepl.com/v2"
        self.max_retries = 3
        self.retry_delay = 1
        self.timeout = 30
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        翻译文本
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言代码
            target_lang: 目标语言代码
            
        Returns:
            翻译后的文本，失败时返回None
        """
        for attempt in range(self.max_retries):
            try:
                # 转换语言代码为DeepL格式
                deepl_source = self._convert_language_code(source_lang, is_source=True)
                deepl_target = self._convert_language_code(target_lang, is_source=False)
                
                if not deepl_target:
                    print(f"DeepL不支持目标语言: {target_lang}")
                    return None
                
                params = {
                    "auth_key": self.api_key,
                    "text": text,
                    "target_lang": deepl_target
                }
                
                # 如果源语言不是自动检测，则添加source_lang参数
                if deepl_source:
                    params["source_lang"] = deepl_source
                
                response = requests.post(
                    f"{self.base_url}/translate",
                    data=params,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "translations" in result and len(result["translations"]) > 0:
                        return result["translations"][0]["text"]
                    else:
                        print("DeepL返回格式异常")
                        return None
                elif response.status_code == 429:
                    # 请求频率限制
                    wait_time = self.retry_delay * (2 ** attempt)
                    print(f"DeepL请求频率限制，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                elif response.status_code == 403:
                    print("DeepL API密钥无效或权限不足")
                    return None
                elif response.status_code == 456:
                    print("DeepL API配额已用完")
                    return None
                else:
                    print(f"DeepL翻译请求失败: {response.status_code} - {response.text}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    return None
                    
            except requests.exceptions.Timeout:
                print(f"DeepL请求超时 (尝试 {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                return None
            except requests.exceptions.ConnectionError:
                print(f"DeepL网络连接错误 (尝试 {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                return None
            except Exception as e:
                print(f"DeepL翻译过程中发生错误: {str(e)}")
                return None
        
        print("DeepL所有重试尝试都失败了")
        return None
    
    def _convert_language_code(self, lang: str, is_source: bool = False) -> Optional[str]:
        """
        转换语言代码为DeepL格式
        
        Args:
            lang: 语言名称或代码
            is_source: 是否为源语言
            
        Returns:
            DeepL格式的语言代码
        """
        # DeepL支持的语言映射
        deepl_language_map = {
            'Chinese': 'ZH',
            'English': 'EN',
            'Vietnamese': 'VI',
            'Thai': 'TH',
            'Indonesian': 'ID',
            'Malay': 'MS',
            'Filipino': 'TL',
            'Burmese': None,  # DeepL不支持
            'Lao': None,      # DeepL不支持
            'Khmer': None,    # DeepL不支持
            # 反向映射
            '中文': 'ZH',
            '英语': 'EN',
            '越南语': 'VI',
            '泰语': 'TH',
            '印尼语': 'ID',
            '马来语': 'MS',
            '菲律宾语': 'TL',
            '缅甸语': None,
            '老挝语': None,
            '柬埔寨语': None
        }
        
        # 如果是源语言且为自动检测，返回None
        if is_source and lang in ['auto', 'AUTO']:
            return None
        
        return deepl_language_map.get(lang)
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            连接是否成功
        """
        for attempt in range(self.max_retries):
            try:
                params = {
                    "auth_key": self.api_key,
                    "text": "Hello",
                    "target_lang": "ZH"
                }
                
                response = requests.post(
                    f"{self.base_url}/translate",
                    data=params,
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
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """
        获取DeepL支持的语言列表
        
        Returns:
            支持的语言信息
        """
        try:
            # 获取目标语言
            target_response = requests.get(
                f"{self.base_url}/languages",
                params={"auth_key": self.api_key, "type": "target"},
                timeout=10
            )
            
            # 获取源语言
            source_response = requests.get(
                f"{self.base_url}/languages",
                params={"auth_key": self.api_key, "type": "source"},
                timeout=10
            )
            
            result = {
                "target_languages": [],
                "source_languages": [],
                "supported": True
            }
            
            if target_response.status_code == 200:
                result["target_languages"] = target_response.json()
            
            if source_response.status_code == 200:
                result["source_languages"] = source_response.json()
            
            return result
            
        except Exception as e:
            return {
                "target_languages": [],
                "source_languages": [],
                "supported": False,
                "error": str(e)
            }
