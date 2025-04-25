import json
import requests
from typing import List, Dict, Optional
from app.config import LLM_API_ENDPOINT, LLM_MODEL_NAME

class LLMService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_endpoint = LLM_API_ENDPOINT
        self.model_name = LLM_MODEL_NAME
        
    def _build_prompt(self, query: str, context_blocks: List[Dict]) -> str:
        """构建提示词"""
        context_texts = []
        for block in context_blocks:
            content = block['content']
            block_type = block['metadata']['block_type']
            if block_type == 'table':
                context_texts.append(f"表格内容：\n{content}")
            else:
                context_texts.append(content)
                
        context = "\n\n".join(context_texts)
        
        prompt = f"""请基于以下文档内容回答用户的问题。如果无法从文档内容中找到答案，请明确说明。
        
文档内容：
{context}

用户问题：
{query}

请提供准确、完整的回答，并尽可能引用原文内容。"""
        
        return prompt
        
    def generate_response(
        self,
        query: str,
        context_blocks: List[Dict]
    ) -> Dict[str, str]:
        """
        生成回答
        返回：{
            'answer': str,  # 生成的回答
            'error': Optional[str]  # 如果发生错误，返回错误信息
        }
        """
        prompt = self._build_prompt(query, context_blocks)
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        data = {
            'model': self.model_name,
            'messages': [
                {'role': 'user', 'content': prompt}
            ]
        }
        
        try:
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            if 'error' in result:
                return {
                    'answer': None,
                    'error': f"API错误: {result['error']}"
                }
                
            answer = result['choices'][0]['message']['content']
            return {
                'answer': answer,
                'error': None
            }
            
        except requests.RequestException as e:
            return {
                'answer': None,
                'error': f"请求失败: {str(e)}"
            }
        except Exception as e:
            return {
                'answer': None,
                'error': f"处理失败: {str(e)}"
            } 