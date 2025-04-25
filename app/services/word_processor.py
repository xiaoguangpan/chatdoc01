import os
import sys
import win32com.client
from typing import List, Dict, Tuple, Optional
import pythoncom
import logging

logger = logging.getLogger(__name__)

class WordProcessor:
    def __init__(self):
        self.word_app = None
        
    def initialize(self):
        """初始化Word应用程序实例"""
        try:
            pythoncom.CoInitialize()
            self.word_app = win32com.client.Dispatch("Word.Application")
            self.word_app.Visible = False
        except Exception as e:
            logger.error(f"初始化Word应用程序失败: {str(e)}")
            raise
            
    def cleanup(self):
        """清理Word应用程序实例"""
        try:
            if self.word_app:
                self.word_app.Quit()
                self.word_app = None
            pythoncom.CoUninitialize()
        except Exception as e:
            logger.error(f"清理Word应用程序失败: {str(e)}")
            
    def __enter__(self):
        """上下文管理器入口"""
        self.initialize()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()
        
    def convert_table_to_markdown(self, table) -> str:
        """将Word表格转换为Markdown格式"""
        try:
            rows = table.Rows.Count
            cols = table.Columns.Count
            
            # 构建表头
            header = "|"
            separator = "|"
            for col in range(1, cols + 1):
                cell_text = table.Cell(1, col).Range.Text.strip('\r\x07')
                header += f" {cell_text} |"
                separator += " --- |"
                
            # 构建表格内容
            content = []
            for row in range(2, rows + 1):
                row_text = "|"
                for col in range(1, cols + 1):
                    cell_text = table.Cell(row, col).Range.Text.strip('\r\x07')
                    row_text += f" {cell_text} |"
                content.append(row_text)
                
            # 组合完整的Markdown表格
            markdown_table = f"{header}\n{separator}\n" + "\n".join(content)
            return markdown_table
        except Exception as e:
            logger.error(f"转换表格到Markdown格式失败: {str(e)}")
            return f"[表格转换失败: {str(e)}]"
            
    def extract_content(self, file_path: str) -> List[Dict]:
        """
        从Word文档中提取内容
        返回格式: List[Dict]，每个Dict包含:
        {
            'type': 'paragraph' | 'table',
            'content': str,
            'sequence': int
        }
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        try:
            doc = self.word_app.Documents.Open(file_path)
            content_blocks = []
            sequence = 0
            
            # 遍历文档中的所有内容
            for item in doc.Content.Paragraphs:
                # 检查段落是否在表格内
                if item.Range.Tables.Count == 0:
                    text = item.Range.Text.strip('\r\x07')
                    if text:  # 只添加非空段落
                        content_blocks.append({
                            'type': 'paragraph',
                            'content': text,
                            'sequence': sequence
                        })
                        sequence += 1
                        
            # 单独处理表格
            for table in doc.Tables:
                markdown_table = self.convert_table_to_markdown(table)
                content_blocks.append({
                    'type': 'table',
                    'content': markdown_table,
                    'sequence': sequence
                })
                sequence += 1
                
            doc.Close()
            return content_blocks
            
        except Exception as e:
            logger.error(f"处理Word文档失败: {str(e)}")
            if 'doc' in locals():
                try:
                    doc.Close()
                except:
                    pass
            raise 