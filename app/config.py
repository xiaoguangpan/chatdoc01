import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 数据库配置
SQLITE_DB_PATH = BASE_DIR / "db" / "app_data.db"
CHROMA_DB_PATH = BASE_DIR / "db" / "chroma_db"

# 文档存储配置
DOCS_STORAGE_PATH = BASE_DIR / "docs_storage"

# 嵌入模型配置
EMBEDDING_MODEL_NAME = "bge-base-zh-v1.5"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

# LLM API配置
LLM_API_ENDPOINT = "https://api.volcengine.com/ml-platform/v1/model/invoke"
LLM_MODEL_NAME = "doubao-1-5-thinking-pro-250415"

# 创建必要的目录
REQUIRED_DIRS = [
    SQLITE_DB_PATH.parent,
    CHROMA_DB_PATH,
    DOCS_STORAGE_PATH
]

for dir_path in REQUIRED_DIRS:
    os.makedirs(dir_path, exist_ok=True) 