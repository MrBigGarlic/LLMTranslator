"""
增强版DeepSeek API客户端
提供优化的翻译功能、智能prompt生成和混合语言处理
"""
import requests
import time
import os
import sys
from typing import Optional, Dict, Any
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, ENABLE_RAG, KNOWLEDGE_BASE_PATH, RAG_TOP_K
from mixed_language_processor import MixedLanguageProcessor

# 添加knowledge_base路径
sys.path.append(os.path.dirname(__file__))
try:
    from knowledge_base.prompt_enhancer import RAGPromptEnhancer
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    RAGPromptEnhancer = None

class EnhancedDeepSeekClient:
    """增强版DeepSeek API客户端"""
    
    def __init__(self, api_key: str = None, use_rag: bool = None):
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.base_url = DEEPSEEK_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.max_retries = 3
        self.retry_delay = 1
        self.timeout = 60
        self.mixed_language_processor = MixedLanguageProcessor()
        
        # RAG配置
        self.use_rag = use_rag if use_rag is not None else (ENABLE_RAG and RAG_AVAILABLE)
        self.rag_enhancer = None
        if self.use_rag and RAG_AVAILABLE:
            try:
                knowledge_base_path = KNOWLEDGE_BASE_PATH or os.path.join(os.path.dirname(__file__), 'knowledge_base')
                self.rag_enhancer = RAGPromptEnhancer(knowledge_base_path)
            except Exception as e:
                print(f"RAG初始化失败，将使用基础prompt: {str(e)}")
                self.use_rag = False
    
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
                
                # AI智能分析（不再使用固定词汇库）
                result["enhancement_info"]["ai_analysis_enabled"] = True
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
        """生成增强的翻译prompt，支持混合语言处理和RAG增强"""
        # 如果启用RAG且有RAG增强器，使用RAG增强的prompt
        if self.use_rag and self.rag_enhancer:
            try:
                rag_prompt = self.rag_enhancer.generate_enhanced_prompt(
                    text, source_lang, target_lang, use_rag=True, top_k=RAG_TOP_K
                )
                # 在RAG prompt基础上添加混合语言处理
                mixed_analysis = self.mixed_language_processor.preprocess_for_translation(text, source_lang, target_lang)
                if mixed_analysis['is_mixed_language']:
                    # 在RAG prompt的【翻译要求】前插入混合语言提示
                    if "【翻译要求】" in rag_prompt:
                        mixed_lang_section = "\n注意：文本包含混合语言内容，请按以下要求处理：\n"
                        mixed_lang_section += "1. 保持英语专有名词、缩写、品牌名等不翻译\n"
                        mixed_lang_section += "2. 确保翻译自然流畅，符合目标语言习惯\n"
                        mixed_lang_section += "3. 对于技术术语，优先使用目标语言的标准译法\n\n"
                        rag_prompt = rag_prompt.replace("【翻译要求】", mixed_lang_section + "【翻译要求】")
                    else:
                        # 如果没有【翻译要求】部分，添加到末尾
                        mixed_lang_section = "\n\n注意：文本包含混合语言内容，请按以下要求处理：\n"
                        mixed_lang_section += "1. 保持英语专有名词、缩写、品牌名等不翻译\n"
                        mixed_lang_section += "2. 确保翻译自然流畅，符合目标语言习惯\n"
                        rag_prompt = rag_prompt.replace(f"\n原文：{text}", mixed_lang_section + f"\n原文：{text}")
                return rag_prompt
            except Exception as e:
                print(f"RAG prompt生成失败，使用基础增强prompt: {str(e)}")
                # 降级到原有方式
                return self._generate_fallback_enhanced_prompt(text, source_lang, target_lang)
        else:
            # 使用原有的增强prompt（无RAG）
            return self._generate_fallback_enhanced_prompt(text, source_lang, target_lang)
    
    def _generate_fallback_enhanced_prompt(self, text: str, source_lang: str, target_lang: str) -> str:
        """生成基础的增强prompt（无RAG时使用）"""
        # 检测混合语言
        mixed_analysis = self.mixed_language_processor.preprocess_for_translation(text, source_lang, target_lang)
        
        base_prompt = f"请将以下{source_lang}文本翻译成{target_lang}。\n\n"
        
        # 混合语言处理
        if mixed_analysis['is_mixed_language']:
            base_prompt += "注意：文本包含混合语言内容，请按以下要求处理：\n"
            base_prompt += "1. 保持英语专有名词、缩写、品牌名等不翻译\n"
            base_prompt += "2. 确保翻译自然流畅，符合目标语言习惯\n"
            base_prompt += "3. 对于技术术语，优先使用目标语言的标准译法\n\n"
        
        # 智能分析指导
        base_prompt += "翻译分析要求：\n"
        base_prompt += "1. 仔细分析文本中的文化特定表达、习语、网络用语等\n"
        base_prompt += "2. 理解字面意义与实际意义的差异\n"
        base_prompt += "3. 识别可能的文化背景和语境\n"
        base_prompt += "4. 考虑目标语言的文化适应性\n\n"
        
        base_prompt += "翻译原则：\n"
        base_prompt += "1. 保持原文的语调和情感\n"
        base_prompt += "2. 确保翻译自然流畅\n"
        base_prompt += "3. 对于文化特定表达，提供准确且符合目标语言习惯的翻译\n"
        base_prompt += "4. 只返回翻译结果，不要添加解释\n\n"
        base_prompt += f"原文：{text}"
        
        return base_prompt
    
    
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