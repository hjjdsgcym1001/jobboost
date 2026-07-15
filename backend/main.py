"""
JobBoost Backend - FastAPI Application
AI Resume Optimizer + Interview Assistant
"""

import os
import json
import uuid
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env file
load_dotenv()

from .models import ResumeAnalysisRequest, InterviewFeedback, InterviewQuestion
from .resume_parser import parse_resume
from .ai_service import AIService
from .payment import router as payment_router

# ─── Logging ───
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jobboost")

# ─── App Setup ───
app = FastAPI(title="JobBoost API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Config ───
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "5242880"))  # 5MB default

# ─── Services ───
ai_service = AIService()

# In-memory interview sessions
interview_sessions: dict = {}


# ─── Routes: Health ───

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "JobBoost", "version": "1.0.0"}


# ─── Routes: Resume Upload & Analysis ───

@app.post("/api/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
):
    """上传简历文件"""
    # Validate file type
    allowed_extensions = {".pdf", ".docx"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="仅支持 PDF 和 DOCX 格式")

    # Validate file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件过大，最大支持 5MB")

    # Save file
    file_id = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{file_id}{file_ext}"
    with open(save_path, "wb") as f:
        f.write(content)

    # Parse resume
    try:
        result = parse_resume(str(save_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"简历解析失败：{str(e)}")

    return {
        "file_id": file_id,
        "filename": file.filename,
        "raw_text": result.raw_text,
        "sections": [s.model_dump() for s in result.sections],
        "word_count": result.word_count,
    }


@app.post("/api/resume/analyze")
async def analyze_resume(request: ResumeAnalysisRequest):
    """分析简历并返回优化建议"""
    try:
        result = ai_service.analyze_resume(
            resume_text=request.resume_text,
            job_description=request.job_description or "",
            target_position=request.target_position or "",
            language=request.language or "中文",
        )
        return result
    except Exception as e:
        logger.exception("Resume analysis failed")
        raise HTTPException(status_code=500, detail=f"分析失败：{str(e)}")


# ─── Routes: Interview ───

@app.post("/api/interview/start")
async def start_interview(
    company: str = Form(""),
    resume_text: str = Form(...),
    position: str = Form(""),
    count: int = Form(5),
):
    """开始面试模拟，生成定制面试题"""
    try:
        questions = ai_service.generate_interview_questions(
            resume_text=resume_text,
            position=position,
            company=company,
            count=count,
        )

        session_id = str(uuid.uuid4())
        interview_sessions[session_id] = {
            "session_id": session_id,
            "resume_text": resume_text,
            "position": position,
            "questions": questions,
            "history": [],
            "started_at": datetime.utcnow().isoformat(),
            "current_index": 0,
        }

        return {
            "session_id": session_id,
            "question": questions[0] if questions else None,
            "total_questions": len(questions),
            "current_index": 0,
        }
    except Exception as e:
        logger.exception("Failed to start interview")
        raise HTTPException(status_code=500, detail=f"启动面试失败：{str(e)}")


@app.post("/api/interview/answer")
async def submit_answer(
    session_id: str = Form(...),
    question_id: int = Form(...),
    answer: str = Form(...),
):
    """提交面试回答并获取反馈"""
    session = interview_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="面试会话不存在或已过期")

    # Find the question
    current_q = None
    for q in session["questions"]:
        if q.get("id") == question_id:
            current_q = q
            break

    if not current_q:
        raise HTTPException(status_code=404, detail="题目不存在")

    # Get AI feedback
    feedback = ai_service.evaluate_answer(
        question=current_q["question"],
        user_answer=answer,
        resume_text=session["resume_text"],
    )

    # Save to history
    session["history"].append({
        "question": current_q,
        "answer": answer,
        "feedback": feedback,
        "timestamp": datetime.utcnow().isoformat(),
    })

    # Get next question
    current_index = session["current_index"] + 1
    next_q = None
    if current_index < len(session["questions"]):
        next_q = session["questions"][current_index]

    session["current_index"] = current_index

    return {
        "feedback": feedback,
        "next_question": next_q,
        "current_index": current_index,
        "total_questions": len(session["questions"]),
        "is_complete": next_q is None,
    }


@app.get("/api/interview/session/{session_id}")
async def get_session(session_id: str):
    """获取面试会话状态"""
    session = interview_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {
        "session_id": session["session_id"],
        "position": session["position"],
        "history": session["history"],
        "current_index": session["current_index"],
        "total_questions": len(session["questions"]),
        "is_complete": session["current_index"] >= len(session["questions"]),
    }


# ─── Routes: Pages (for non-SPA clients) ───

from jinja2 import Environment, FileSystemLoader

templates_env = Environment(loader=FileSystemLoader(str(BASE_DIR / "frontend" / "templates")))

def render(template_name: str, **kwargs) -> HTMLResponse:
    template = templates_env.get_template(template_name)
    return HTMLResponse(content=template.render(**kwargs))


@app.get("/", response_class=HTMLResponse)
async def index_page():
    return render("index.html")

@app.get("/result", response_class=HTMLResponse)
async def result_page():
    return render("result.html")

@app.get("/templates", response_class=HTMLResponse)
async def templates_page():
    return render("templates.html")

@app.get("/interview", response_class=HTMLResponse)
async def interview_page():
    return render("interview.html")


@app.get("/payment", response_class=HTMLResponse)
async def payment_page():
    return render("payment.html")
@app.get("/pricing", response_class=HTMLResponse)
async def pricing_page():
    return render("pricing.html")


# ─── Static Files ───
static_dir = BASE_DIR / "frontend" / "static"
if static_dir.exists():
    app.include_router(payment_router)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ─── Run ───
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
