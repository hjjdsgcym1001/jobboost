"""
JobBoost - AI Resume Optimizer & Interview Assistant
启动入口
"""
import os
import sys

# Add project root to Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    print(f"╔══════════════════════════════════════════╗")
    print(f"║        JobBoost - AI Resume Optimizer    ║")
    print(f"║                                          ║")
    print(f"║  🌐  http://localhost:{port}                 ║")
    print(f"║  📄  API: http://localhost:{port}/api/health ║")
    print(f"║                                          ║")
    print(f"║  🎯 Demo Mode: 无需 API Key 即可体验      ║")
    print(f"║  ⚡ 配置 API Key 后启用真实 AI 分析       ║")
    print(f"║  📖 查看 backend/.env.example 获取配置    ║")
    print(f"╚══════════════════════════════════════════╝")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=False)
