---
title: JobBoostemoji: 🚀colorFrom: bluecolorTo: purplesdk: dockerpinned: falseapp_port: 7860
JobBoost - AI Resume Optimizer
AI-powered resume optimization and interview preparation tool.
Features
 Resume upload & analysis (PDF/DOCX)
 AI-powered optimization suggestions
 ATS compatibility scoring
 Company-specific interview simulations
 Resume templates for fresh graduates

Repository structure
 `backend/main.py` — FastAPI routes and page entry points
 `backend/resume_parser.py` — PDF/DOCX extraction and resume section parsing
 `backend/ai_service.py` — LLM providers, resume analysis, interview generation and template formatting
 `backend/payment.py` — student verification and Alipay payment APIs
 `frontend/templates/` — HTML pages
 `run.py` — local/deployment startup entry point
 `scripts/` — TalentsAI admission and repository quality checks
 `docs/` — milestone, TODO and execution-record documentation
Installation & setup
Install dependencies and configure environment variables.
Configuration
Copy `.env.example` to `.env` and configure the AI provider. The default example uses DeepSeek:
```envDEEPSEEK_API_KEY=your-keyAI_PROVIDER=deepseekDEEPSEEK_MODEL=deepseek-chat```
For Alipay deployment, configure the required payment key environment variables described in the deployment configuration. Do not commit private keys.
Run locally
```bashpip install -r backend/requirements.txtpython run.py```
The service listens on `PORT` when provided, otherwise port `8000`.
API entry points
 `GET /api/health`
 `POST /api/resume/upload`
 `POST /api/resume/analyze`
 `POST /api/resume/template`
 `POST /api/interview/start`
 `POST /api/interview/answer`
 `GET /api/interview/session/{session_id}`
 `/api/payment/*`
TalentsAI quality checks
Run:
```bashpython scripts/admission_check.pypython scripts/repo_quality_check.pypython scripts/repo_quality_check.py --json```
The quality checker covers functional subsystem evidence, README/code consistency, commit-message quality, milestone coverage and milestone granularity.
See:
 `docs/MILESTONES.md`
 `docs/NEXT_TODO.md`
 `docs/EXECUTION_RECORD.md`
> Note: a ZIP snapshot does not contain Git history. Exact commit ranges are therefore only populated when the checker runs inside the original Git repository.
