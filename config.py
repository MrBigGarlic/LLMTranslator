"""
简化版配置文件 - 只保留DeepSeek翻译分析所需配置
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-7a4f0143ac12497d931f39bf161941c5')
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')

# DeepL API配置
DEEPL_API_KEY = os.getenv('DEEPL_API_KEY', '6893c45b-e4d8-4d59-a52d-40334a2c9706:fx')

# 支持的语言映射
LANGUAGE_MAPPING = {
    '中文': 'Chinese',
    '英语': 'English', 
    '越南语': 'Vietnamese',
    '马来语': 'Malay',
    '泰语': 'Thai',
    '印尼语': 'Indonesian',
    '菲律宾语': 'Filipino',
    '缅甸语': 'Burmese',
    '老挝语': 'Lao',
    '柬埔寨语': 'Khmer'
}

# 语义相似度阈值
SIMILARITY_THRESHOLD = 0.7

# RAG配置
ENABLE_RAG = os.getenv('ENABLE_RAG', 'true').lower() == 'true'
KNOWLEDGE_BASE_PATH = os.getenv('KNOWLEDGE_BASE_PATH', None)
RAG_TOP_K = int(os.getenv('RAG_TOP_K', '5'))
RAG_MIN_CONFIDENCE = float(os.getenv('RAG_MIN_CONFIDENCE', '0.3'))

# 外部知识库API配置（可选）
USE_EXTERNAL_APIS = os.getenv('USE_EXTERNAL_APIS', 'false').lower() == 'true'
YOUDAO_APP_KEY = os.getenv('YOUDAO_APP_KEY', None)
YOUDAO_APP_SECRET = os.getenv('YOUDAO_APP_SECRET', None)
