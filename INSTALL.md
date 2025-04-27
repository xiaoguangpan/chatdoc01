# 本地智能文档问答助手安装指南

## 环境要求

- Python 3.10 或 3.11（**不支持 3.12 及以上版本**，否则 torch 无法安装）
- Microsoft Word（用于处理加密文档，Windows 必须）
- 操作系统：Windows（如需解析 docx 加密文档）或 Mac/Linux（仅基础功能）

> **重要提示：**
> 安装前请先运行 `python --version`，确保 Python 版本为 3.10 或 3.11，否则请先更换 Python 版本！

## 安装步骤

1. 创建并激活 Python 虚拟环境（务必用 3.10/3.11）：
```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

2. 安装项目依赖：
```bash
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

3. 配置环境变量：
创建 `.env` 文件并添加以下配置：
```env
LLM_API_KEY=xxx
LLM_MODEL_NAME=xxx
EMBEDDING_MODEL=xxx
CHUNK_SIZE=512
CHUNK_OVERLAP=50
```

4. 初始化数据库：
```bash
python scripts/init_db.py
```

5. 启动应用：
```bash
python run.py
```

## 目录结构
```
chatdoc01/
├── app/
│   ├── api/
│   ├── models/
│   ├── services/
│   ├── static/
│   │   └── js/
│   ├── templates/
│   └── utils/
├── db/
│   └── chroma_db/
├── docs_storage/
├── scripts/
│   └── init_db.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## 常见问题解决方案

1. **numpy 版本冲突**
   - 问题：安装依赖时可能出现 numpy 版本冲突
   - 解决方案：先卸载现有 numpy，然后安装指定版本：
     ```bash
     pip uninstall numpy
     pip install numpy<2.0.0
     ```

2. **ChromaDB 初始化错误**
   - 问题：ChromaDB 可能无法正确初始化持久化存储
   - 解决方案：确保 db/chroma_db 目录存在且有写入权限

3. **依赖安装失败**
   - 问题：某些依赖包在默认源下载速度慢或失败
   - 解决方案：使用阿里云镜像源：
     ```bash
     pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
     ```

4. **Word COM 组件错误**
   - 问题：无法正确调用 Word COM 组件
   - 解决方案：
     - 确保已安装 Microsoft Word
     - 以管理员权限运行应用
     - 检查 pywin32 是否正确安装

5. **端口占用**
   - 问题：启动服务时提示端口被占用
   - 解决方案：
     - 使用不同端口：`uvicorn app.main:app --port 8001`
     - 或终止占用端口的进程

6. **内存占用过高**
   - 问题：处理大文档时内存占用过高
   - 解决方案：
     - 调整 CHUNK_SIZE 参数
     - 增加系统虚拟内存
     - 分批处理大文档

7. **模型下载失败**
   - 问题：首次运行时嵌入模型下载失败
   - 解决方案：
     - 检查网络连接
     - 使用代理或镜像源
     - 手动下载模型文件到缓存目录

## 性能优化建议

1. 调整 CHUNK_SIZE 和 CHUNK_OVERLAP 参数以平衡性能和准确性
2. 使用 SSD 存储 ChromaDB 数据
3. 适当增加系统内存，建议至少 16GB
4. 定期清理未使用的向量数据
5. 使用生产环境 WSGI 服务器（如 gunicorn）替代开发服务器

## 安全建议

1. 不要在公共环境暴露 API 密钥
2. 定期备份数据库
3. 限制文件上传大小
4. 使用 HTTPS 进行通信（如需要）
5. 定期更新依赖包版本 