#!/usr/bin/env python3
"""
TalentsAI repository quality checker.

Covers:
1.3 Repo quality: functional subsystems, README/code consistency, commit-message quality.
1.5 Milestone quality: aggregation, requirement verifiability, code coverage, granularity.
Also records the 1.2 admission checks when available.

This script is intentionally dependency-free.
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]

SUBSYSTEMS = {
    "health": {
        "files": ["backend/main.py"],
        "patterns": [r'@app\.get\("/api/health"\)'],
        "readme_terms": ["health", "API"],
    },
    "resume_upload_parse": {
        "files": ["backend/main.py", "backend/resume_parser.py", "backend/models.py"],
        "patterns": [r'@app\.post\("/api/resume/upload"\)', r"def parse_resume", r"ResumeParseResult"],
        "readme_terms": ["PDF", "DOCX", "upload", "Resume"],
    },
    "resume_ai_analysis": {
        "files": ["backend/main.py", "backend/ai_service.py", "backend/models.py"],
        "patterns": [r'@app\.post\("/api/resume/analyze"\)', r"def analyze_resume", r"ats_score"],
        "readme_terms": ["AI", "ATS", "optimization"],
    },
    "interview": {
        "files": ["backend/main.py", "backend/ai_service.py", "backend/models.py"],
        "patterns": [r'@app\.post\("/api/interview/start"\)', r'@app\.post\("/api/interview/answer"\)', r"def generate_interview_questions"],
        "readme_terms": ["interview"],
    },
    "templates": {
        "files": ["backend/main.py", "backend/ai_service.py"],
        "patterns": [r'@app\.post\("/api/resume/template"\)', r"TEMPLATE_PROMPTS"],
        "readme_terms": ["template"],
    },
    "payment": {
        "files": ["backend/main.py", "backend/payment.py", "frontend/templates/pricing.html", "frontend/templates/payment.html"],
        "patterns": [r"payment_router", r'@router\.post\("/create"\)', r'@router\.get\("/query'],
        "readme_terms": [],
    },
}

README_REQUIREMENTS = {
    "project_description": [r"AI-powered", r"JobBoost"],
    "features": [r"## Features", r"Resume", r"interview"],
    "installation": [r"## (Installation|Setup|安装|运行)"],
    "configuration": [r"environment|\.env|DEEPSEEK_API_KEY"],
    "run": [r"python\s+run\.py|uvicorn"],
    "architecture": [r"backend/", r"frontend/"],
    "quality": [r"admission|quality|TalentsAI|质检"],
}

def run_git(*args):
    try:
        p = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, timeout=10)
        if p.returncode == 0:
            return p.stdout.strip()
    except Exception:
        pass
    return None

def get_commits():
    raw = run_git("log", "--pretty=format:%H%x1f%s%x1e", "--reverse")
    if not raw:
        return []
    result=[]
    for row in raw.split("\x1e"):
        row=row.strip()
        if not row: continue
        sha,msg=row.split("\x1f",1)
        result.append({"sha":sha,"message":msg})
    return result

def check_subsystems():
    results={}
    for name, spec in SUBSYSTEMS.items():
        existing=[f for f in spec["files"] if (ROOT/f).exists()]
        blobs=[]
        for f in existing:
            try: blobs.append((ROOT/f).read_text(encoding="utf-8", errors="ignore"))
            except Exception: pass
        blob="\n".join(blobs)
        matched=sum(bool(re.search(p,blob,re.I)) for p in spec["patterns"])
        results[name]={
            "files_present": len(existing)==len(spec["files"]),
            "files": existing,
            "signals_found": matched,
            "signals_expected": len(spec["patterns"]),
            "status": "PASS" if len(existing)==len(spec["files"]) and matched==len(spec["patterns"]) else "WARN",
        }
    return results

def check_readme():
    text=(ROOT/"README.md").read_text(encoding="utf-8",errors="ignore") if (ROOT/"README.md").exists() else ""
    out={}
    for k, pats in README_REQUIREMENTS.items():
        out[k]=all(re.search(p,text,re.I) for p in pats)
    return {"checks":out,"status":"PASS" if all(out.values()) else "WARN"}

def check_commit_quality(commits):
    if not commits:
        return {"status":"UNAVAILABLE","count":0,"good":0,"bad":0,"reasons":["No .git history in uploaded package."]}
    generic=re.compile(r"^(update|fix|changes?|commit|wip|test|temp|final|修改|更新|测试|修复)$",re.I)
    good=[]
    bad=[]
    for c in commits:
        msg=c["message"].strip()
        ok=len(msg)>=12 and not generic.match(msg) and not msg.lower().startswith(("merge ","revert "))
        (good if ok else bad).append({"sha":c["sha"],"message":msg})
    return {"status":"PASS" if not bad else "WARN","count":len(commits),"good":len(good),"bad":len(bad),"bad_commits":bad}

MILESTONES = [
    {"id":"M1","name":"Core resume ingestion","objective":"建立 PDF/DOCX 简历上传、解析与结构化结果返回能力。",
     "files":["backend/main.py","backend/resume_parser.py","backend/models.py"],
     "signals":["/api/resume/upload","parse_resume","ResumeParseResult"]},
    {"id":"M2","name":"AI resume optimization","objective":"建立简历 AI 分析、ATS 评分、关键词缺口和模板格式化能力。",
     "files":["backend/main.py","backend/ai_service.py","backend/models.py"],
     "signals":["/api/resume/analyze","analyze_resume","TEMPLATE_PROMPTS"]},
    {"id":"M3","name":"Interview assistant","objective":"建立基于简历/职位/公司的面试生成、回答评估和会话状态能力。",
     "files":["backend/main.py","backend/ai_service.py","backend/models.py"],
     "signals":["/api/interview/start","/api/interview/answer","generate_interview_questions","evaluate_answer"]},
    {"id":"M4","name":"Monetization and deployment","objective":"建立套餐、学生验证、支付查询及部署配置。",
     "files":["backend/payment.py","run.py","Dockerfile","railway.json","koyeb.yaml"],
     "signals":["/api/payment","student_verifications","ALIPAY","PORT"]},
]

def check_milestones(commits):
    results=[]
    for m in MILESTONES:
        exists=[f for f in m["files"] if (ROOT/f).exists()]
        blob=""
        for f in exists:
            blob += "\n" + (ROOT/f).read_text(encoding="utf-8",errors="ignore")
        found=[s for s in m["signals"] if s.lower() in blob.lower()]
        coverage=len(exists)/len(m["files"]) if m["files"] else 1
        verifiable=len(found)/len(m["signals"]) if m["signals"] else 1
        results.append({
            **m,
            "file_coverage": round(coverage,2),
            "requirement_signal_coverage": round(verifiable,2),
            "commit_range": None,
            "status":"PASS" if coverage==1 and verifiable==1 else "WARN",
        })
    # If history exists, assign chronological contiguous ranges by milestone keyword matches.
    # We do not invent SHAs when history is absent.
    if commits:
        for i,m in enumerate(results):
            keywords={
                "M1":["resume","upload","parse","pdf","docx"],
                "M2":["ai","resume","analysis","ats","template","optimiz"],
                "M3":["interview","question","answer"],
                "M4":["payment","alipay","deploy","railway","koyeb"],
            }[m["id"]]
            hits=[idx for idx,c in enumerate(commits) if any(k in c["message"].lower() for k in keywords)]
            if hits:
                lo,hi=min(hits),max(hits)
                m["commit_range"]={"start":commits[lo]["sha"],"end":commits[hi]["sha"],
                                   "start_message":commits[lo]["message"],"end_message":commits[hi]["message"]}
            else:
                m["commit_range"]={"status":"not-inferred","reason":"No sufficiently specific commit subject matched milestone keywords."}
    return results

def check_milestone_quality(milestones):
    # aggregation: every milestone has a distinct objective and >=2 files/signals
    aggregation=all(len(m["files"])>=2 and len(m["objective"])>=12 for m in milestones)
    verifiable=all(m["requirement_signal_coverage"]>=0.75 for m in milestones)
    coverage=all(m["file_coverage"]>=0.75 for m in milestones)
    granularity=all(2 <= len(m["files"]) <= 6 for m in milestones)
    status="PASS" if all([aggregation,verifiable,coverage,granularity]) else "WARN"
    return {"aggregation":aggregation,"requirement_verifiability":verifiable,"code_coverage":coverage,
            "split_granularity":granularity,"status":status}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--json",action="store_true")
    args=ap.parse_args()
    commits=get_commits()
    subs=check_subsystems()
    readme=check_readme()
    commitq=check_commit_quality(commits)
    milestones=check_milestones(commits)
    msq=check_milestone_quality(milestones)
    result={
        "generated_at":datetime.now(timezone.utc).isoformat(),
        "repo":str(ROOT.name),
        "git_history_available":bool(commits),
        "stage_13":{"functional_subsystems":subs,"readme_code_consistency":readme,"commit_message_quality":commitq},
        "stage_15":{"milestones":milestones,"quality":msq},
    }
    if args.json:
        print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        print("=== TalentsAI Repo Quality Check ===")
        print("1.3 Functional subsystems:", "PASS" if all(x["status"]=="PASS" for x in subs.values()) else "WARN")
        print("1.3 README/code consistency:", readme["status"])
        print("1.3 Commit message quality:", commitq["status"], f"({commitq['count']} commits)")
        print("1.5 Milestone quality:", msq["status"])
        for m in milestones:
            print(f"  {m['id']} {m['name']}: {m['status']} | file={m['file_coverage']:.0%} signal={m['requirement_signal_coverage']:.0%}")
        if not commits:
            print("NOTE: .git history is absent; exact commit ranges cannot be reconstructed from this ZIP.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
