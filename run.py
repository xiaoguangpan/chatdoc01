import sys
import uvicorn
import webbrowser
import os
from threading import Timer

# Python 版本校验
if not (sys.version_info.major == 3 and sys.version_info.minor in (10, 11)):
    print("\033[91m[错误] 仅支持 Python 3.10 或 3.11，当前版本：{}\033[0m".format(sys.version))
    sys.exit(1)

def open_browser():
    webbrowser.open('http://127.0.0.1:8000')

if __name__ == "__main__":
    # 确保必要的目录存在
    os.makedirs('db/chroma_db', exist_ok=True)
    os.makedirs('docs_storage', exist_ok=True)
    
    # 3秒后自动打开浏览器
    Timer(3, open_browser).start()
    
    # 启动应用
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True) 