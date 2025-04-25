from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import json
import os
from datetime import datetime

from app.models.database import Project, Document, DocumentVersion, ChatSession, Message, Setting
from app.models.database_manager import get_db
from app.services.word_processor import WordProcessor
from app.services.document_processor import DocumentProcessor
from app.services.llm_service import LLMService
from app.config import DOCS_STORAGE_PATH

router = APIRouter()

# 项目相关路由
@router.post("/projects/")
async def create_project(
    project_id: str,
    project_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """创建新项目"""
    project = Project(
        project_id=project_id,
        project_name=project_name
    )
    db.add(project)
    try:
        await db.commit()
        return {"message": "项目创建成功", "project_id": project_id}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/projects/")
async def list_projects(db: AsyncSession = Depends(get_db)):
    """获取项目列表"""
    result = await db.execute(
        "SELECT * FROM projects ORDER BY creation_time DESC"
    )
    projects = result.fetchall()
    return {"projects": projects}

# 文档相关路由
@router.post("/documents/upload/")
async def upload_document(
    background_tasks: BackgroundTasks,
    project_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """上传文档"""
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="只支持.docx格式文件")
        
    # 检查项目是否存在
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
        
    # 检查是否是新文档或新版本
    result = await db.execute(
        "SELECT * FROM documents WHERE project_id = :project_id AND original_filename = :filename",
        {"project_id": project_id, "filename": file.filename}
    )
    existing_doc = result.first()
    
    if existing_doc:
        # 新版本
        doc_base_id = existing_doc.doc_base_id
        result = await db.execute(
            "SELECT MAX(version_number) FROM document_versions WHERE doc_base_id = :doc_base_id",
            {"doc_base_id": doc_base_id}
        )
        max_version = result.scalar() or 0
        version_number = max_version + 1
        
        # 更新之前版本的is_latest状态
        await db.execute(
            "UPDATE document_versions SET is_latest = FALSE WHERE doc_base_id = :doc_base_id",
            {"doc_base_id": doc_base_id}
        )
    else:
        # 新文档
        doc = Document(
            project_id=project_id,
            original_filename=file.filename
        )
        db.add(doc)
        await db.flush()
        doc_base_id = doc.doc_base_id
        version_number = 1
        
    # 保存文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stored_filename = f"{doc_base_id}_v{version_number}_{timestamp}.docx"
    stored_filepath = os.path.join(DOCS_STORAGE_PATH, stored_filename)
    
    with open(stored_filepath, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    # 创建版本记录
    version = DocumentVersion(
        doc_base_id=doc_base_id,
        version_number=version_number,
        stored_filename=stored_filename,
        stored_filepath=stored_filepath,
        status="processing",
        is_latest=True
    )
    db.add(version)
    await db.flush()
    version_id = version.version_id
    
    # 在后台处理文档
    background_tasks.add_task(
        process_document_background,
        stored_filepath,
        version_id,
        doc_base_id,
        project_id
    )
    
    await db.commit()
    
    return {
        "message": "文档上传成功，正在处理",
        "version_id": version_id,
        "version_number": version_number
    }

@router.get("/documents/{project_id}")
async def list_documents(project_id: str, db: AsyncSession = Depends(get_db)):
    """获取项目下的文档列表"""
    result = await db.execute(
        """
        SELECT d.*, v.version_number, v.status, v.is_latest, v.version_id
        FROM documents d
        LEFT JOIN document_versions v ON d.doc_base_id = v.doc_base_id
        WHERE d.project_id = :project_id AND (v.is_latest = TRUE OR v.is_latest IS NULL)
        ORDER BY d.creation_time DESC
        """,
        {"project_id": project_id}
    )
    documents = result.fetchall()
    return {"documents": documents}

@router.get("/documents/{doc_base_id}/versions")
async def list_versions(doc_base_id: int, db: AsyncSession = Depends(get_db)):
    """获取文档的版本列表"""
    result = await db.execute(
        """
        SELECT *
        FROM document_versions
        WHERE doc_base_id = :doc_base_id AND is_deleted = FALSE
        ORDER BY version_number DESC
        """,
        {"doc_base_id": doc_base_id}
    )
    versions = result.fetchall()
    return {"versions": versions}

@router.delete("/versions/{version_id}")
async def soft_delete_version(version_id: int, db: AsyncSession = Depends(get_db)):
    """软删除文档版本"""
    version = await db.get(DocumentVersion, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")
        
    if version.is_latest:
        raise HTTPException(status_code=400, detail="不能删除最新版本")
        
    version.is_deleted = True
    await db.commit()
    return {"message": "版本已删除"}

# 问答相关路由
@router.post("/chat/sessions/")
async def create_chat_session(version_id: int, db: AsyncSession = Depends(get_db)):
    """创建新的聊天会话"""
    version = await db.get(DocumentVersion, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="文档版本不存在")
        
    session = ChatSession(version_id=version_id)
    db.add(session)
    await db.commit()
    return {"session_id": session.session_id}

@router.post("/chat/{session_id}/messages")
async def send_message(
    session_id: int,
    query: str,
    db: AsyncSession = Depends(get_db)
):
    """发送问题并获取回答"""
    session = await db.get(ChatSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
        
    # 保存用户问题
    user_message = Message(
        session_id=session_id,
        sender="user",
        text=query
    )
    db.add(user_message)
    await db.flush()
    
    # 获取API Key
    result = await db.execute(
        "SELECT value FROM settings WHERE key = 'llm_api_key'"
    )
    api_key = result.scalar()
    if not api_key:
        raise HTTPException(status_code=400, detail="未配置API Key")
        
    # 初始化服务
    doc_processor = DocumentProcessor()
    llm_service = LLMService(api_key)
    
    # 检索相关内容
    relevant_blocks = doc_processor.query_document(
        query_text=query,
        version_id=session.version_id
    )
    
    # 生成回答
    response = llm_service.generate_response(query, relevant_blocks)
    if response['error']:
        raise HTTPException(status_code=500, detail=response['error'])
        
    # 提取引用的块ID
    html_ids = [block['metadata']['html_id'] for block in relevant_blocks]
    
    # 保存系统回答
    system_message = Message(
        session_id=session_id,
        sender="system",
        text=response['answer'],
        retrieved_chunk_html_ids=json.dumps(html_ids)
    )
    db.add(system_message)
    await db.commit()
    
    return {
        "answer": response['answer'],
        "sources": html_ids
    }

@router.get("/chat/{session_id}/messages")
async def get_chat_history(session_id: int, db: AsyncSession = Depends(get_db)):
    """获取聊天历史记录"""
    result = await db.execute(
        "SELECT * FROM messages WHERE session_id = :session_id ORDER BY timestamp",
        {"session_id": session_id}
    )
    messages = result.fetchall()
    return {"messages": messages}

# 设置相关路由
@router.post("/settings/api-key")
async def update_api_key(api_key: str, db: AsyncSession = Depends(get_db)):
    """更新API Key"""
    setting = Setting(key="llm_api_key", value=api_key)
    db.merge(setting)
    await db.commit()
    return {"message": "API Key已更新"}

@router.get("/settings/api-key")
async def get_api_key(db: AsyncSession = Depends(get_db)):
    """获取API Key"""
    result = await db.execute(
        "SELECT value FROM settings WHERE key = 'llm_api_key'"
    )
    api_key = result.scalar()
    return {"api_key": api_key}

# 后台任务
async def process_document_background(
    file_path: str,
    version_id: int,
    doc_base_id: int,
    project_id: str
):
    """后台处理文档"""
    try:
        # 初始化处理器
        word_processor = WordProcessor()
        doc_processor = DocumentProcessor()
        
        # 提取文档内容
        with word_processor as wp:
            content_blocks = wp.extract_content(file_path)
            
        # 处理文档内容
        processed_blocks = doc_processor.process_document(
            content_blocks,
            version_id,
            doc_base_id,
            project_id
        )
        
        # 更新处理状态
        async with AsyncSession() as db:
            version = await db.get(DocumentVersion, version_id)
            version.status = "ready"
            await db.commit()
            
    except Exception as e:
        # 更新错误状态
        async with AsyncSession() as db:
            version = await db.get(DocumentVersion, version_id)
            version.status = "error"
            version.error_message = str(e)
            await db.commit() 