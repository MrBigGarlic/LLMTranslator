"""
混合语言处理器
识别和处理混合语言文本，如中文中掺杂英语单词
"""
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class LanguageSegment:
    """语言片段"""
    text: str
    language: str  # 'chinese', 'english', 'mixed', 'unknown'
    start_pos: int
    end_pos: int
    confidence: float


class MixedLanguageProcessor:
    """混合语言处理器"""
    
    def __init__(self):
        # 英语单词模式（包括缩写、专有名词等）
        self.english_patterns = [
            # 常见缩写（2-6个大写字母）
            r'[A-Z]{2,6}',  # NBA, CPU, API, HTTP等
            # 品牌名和专有名词（首字母大写）
            r'[A-Z][a-z]+[A-Z][a-z]*',  # iPhone, YouTube等
            # 标准英语单词（纯字母）
            r'[a-zA-Z]+',  # 纯字母单词
        ]
        
        # 中文模式
        self.chinese_patterns = [
            r'[\u4e00-\u9fff]+',  # 中文字符
            r'[\u3400-\u4dbf]+',  # 扩展A区
            r'[\u20000-\u2a6df]+',  # 扩展B区
        ]
        
        # 常见混合语言词汇库
        self.mixed_vocabulary = {
            # 技术术语
            'NBA': '美国职业篮球联赛',
            'CBA': '中国职业篮球联赛', 
            'CPU': '中央处理器',
            'GPU': '图形处理器',
            'API': '应用程序接口',
            'HTTP': '超文本传输协议',
            'URL': '统一资源定位符',
            'HTML': '超文本标记语言',
            'CSS': '层叠样式表',
            'JavaScript': 'JavaScript编程语言',
            'Python': 'Python编程语言',
            'Java': 'Java编程语言',
            'C++': 'C++编程语言',
            'AI': '人工智能',
            'ML': '机器学习',
            'DL': '深度学习',
            'NLP': '自然语言处理',
            'CV': '计算机视觉',
            'IoT': '物联网',
            'VR': '虚拟现实',
            'AR': '增强现实',
            '5G': '第五代移动通信技术',
            'WiFi': '无线网络',
            'Bluetooth': '蓝牙',
            'USB': '通用串行总线',
            'HDMI': '高清多媒体接口',
            'SSD': '固态硬盘',
            'RAM': '随机存取存储器',
            'ROM': '只读存储器',
            'OS': '操作系统',
            'UI': '用户界面',
            'UX': '用户体验',
            'SEO': '搜索引擎优化',
            'SEM': '搜索引擎营销',
            'CRM': '客户关系管理',
            'ERP': '企业资源规划',
            'SaaS': '软件即服务',
            'PaaS': '平台即服务',
            'IaaS': '基础设施即服务',
            'B2B': '企业对企业',
            'B2C': '企业对消费者',
            'C2C': '消费者对消费者',
            'O2O': '线上到线下',
            'KPI': '关键绩效指标',
            'ROI': '投资回报率',
            'CTO': '首席技术官',
            'CEO': '首席执行官',
            'CFO': '首席财务官',
            'COO': '首席运营官',
            'CTO': '首席技术官',
            'PM': '产品经理',
            'UI/UX': '用户界面/用户体验',
            'QA': '质量保证',
            'DevOps': '开发运维',
            'Git': 'Git版本控制系统',
            'GitHub': 'GitHub代码托管平台',
            'Docker': 'Docker容器技术',
            'Kubernetes': 'Kubernetes容器编排',
            'AWS': '亚马逊云服务',
            'Azure': '微软云服务',
            'GCP': '谷歌云平台',
            'Linux': 'Linux操作系统',
            'Windows': 'Windows操作系统',
            'macOS': 'macOS操作系统',
            'iOS': 'iOS操作系统',
            'Android': 'Android操作系统',
            'Chrome': 'Chrome浏览器',
            'Firefox': 'Firefox浏览器',
            'Safari': 'Safari浏览器',
            'Edge': 'Edge浏览器',
            'Word': 'Microsoft Word',
            'Excel': 'Microsoft Excel',
            'PowerPoint': 'Microsoft PowerPoint',
            'Photoshop': 'Adobe Photoshop',
            'Illustrator': 'Adobe Illustrator',
            'Premiere': 'Adobe Premiere Pro',
            'After Effects': 'Adobe After Effects',
            'Sketch': 'Sketch设计工具',
            'Figma': 'Figma设计工具',
            'Slack': 'Slack协作工具',
            'Zoom': 'Zoom视频会议',
            'Teams': 'Microsoft Teams',
            'Discord': 'Discord聊天平台',
            'Telegram': 'Telegram即时通讯',
            'WhatsApp': 'WhatsApp即时通讯',
            'WeChat': '微信',
            'QQ': 'QQ即时通讯',
            'TikTok': 'TikTok短视频平台',
            'Instagram': 'Instagram社交平台',
            'Facebook': 'Facebook社交平台',
            'Twitter': 'Twitter社交平台',
            'LinkedIn': 'LinkedIn职业社交',
            'YouTube': 'YouTube视频平台',
            'Netflix': 'Netflix流媒体',
            'Spotify': 'Spotify音乐流媒体',
            'Apple': '苹果公司',
            'Google': '谷歌公司',
            'Microsoft': '微软公司',
            'Amazon': '亚马逊公司',
            'Meta': 'Meta公司',
            'Tesla': '特斯拉公司',
            'Uber': 'Uber出行服务',
            'Airbnb': 'Airbnb住宿服务',
            'PayPal': 'PayPal支付服务',
            'Visa': 'Visa信用卡',
            'Mastercard': '万事达信用卡',
            'Bitcoin': '比特币',
            'Ethereum': '以太坊',
            'Blockchain': '区块链',
            'NFT': '非同质化代币',
            'DeFi': '去中心化金融',
            'Web3': 'Web3.0',
            'Metaverse': '元宇宙',
            'Crypto': '加密货币',
            'Mining': '挖矿',
            'Trading': '交易',
            'HODL': '持有',
            'FOMO': '错失恐惧症',
            'YOLO': '你只活一次',
            'FOMO': '错失恐惧症',
            'LOL': '大声笑',
            'OMG': '我的天',
            'WTF': '什么鬼',
            'BTW': '顺便说一下',
            'FYI': '供您参考',
            'ASAP': '尽快',
            'ETA': '预计到达时间',
            'FAQ': '常见问题',
            'VIP': '贵宾',
            'CEO': '首席执行官',
            'CTO': '首席技术官',
            'CFO': '首席财务官',
            'COO': '首席运营官',
            'PM': '产品经理',
            'HR': '人力资源',
            'PR': '公共关系',
            'R&D': '研发',
            'IT': '信息技术',
            'QA': '质量保证',
            'QC': '质量控制',
            'SOP': '标准操作程序',
            'GDP': '国内生产总值',
            'CPI': '消费者价格指数',
            'PPI': '生产者价格指数',
            'IPO': '首次公开募股',
            'M&A': '并购',
            'IPO': '首次公开募股',
            'VC': '风险投资',
            'PE': '私募股权',
            'IPO': '首次公开募股',
            'SEC': '证券交易委员会',
            'FDA': '食品药品监督管理局',
            'WHO': '世界卫生组织',
            'UN': '联合国',
            'EU': '欧盟',
            'NATO': '北约',
            'UNESCO': '联合国教科文组织',
            'UNICEF': '联合国儿童基金会',
            'WTO': '世界贸易组织',
            'IMF': '国际货币基金组织',
            'World Bank': '世界银行',
            'OECD': '经济合作与发展组织',
            'G7': '七国集团',
            'G20': '二十国集团',
            'BRICS': '金砖国家',
            'ASEAN': '东南亚国家联盟',
            'APEC': '亚太经济合作组织',
            'OPEC': '石油输出国组织',
            'NASA': '美国国家航空航天局',
            'FBI': '联邦调查局',
            'CIA': '中央情报局',
            'NSA': '国家安全局',
            'IRS': '国税局',
            'CDC': '疾病控制与预防中心',
            'NIH': '国立卫生研究院',
            'DARPA': '国防高级研究计划局',
            'MIT': '麻省理工学院',
            'Harvard': '哈佛大学',
            'Stanford': '斯坦福大学',
            'Yale': '耶鲁大学',
            'Princeton': '普林斯顿大学',
            'Columbia': '哥伦比亚大学',
            'Berkeley': '加州大学伯克利分校',
            'Caltech': '加州理工学院',
            'CMU': '卡内基梅隆大学',
            'NYU': '纽约大学',
            'UCLA': '加州大学洛杉矶分校',
            'UCSD': '加州大学圣地亚哥分校',
            'UCSF': '加州大学旧金山分校',
            'UCI': '加州大学欧文分校',
            'UCD': '加州大学戴维斯分校',
            'UCSB': '加州大学圣巴巴拉分校',
            'UCSC': '加州大学圣克鲁兹分校',
            'UCR': '加州大学河滨分校',
            'UCM': '加州大学默塞德分校',
            'UCB': '加州大学伯克利分校',
            'UCLA': '加州大学洛杉矶分校',
            'UCSD': '加州大学圣地亚哥分校',
            'UCSF': '加州大学旧金山分校',
            'UCI': '加州大学欧文分校',
            'UCD': '加州大学戴维斯分校',
            'UCSB': '加州大学圣巴巴拉分校',
            'UCSC': '加州大学圣克鲁兹分校',
            'UCR': '加州大学河滨分校',
            'UCM': '加州大学默塞德分校',
            # 拟音词和网络用语
            'soga': '原来如此',
            'AppleU': '苹果公司',
            'GoogleU': '谷歌公司',
            'MicrosoftU': '微软公司',
            'AmazonU': '亚马逊公司',
            'MetaU': 'Meta公司',
            'TeslaU': '特斯拉公司',
            'UberU': 'Uber公司',
            'AirbnbU': 'Airbnb公司',
            'PayPalU': 'PayPal公司',
            'VisaU': 'Visa公司',
            'MastercardU': '万事达公司',
            'BitcoinU': '比特币',
            'EthereumU': '以太坊',
            'BlockchainU': '区块链',
            'NFTU': '非同质化代币',
            'DeFiU': '去中心化金融',
            'Web3U': 'Web3.0',
            'MetaverseU': '元宇宙',
            'CryptoU': '加密货币',
            'MiningU': '挖矿',
            'TradingU': '交易',
            'HODLU': '持有',
            'FOMOU': '错失恐惧症',
            'YOLOU': '你只活一次',
            'FOMOU': '错失恐惧症',
            'LOLU': '大声笑',
            'OMGU': '我的天',
            'WTFU': '什么鬼',
            'BTWU': '顺便说一下',
            'FYIU': '供您参考',
            'ASAPU': '尽快',
            'ETAU': '预计到达时间',
            'FAQU': '常见问题',
            'VIPU': '贵宾',
            'CEOU': '首席执行官',
            'CTOU': '首席技术官',
            'CFOU': '首席财务官',
            'COOU': '首席运营官',
            'PMU': '产品经理',
            'HRU': '人力资源',
            'PRU': '公共关系',
            'R&DU': '研发',
            'ITU': '信息技术',
            'QAU': '质量保证',
            'QCU': '质量控制',
            'SOPU': '标准操作程序',
            'GDPU': '国内生产总值',
            'CPIU': '消费者价格指数',
            'PPIU': '生产者价格指数',
            'IPOU': '首次公开募股',
            'M&AU': '并购',
            'IPOU': '首次公开募股',
            'VCU': '风险投资',
            'PEU': '私募股权',
            'IPOU': '首次公开募股',
            'SECU': '证券交易委员会',
            'FDAU': '食品药品监督管理局',
            'WHOU': '世界卫生组织',
            'UNU': '联合国',
            'EUU': '欧盟',
            'NATOU': '北约',
            'UNESCOU': '联合国教科文组织',
            'UNICEFU': '联合国儿童基金会',
            'WTOU': '世界贸易组织',
            'IMFU': '国际货币基金组织',
            'World BankU': '世界银行',
            'OECDU': '经济合作与发展组织',
            'G7U': '七国集团',
            'G20U': '二十国集团',
            'BRICSU': '金砖国家',
            'ASEANU': '东南亚国家联盟',
            'APECU': '亚太经济合作组织',
            'OPECU': '石油输出国组织',
            'NASAU': '美国国家航空航天局',
            'FBIU': '联邦调查局',
            'CIAU': '中央情报局',
            'NSU': '国家安全局',
            'IRSU': '国税局',
            'CDCU': '疾病控制与预防中心',
            'NIHU': '国立卫生研究院',
            'DARPU': '国防高级研究计划局',
            'MITU': '麻省理工学院',
            'HarvardU': '哈佛大学',
            'StanfordU': '斯坦福大学',
            'YaleU': '耶鲁大学',
            'PrincetonU': '普林斯顿大学',
            'ColumbiaU': '哥伦比亚大学',
            'BerkeleyU': '加州大学伯克利分校',
            'CaltechU': '加州理工学院',
            'CMUU': '卡内基梅隆大学',
            'NYUU': '纽约大学',
            'UCLAU': '加州大学洛杉矶分校',
            'UCSDU': '加州大学圣地亚哥分校',
            'UCSFU': '加州大学旧金山分校',
            'UCIU': '加州大学欧文分校',
            'UCDU': '加州大学戴维斯分校',
            'UCSBU': '加州大学圣巴巴拉分校',
            'UCSCU': '加州大学圣克鲁兹分校',
            'UCRU': '加州大学河滨分校',
            'UCMU': '加州大学默塞德分校',
            'UCBU': '加州大学伯克利分校',
            'UCLAU': '加州大学洛杉矶分校',
            'UCSDU': '加州大学圣地亚哥分校',
            'UCSFU': '加州大学旧金山分校',
            'UCIU': '加州大学欧文分校',
            'UCDU': '加州大学戴维斯分校',
            'UCSBU': '加州大学圣巴巴拉分校',
            'UCSCU': '加州大学圣克鲁兹分校',
            'UCRU': '加州大学河滨分校',
            'UCMU': '加州大学默塞德分校',
        }
    
    def analyze_mixed_language(self, text: str) -> List[LanguageSegment]:
        """
        分析混合语言文本
        
        Args:
            text: 输入文本
            
        Returns:
            语言片段列表
        """
        segments = []
        
        # 先识别英语词汇
        english_matches = []
        for pattern in self.english_patterns:
            for match in re.finditer(pattern, text):
                english_matches.append((match.start(), match.end(), match.group()))
        
        # 按位置排序英语匹配
        english_matches.sort(key=lambda x: x[0])
        
        # 去重（相同位置的匹配）
        unique_english_matches = []
        seen_positions = set()
        for start, end, content in english_matches:
            position_key = (start, end)
            if position_key not in seen_positions:
                unique_english_matches.append((start, end, content))
                seen_positions.add(position_key)
        
        english_matches = unique_english_matches
        
        # 处理文本，标记英语部分
        processed_text = text
        english_positions = set()
        
        for start, end, content in english_matches:
            # 标记英语位置
            for i in range(start, end):
                english_positions.add(i)
            
            # 添加英语片段
            confidence = self._calculate_confidence(content, 'english')
            segments.append(LanguageSegment(
                text=content,
                language='english',
                start_pos=start,
                end_pos=end,
                confidence=confidence
            ))
        
        # 识别中文片段（排除英语部分）
        chinese_matches = []
        for pattern in self.chinese_patterns:
            for match in re.finditer(pattern, text):
                start, end = match.start(), match.end()
                # 检查是否与英语重叠
                if not any(i in english_positions for i in range(start, end)):
                    chinese_matches.append((start, end, match.group()))
        
        # 添加中文片段
        for start, end, content in chinese_matches:
            confidence = self._calculate_confidence(content, 'chinese')
            segments.append(LanguageSegment(
                text=content,
                language='chinese',
                start_pos=start,
                end_pos=end,
                confidence=confidence
            ))
        
        # 按位置排序
        segments.sort(key=lambda x: x.start_pos)
        
        return segments
    
    def _calculate_confidence(self, text: str, lang_type: str) -> float:
        """计算语言识别置信度"""
        if lang_type == 'english':
            # 检查是否在词汇库中
            if text in self.mixed_vocabulary:
                return 0.95
            # 检查是否为常见英语模式
            if re.match(r'^[A-Z]{2,6}$', text):  # 缩写
                return 0.9
            if re.match(r'^[a-zA-Z]+$', text):  # 纯字母
                return 0.8
            return 0.7
        elif lang_type == 'chinese':
            return 0.95
        return 0.5
    
    def preprocess_for_translation(self, text: str, source_lang: str, target_lang: str) -> Dict[str, any]:
        """
        预处理混合语言文本用于翻译
        
        Args:
            text: 输入文本
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            预处理结果
        """
        segments = self.analyze_mixed_language(text)
        
        # 分析文本特征
        has_english = any(seg.language == 'english' for seg in segments)
        has_chinese = any(seg.language == 'chinese' for seg in segments)
        is_mixed = has_english and has_chinese
        
        # 生成翻译提示
        translation_hints = []
        if is_mixed:
            translation_hints.append("检测到混合语言文本")
            
            # 识别英语词汇
            english_words = [seg.text for seg in segments if seg.language == 'english']
            if english_words:
                translation_hints.append(f"包含英语词汇: {', '.join(english_words)}")
                
                # 提供翻译建议
                for word in english_words:
                    if word in self.mixed_vocabulary:
                        translation_hints.append(f"'{word}' 建议翻译为: {self.mixed_vocabulary[word]}")
        
        return {
            'original_text': text,
            'segments': segments,
            'is_mixed_language': is_mixed,
            'has_english': has_english,
            'has_chinese': has_chinese,
            'translation_hints': translation_hints,
            'english_words': [seg.text for seg in segments if seg.language == 'english'],
            'chinese_words': [seg.text for seg in segments if seg.language == 'chinese']
        }
    
    def generate_mixed_language_prompt(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        为混合语言文本生成翻译提示
        
        Args:
            text: 输入文本
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            增强的翻译提示
        """
        analysis = self.preprocess_for_translation(text, source_lang, target_lang)
        
        base_prompt = f"请将以下{source_lang}文本翻译成{target_lang}。"
        
        if analysis['is_mixed_language']:
            base_prompt += "\n\n注意：文本包含混合语言内容，请按以下要求处理：\n"
            base_prompt += "1. 保持英语专有名词、缩写、品牌名等不翻译\n"
            base_prompt += "2. 确保翻译自然流畅，符合目标语言习惯\n"
            base_prompt += "3. 对于技术术语，优先使用目标语言的标准译法\n"
            
            if analysis['translation_hints']:
                base_prompt += "\n特殊处理建议：\n"
                for hint in analysis['translation_hints']:
                    base_prompt += f"- {hint}\n"
        
        base_prompt += f"\n翻译要求：\n"
        base_prompt += f"1. 保持原文的语调和情感\n"
        base_prompt += f"2. 确保翻译自然流畅\n"
        base_prompt += f"3. 如有文化差异，请提供适当的解释\n"
        base_prompt += f"4. 只返回翻译结果，不要添加解释\n\n"
        base_prompt += f"原文：{text}"
        
        return base_prompt
