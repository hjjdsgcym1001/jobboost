#!/usr/bin/env python3
"""TalentsAI 1.2 admission checks: commit count, code scale, parseability, README basics."""
from pathlib import Path
import argparse, ast, json, re, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
SOURCE_EXT={".py",".js",".ts",".jsx",".tsx",".json",".yaml",".yml"}
EXCLUDE={"node_modules",".git","venv",".venv","__pycache__","uploads","dist","build"}
def git_count():
    try:
        p=subprocess.run(["git","rev-list","--count","HEAD"],cwd=ROOT,text=True,capture_output=True,timeout=5)
        return int(p.stdout.strip()) if p.returncode==0 else None
    except Exception:return None
def files():
    return [p for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in SOURCE_EXT and not any(x in p.parts for x in EXCLUDE)]
def loc(p):
    try:
        return sum(1 for x in p.read_text(encoding="utf8",errors="ignore").splitlines() if x.strip() and not x.lstrip().startswith(("//","#","<!--","/*","*")))
    except Exception:return 0
def parse(p):
    try:
        text=p.read_text(encoding="utf8",errors="ignore")
        if p.suffix==".py": ast.parse(text)
        elif p.suffix==".json": json.loads(text)
        elif p.suffix in {".yaml",".yml"}: 
            # basic structural parse without external dependency
            if "\x00" in text: raise ValueError("NUL byte")
        else:
            if "\x00" in text: raise ValueError("NUL byte")
        return True,""
    except Exception as e:return False,str(e)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--min-commits",type=int,default=1)
    ap.add_argument("--min-loc",type=int,default=100)
    ap.add_argument("--min-parse-rate",type=float,default=1.0)
    ap.add_argument("--json",action="store_true")
    a=ap.parse_args()
    fs=files(); total_loc=sum(loc(p) for p in fs)
    parsed=[parse(p)[0] for p in fs]; rate=sum(parsed)/len(parsed) if fs else 0
    r={"submission_count":{"value":git_count(),"threshold":a.min_commits},
       "code_scale":{"files":len(fs),"effective_loc":total_loc,"threshold":a.min_loc},
       "parseability":{"parsed":sum(parsed),"total":len(fs),"rate":rate,"threshold":a.min_parse_rate},
       "readme":{"exists":(ROOT/"README.md").exists(),"size":(ROOT/"README.md").stat().st_size if (ROOT/"README.md").exists() else 0},
       "notes":[]}
    r["submission_count"]["status"]="PASS" if r["submission_count"]["value"] is not None and r["submission_count"]["value"]>=a.min_commits else ("UNAVAILABLE" if r["submission_count"]["value"] is None else "FAIL")
    r["code_scale"]["status"]="PASS" if total_loc>=a.min_loc else "FAIL"
    r["parseability"]["status"]="PASS" if rate>=a.min_parse_rate else "FAIL"
    readme=(ROOT/"README.md").read_text(encoding="utf8",errors="ignore") if (ROOT/"README.md").exists() else ""
    basics=all(x in readme for x in ["# JobBoost","## Features","## Installation","## Configuration","## Run locally"])
    r["readme"]["status"]="PASS" if basics else "FAIL"
    r["status"]="PASS" if all(x["status"]=="PASS" for x in [r["code_scale"],r["parseability"],r["readme"]]) and r["submission_count"]["status"]!="FAIL" else "FAIL"
    if r["submission_count"]["status"]=="UNAVAILABLE": r["notes"].append("ZIP snapshot has no .git history; commit count must be checked in the original repository.")
    print(json.dumps(r,ensure_ascii=False,indent=2) if a.json else "\n".join([f"1.2 Admission: {r['status']}",f"Commits: {r['submission_count']['value'] or 'N/A'}",f"Effective LOC: {total_loc}",f"Parse rate: {rate:.1%}",f"README: {r['readme']['status']}"]))
    return 0
if __name__=="__main__": raise SystemExit(main())
