"""
简历解析模块 - 支持 PDF 和 DOCX 格式
"""

import os
import re
from pathlib import Path
from typing import Optional

from .models import ResumeParseResult, ResumeSection


def extract_text_from_pdf(file_path: str) -> str:
    """从 PDF 文件中提取文本"""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        text_parts = []
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                text_parts.append(text)
        doc.close()
        return "\n".join(text_parts)
    except ImportError:
        raise ImportError("PyMuPDF (fitz) is required for PDF parsing")
    except Exception as e:
        raise RuntimeError(f"Failed to parse PDF: {e}")


def extract_text_from_docx(file_path: str) -> str:
    """从 DOCX 文件中提取文本"""
    try:
        from docx import Document
        doc = Document(file_path)
        text_parts = []
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text.strip())
        return "\n".join(text_parts)
    except ImportError:
        raise ImportError("python-docx is required for DOCX parsing")
    except Exception as e:
        raise RuntimeError(f"Failed to parse DOCX: {e}")


def parse_sections(text: str) -> list[ResumeSection]:
    """将简历文本按常见段落划分"""
    section_keywords = {
        "personal_info": r"(个人信息|联系方式|个人概况|基本信息|关于我)",
        "summary": r"(个人总结|自我评价|职业概述|专业概要|个人简介|职业简介|profile|summary)",
        "experience": r"(工作经历|工作经验|职业经历|项目经历|实习经历|工作经验|work experience|employment|experience)",
        "education": r"(教育背景|教育经历|学历|学校|教育|education)",
        "skills": r"(技能|专业技能|技术能力|核心能力|技能特长|skills|technical skills)",
        "projects": r"(项目经验|项目经历|项目|projects|portfolio)",
        "certifications": r"(证书|认证|资格|资质|certifications)",
        "languages": r"(语言能力|语言|languages)",
    }

    sections = []
    lines = text.split("\n")
    current_section = None
    current_content = []
    section_order = 0

    # Try to identify sections by keywords
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            if current_content:
                current_content.append("")
            continue

        found_section = None
        for section_type, pattern in section_keywords.items():
            if re.search(pattern, line_stripped, re.IGNORECASE):
                found_section = section_type
                break

        if found_section:
            # Save previous section
            if current_section and current_content:
                sections.append(ResumeSection(
                    section_type=current_section,
                    content="\n".join(current_content).strip(),
                    order=section_order,
                ))
                section_order += 1
            current_section = found_section
            current_content = [line_stripped]
        else:
            if current_content:
                current_content.append(line_stripped)

    # Save last section
    if current_section and current_content:
        sections.append(ResumeSection(
            section_type=current_section,
            content="\n".join(current_content).strip(),
            order=section_order,
        ))

    return sections


def parse_resume(file_path: str) -> ResumeParseResult:
    """
    解析简历文件并返回结构化结果
    自动检测文件类型（pdf/docx）
    """
    file_path = str(file_path)
    file_ext = Path(file_path).suffix.lower()

    if file_ext == ".pdf":
        raw_text = extract_text_from_pdf(file_path)
        file_type = "pdf"
    elif file_ext == ".docx":
        raw_text = extract_text_from_docx(file_path)
        file_type = "docx"
    else:
        raise ValueError(f"Unsupported file type: {file_ext}. Only PDF and DOCX are supported.")

    sections = parse_sections(raw_text)
    word_count = len(raw_text.replace("\n", " ").split())

    from datetime import datetime
    return ResumeParseResult(
        raw_text=raw_text,
        sections=sections,
        file_type=file_type,
        word_count=word_count,
        parsed_at=datetime.utcnow().isoformat(),
    )
