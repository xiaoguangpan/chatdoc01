# 本地智能文档问答助手部署指南

## 1. 系统要求

- Python 3.10 或 3.11（**不支持 3.12 及以上版本**，否则 torch 无法安装）
- Microsoft Word（用于处理加密文档，Windows 必须）
- 操作系统：Windows（如需解析 docx 加密文档）或 Mac/Linux（仅基础功能）
- 内存：建议 16GB 或以上
- 存储：建议 SSD，至少 10GB 可用空间

> **重要提示：**
> 部署前请先运行 `python --version`，确保 Python 版本为 3.10 或 3.11，否则请先更换 Python 版本！

## 2. 环境准备

1. 克隆项目：
```bash
git clone [项目地址]
cd chatdoc01
```

2. 创建并激活虚拟环境（务必用 3.10/3.11）：
```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
``` 