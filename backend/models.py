from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ResumeSection(BaseModel):
    """简历中的单个段落"""
    section_type: str  # personal_info, experience, education, skills, projects, summary
    content: str
    order: int = 0

class ResumeParseResult(BaseModel):
    """简历解析结果"""
    raw_text: str
    sections: List[ResumeSection] = []
    file_type: str = "pdf"  # pdf or docx
    word_count: int = 0
    parsed_at: str = ""

class ResumeAnalysisRequest(BaseModel):
    """简历分析请求"""
    resume_text: str
    job_description: Optional[str] = None
    target_position: Optional[str] = None
    language: Optional[str] = "中文"

class ResumeAnalysisResult(BaseModel):
    """简历分析结果"""
    summary: str = ""
    strengths: List[str] = []
    weaknesses: List[str] = []
    suggestions: List[dict] = []  # each: {"section": "...", "original": "...", "suggested": "...", "reason": "..."}
    ats_score: int = 0  # 0-100
    keyword_gaps: List[str] = []
    overall_score: int = 0
    optimized_version: str = ""

class InterviewQuestion(BaseModel):
    """面试题"""
    id: int = 0
    question: str
    category: str = ""  # technical, behavioral, general
    difficulty: str = ""  # easy, medium, hard
    sample_answer: str = ""

class InterviewFeedback(BaseModel):
    """面试回答反馈"""
    question: str
    user_answer: str
    score: int = 0  # 0-100
    feedback: str = ""
    improvements: List[str] = []
    sample_answer: str = ""

class InterviewSession(BaseModel):
    """面试模拟会话"""
    session_id: str = ""
    resume_text: str = ""
    position: str = ""
    questions: List[InterviewQuestion] = []
    history: List[dict] = []  # QA pairs
    started_at: str = ""
    current_index: int = 0
