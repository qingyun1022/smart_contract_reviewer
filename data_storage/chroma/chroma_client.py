from typing import List, Dict, Any, Optional
import os
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from common.logger import get_logger
from common.config import get_config

logger = get_logger(__name__)
config = get_config()

class ChromaClient:
    """Chroma向量数据库客户端，用于存储和检索向量化的文本数据"""
    
    def __init__(self, persist_directory: str = None):
        """初始化Chroma客户端
        
        Args:
            persist_directory: 持久化目录，如果为None则使用配置中的默认目录
        """
        if persist_directory is None:
            persist_directory = config.get("chroma", {}).get("persist_directory", "data/chroma_db")
            
        # 确保目录存在
        os.makedirs(persist_directory, exist_ok=True)
        
        # 初始化客户端
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # 默认使用sentence-transformers嵌入函数
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=config.get("embedding", {}).get("model_name", "all-MiniLM-L6-v2")
        )
        
        logger.info(f"ChromaDB客户端初始化完成，持久化目录: {persist_directory}")
    
    def create_collection(self, collection_name: str, metadata: Dict[str, Any] = None) -> Any:
        """创建或获取集合
        
        Args:
            collection_name: 集合名称
            metadata: 集合元数据
            
        Returns:
            集合对象
        """
        try:
            collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
                metadata=metadata
            )
            logger.info(f"成功创建/获取集合: {collection_name}")
            return collection
        except Exception as e:
            logger.error(f"创建/获取集合失败: {str(e)}")
            raise
    
    def add_documents(self, collection_name: str, documents: List[str], 
                      metadatas: List[Dict[str, Any]] = None, ids: List[str] = None) -> bool:
        """向集合添加文档
        
        Args:
            collection_name: 集合名称
            documents: 文档列表
            metadatas: 文档元数据列表
            ids: 文档ID列表
            
        Returns:
            是否成功添加
        """
        try:
            collection = self.client.get_collection(collection_name, self.embedding_function)
            
            # 如果没有提供ID，生成唯一ID
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in range(len(documents))]
            
            # 如果没有提供元数据，使用空字典
            if metadatas is None:
                metadatas = [{} for _ in range(len(documents))]
            
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"成功添加{len(documents)}个文档到集合{collection_name}")
            return True
        except Exception as e:
            logger.error(f"添加文档失败: {str(e)}")
            return False
    
    def query(self, collection_name: str, query_text: str, n_results: int = 5, 
              filter_dict: Dict[str, Any] = None) -> Dict[str, Any]:
        """查询最相似的文档
        
        Args:
            collection_name: 集合名称
            query_text: 查询文本
            n_results: 返回结果数量
            filter_dict: 过滤条件
            
        Returns:
            查询结果
        """
        try:
            collection = self.client.get_collection(collection_name, self.embedding_function)
            
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=filter_dict
            )
            
            logger.info(f"成功查询集合{collection_name}，找到{len(results['documents'][0])}个结果")
            return results
        except Exception as e:
            logger.error(f"查询失败: {str(e)}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}
    
    def delete_collection(self, collection_name: str) -> bool:
        """删除集合
        
        Args:
            collection_name: 集合名称
            
        Returns:
            是否成功删除
        """
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"成功删除集合: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"删除集合失败: {str(e)}")
            return False
