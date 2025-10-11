"""
简化版输入处理模块 - 支持短文本终端输入和长文本文件输入
"""
import os

class SimpleInputHandler:
    """简化版输入处理器"""
    
    def __init__(self):
        self.input_file = "input.txt"
        self.output_file = "output.txt"
    
    def get_text_input(self, source_lang: str) -> str:
        """
        获取文本输入 - 支持短文本终端输入和长文本文件输入
        
        Args:
            source_lang: 源语言
            
        Returns:
            输入的文本
        """
        print(f"\n请选择输入方式:")
        print("  1. 短文本输入（直接在终端中输入）")
        print("  2. 长文本输入（从 input.txt 文件读取）")
        
        while True:
            choice = input("请选择 (1-2): ").strip()
            
            if choice == "1":
                return self._get_short_text_input(source_lang)
            elif choice == "2":
                return self._get_long_text_input()
            else:
                print("无效选择，请重新输入")
    
    def _get_short_text_input(self, source_lang: str) -> str:
        """
        获取短文本输入（终端输入）
        
        Args:
            source_lang: 源语言
            
        Returns:
            输入的文本
        """
        print(f"\n请输入要翻译的{source_lang}文本:")
        print("提示: 适合短文本，直接在终端中输入")
        
        while True:
            text = input("> ").strip()
            if text:
                print(f"已输入文本，长度: {len(text)} 字符")
                return text
            else:
                print("文本不能为空，请重新输入")
    
    def _get_long_text_input(self) -> str:
        """
        获取长文本输入（从文件读取）
        
        Returns:
            文件中的文本
        """
        print(f"\n从文件读取长文本:")
        print(f"提示: 程序将从 {self.input_file} 文件读取文本")
        
        # 检查文件是否存在
        if not os.path.exists(self.input_file):
            print(f"文件 {self.input_file} 不存在")
            print(f"请创建 {self.input_file} 文件并放入要翻译的文本")
            return ""
        
        try:
            # 尝试多种编码读取文件
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
            content = None
            used_encoding = None
            
            for encoding in encodings:
                try:
                    with open(self.input_file, 'r', encoding=encoding) as f:
                        content = f.read().strip()
                    used_encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                print("无法读取文件，请检查文件编码")
                return ""
            
            if not content:
                print("文件为空，请检查文件内容")
                return ""
            
            print(f"成功读取文件，使用编码: {used_encoding}")
            print(f"文本长度: {len(content)} 字符")
            return content
            
        except Exception as e:
            print(f"读取文件失败: {str(e)}")
            return ""
    
    def save_results(self, original_text: str, target_translation: str, back_translation: str, 
                    source_lang: str, target_lang: str, semantic_analysis: dict = None, 
                    is_long_text: bool = False, chunks_count: int = 1) -> bool:
        """
        保存翻译结果到 output.txt，包含相似度检测报告
        
        Args:
            original_text: 原始文本
            target_translation: 小语种翻译
            back_translation: 回译文本
            source_lang: 源语言
            target_lang: 目标语言
            semantic_analysis: 语义分析结果
            is_long_text: 是否为长文本
            chunks_count: 分段数量
            
        Returns:
            是否保存成功
        """
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("DeepSeek翻译分析结果\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"源语言: {source_lang}\n")
                f.write(f"目标语言: {target_lang}\n")
                f.write(f"文本长度: {len(original_text)} 字符\n")
                f.write(f"是否长文本: {'是' if is_long_text else '否'}\n")
                if is_long_text:
                    f.write(f"分段数量: {chunks_count} 段\n")
                f.write("\n")
                
                f.write("原始文本:\n")
                f.write("-" * 30 + "\n")
                f.write(original_text + "\n\n")
                
                f.write(f"{target_lang}翻译:\n")
                f.write("-" * 30 + "\n")
                f.write(target_translation + "\n\n")
                
                f.write(f"{source_lang}回译:\n")
                f.write("-" * 30 + "\n")
                f.write(back_translation + "\n\n")
                
                # 添加相似度检测报告
                if semantic_analysis:
                    f.write("DeepSeek语义一致性分析报告:\n")
                    f.write("-" * 30 + "\n")
                    f.write(f"相似度分数: {semantic_analysis.get('similarity_score', 0.0):.3f}\n")
                    f.write(f"一致性等级: {semantic_analysis.get('consistency_level', '未知')}\n")
                    f.write(f"是否一致: {'是' if semantic_analysis.get('is_consistent', False) else '否'}\n")
                    f.write(f"动态阈值: {semantic_analysis.get('threshold', 0.7):.3f}\n")
                    f.write(f"语义含义: {semantic_analysis.get('semantic_meaning', 'unknown')}\n")
                    f.write(f"置信度: {semantic_analysis.get('confidence', 0.0):.3f}\n\n")
                    
                    f.write("分析说明:\n")
                    f.write(f"{semantic_analysis.get('deepseek_analysis', '无分析说明')}\n\n")
                    
                    f.write("建议:\n")
                    f.write(f"{semantic_analysis.get('suggestion', '无建议')}\n\n")
                else:
                    f.write("语义分析: 未进行语义分析\n\n")
                
                # 长文本处理说明
                if is_long_text:
                    f.write("长文本处理说明:\n")
                    f.write("-" * 30 + "\n")
                    f.write(f"- 文本已自动分割为 {chunks_count} 段进行处理\n")
                    f.write("- 每段最大长度: 1000 字符\n")
                    f.write("- 段落间重叠: 100 字符\n")
                    f.write("- 处理方式: 分段翻译后合并\n\n")
                
                f.write("=" * 60 + "\n")
                f.write("翻译完成时间: " + str(os.popen('date').read().strip()) + "\n")
                f.write("=" * 60 + "\n")
            
            print(f"翻译结果和相似度检测报告已保存到 {self.output_file}")
            return True
            
        except Exception as e:
            print(f"保存结果失败: {str(e)}")
            return False