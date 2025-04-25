import json
from typing import List, Dict
from llama_index import Document, VectorStoreIndex, ServiceContext
from llama_index.node_parser import SimpleNodeParser
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.vector_stores import ChromaVectorStore
import chromadb
from app.config import (
    CHROMA_DB_PATH,
    EMBEDDING_MODEL_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)

class DocumentProcessor:
    def __init__(self):
        # 初始化ChromaDB客户端
        self.chroma_client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
        
        # 初始化嵌入模型
        self.embed_model = HuggingFaceEmbedding(
            model_name=EMBEDDING_MODEL_NAME
        )
        
        # 初始化节点解析器
        self.node_parser = SimpleNodeParser.from_defaults(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        
    def process_document(
        self,
        content_blocks: List[Dict],
        version_id: int,
        doc_base_id: int,
        project_id: str
    ) -> List[Dict]:
        """
        处理文档内容：
        1. 将内容块转换为Document对象
        2. 解析为节点
        3. 向量化并存储到ChromaDB
        4. 返回处理后的块信息（包含html_id）
        """
        # 为每个内容块创建唯一的html_id
        processed_blocks = []
        for block in content_blocks:
            block_type = block['type']
            sequence = block['sequence']
            html_id = f"doc_{version_id}_{block_type}_{sequence}"
            
            processed_block = {
                **block,
                'html_id': html_id,
                'version_id': version_id,
                'doc_base_id': doc_base_id,
                'project_id': project_id
            }
            processed_blocks.append(processed_block)
            
        # 创建Document对象
        documents = [
            Document(
                text=block['content'],
                metadata={
                    'html_id': block['html_id'],
                    'version_id': version_id,
                    'doc_base_id': doc_base_id,
                    'project_id': project_id,
                    'block_type': block['type'],
                    'sequence_in_doc': block['sequence']
                }
            )
            for block in processed_blocks
        ]
        
        # 解析为节点
        nodes = self.node_parser.get_nodes_from_documents(documents)
        
        # 获取或创建collection
        collection_name = f"version_{version_id}"
        collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"version_id": version_id}
        )
        
        # 创建向量存储
        vector_store = ChromaVectorStore(
            chroma_collection=collection
        )
        
        # 创建索引
        service_context = ServiceContext.from_defaults(
            embed_model=self.embed_model,
            node_parser=self.node_parser
        )
        index = VectorStoreIndex.from_documents(
            documents,
            service_context=service_context,
            vector_store=vector_store
        )
        
        return processed_blocks
        
    def query_document(
        self,
        query_text: str,
        version_id: int,
        top_k: int = 5
    ) -> List[Dict]:
        """
        查询文档内容
        返回相关的文档块及其元数据
        """
        collection_name = f"version_{version_id}"
        collection = self.chroma_client.get_collection(name=collection_name)
        
        # 创建查询索引
        vector_store = ChromaVectorStore(chroma_collection=collection)
        index = VectorStoreIndex.from_vector_store(
            vector_store,
            service_context=ServiceContext.from_defaults(
                embed_model=self.embed_model
            )
        )
        
        # 执行查询
        query_engine = index.as_query_engine(
            similarity_top_k=top_k
        )
        response = query_engine.query(query_text)
        
        # 提取结果
        source_nodes = response.source_nodes
        results = []
        for node in source_nodes:
            results.append({
                'content': node.text,
                'metadata': node.metadata,
                'score': node.score if hasattr(node, 'score') else None
            })
            
        return results 