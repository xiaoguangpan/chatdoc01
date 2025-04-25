# 本地智能文档问答助手

一个基于本地部署的智能文档问答助手，用于帮助内部员工快速分析和解读公司内部的技术协议Word文档。

## 功能特点

- 本地运行，数据安全
- 基于项目号管理文档
- 支持文档版本控制
- 支持加密Word文档处理
- 本地向量化存储
- 智能问答功能
- 精确的来源引用和定位

## 系统要求

- Python 3.9+
- Microsoft Word (用于处理Word文档)
- 火山方舟API Key

## 安装步骤

1. 克隆项目：

```bash
git clone [项目地址]
cd chatdoc01
```

2. 创建虚拟环境：

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

4. 配置API Key：

首次运行时，系统会提示您输入火山方舟API Key。

## 运行应用

1. 启动应用：

```bash
python -m app.main
```

2. 在浏览器中访问：

```
http://127.0.0.1:8000
```

## 使用说明

1. 首次运行时，需要配置火山方舟API Key。
2. 创建项目并上传Word文档。
3. 等待文档处理完成。
4. 选择文档版本开始问答。
5. 点击答案中的来源引用可以定位到原文。

## 目录结构

```
chatdoc01/
├── app/
│   ├── api/
│   │   └── routes.py
│   ├── models/
│   │   ├── database.py
│   │   └── database_manager.py
│   ├── services/
│   │   ├── word_processor.py
│   │   ├── document_processor.py
│   │   └── llm_service.py
│   ├── static/
│   │   └── js/
│   │       ├── api.js
│   │       ├── ui.js
│   │       └── main.js
│   ├── templates/
│   │   └── index.html
│   ├── config.py
│   └── main.py
├── db/
│   ├── chroma_db/
│   └── app_data.db
├── docs_storage/
├── requirements.txt
└── README.md
```

## 注意事项

- 确保本地安装了Microsoft Word并能正常运行。
- 文档处理可能需要一定时间，请耐心等待。
- 建议定期备份数据库和文档存储目录。

## 技术栈

- 后端：FastAPI, SQLAlchemy, LlamaIndex, ChromaDB
- 前端：HTML, Tailwind CSS, Vanilla JavaScript
- 数据库：SQLite, ChromaDB
- 文档处理：pywin32
- LLM：火山方舟API 