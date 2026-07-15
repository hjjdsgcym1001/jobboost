"""
JobBoost - AI Resume Optimizer & Interview Assistant
entry point
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    print(f"Starting JobBoost on port {port}")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=False)