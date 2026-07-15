"""
AI 服务模块 - 调用 OpenAI / Claude / DeepSeek API
"""

import os
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AIService:
    """统一的 AI 服务封装，支持 OpenAI / Anthropic / DeepSeek"""

    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "openai").lower()
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.claude_model = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
        self.deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

        self.openai_client = None
        self.anthropic_client = None
        self.deepseek_client = None

        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "anthropic":
            self._init_anthropic()
        elif self.provider == "deepseek":
            self._init_deepseek()

    def _init_openai(self):
        try:
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and api_key != "sk-your-openai-api-key-here":
                self.openai_client = OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized")
            else:
                logger.warning("OpenAI API key not configured")
        except ImportError:
            logger.warning("openai package not installed")

    def _init_anthropic(self):
        try:
            from anthropic import Anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key and api_key != "sk-ant-your-anthropic-api-key-here":
                self.anthropic_client = Anthropic(api_key=api_key)
                logger.info("Anthropic client initialized")
            else:
                logger.warning("Anthropic API key not configured")
        except ImportError:
            logger.warning("anthropic package not installed")

    def _init_deepseek(self):
        """DeepSeek API 兼容 OpenAI SDK, 仅需修改 base_url"""
        try:
            from openai import OpenAI
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if api_key and api_key != "sk-your-deepseek-api-key-here":
                self.deepseek_client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.deepseek.com"
                )
                logger.info("DeepSeek client initialized")
            else:
                logger.warning("DeepSeek API key not configured")
        except ImportError:
            logger.warning("openai package not installed (required for DeepSeek)")

    def _call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """调用 LLM 并返回文本响应"""
        if self.provider == "deepseek" and self.deepseek_client:
            return self._call_deepseek(system_prompt, user_prompt, temperature)
        elif self.provider == "openai" and self.openai_client:
            return self._call_openai(system_prompt, user_prompt, temperature)
        elif self.provider == "anthropic" and self.anthropic_client:
            return self._call_anthropic(system_prompt, user_prompt, temperature)
        else:
            return self._mock_response(user_prompt)

    def _call_openai(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        response = self.openai_client.chat.completions.create(
            model=self.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content

    def _call_anthropic(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        response = self.anthropic_client.messages.create(
            model=self.claude_model,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=temperature,
            max_tokens=4096,
        )
        return response.content[0].text

    def _call_deepseek(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """调用 DeepSeek API (兼容 OpenAI 协议)"""
        response = self.deepseek_client.chat.completions.create(
            model=self.deepseek_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=4096,
        )
        return response.choices[0].message.content

    def _mock_response(self, user_prompt: str) -> str:
        """无 API Key 时的演示模式，返回示例数据"""
        return json.dumps({
            "summary": "该简历展示了候选人扎实的技术背景和丰富的项目经验。",
            "strengths": ["清晰的技术技能栈", "量化的工作成果", "良好的教育背景"],
            "weaknesses": ["缺少领导力相关的描述", "工作经历时间线有空白期"],
            "suggestions": [
                {
                    "section": "工作经验",
                    "original": "参与项目开发",
                    "suggested": "独立负责项目核心模块的架构设计与开发，主导团队技术方案评审",
                    "reason": "体现主动性和领导力"
                }
            ],
            "ats_score": 72,
            "keyword_gaps": ["项目管理", "团队协作"],
            "overall_score": 75,
            "optimized_version": "# 优化版简历\n\n## 个人总结\n具有丰富经验的软件工程师...\n"
        }, ensure_ascii=False)

    # ──────────────── Resume Analysis ────────────────

    def analyze_resume(self, resume_text: str, job_description: str = "", target_position: str = "", language: str = "中文") -> dict:
        """分析简历并提供优化建议"""
        system_prompt = f"""你是一名资深简历优化专家和HR顾问。你的任务是分析候选人简历，提供具体、可操作的优化建议。

分析时注意：
1. 找出简历的核心优势和亮点
2. 发现简历中的薄弱环节和潜在问题
3. 针对每个问题给出具体的修改建议
4. 评估ATS（招聘管理系统）匹配度
5. 分析简历中缺失的关键词

请用{language}输出，格式为JSON：{{
    "summary": "一句话总结",
    "strengths": ["优势1", "优势2"],
    "weaknesses": ["不足1", "不足2"],
    "suggestions": [{{"section": "段落名", "original": "原文", "suggested": "修改建议", "reason": "理由"}}],
    "ats_score": 0-100,
    "keyword_gaps": ["缺失的关键词"],
    "overall_score": 0-100,
    "optimized_version": "优化后的完整简历文本"
}}"""

        user_prompt = f"请分析以下简历：\n\n{resume_text}\n"
        if job_description:
            user_prompt += f"\n目标岗位描述：\n{job_description}\n"
        if target_position:
            user_prompt += f"\n目标职位：{target_position}\n"

        result = self._call_llm(system_prompt, user_prompt, temperature=0.3)
        return self._parse_json_result(result)

    # ──────────────── Interview Questions ────────────────

    def generate_interview_questions(self, resume_text: str, position: str = '', company: str = '', count: int = 5) -> list[dict]:
        """根据简历生成定制面试题"""
        system_prompt = f"""你是一名资深面试官。根据候选人简历生成针对性的{count}道面试题。

要求：
1. 问题要结合简历中的具体经历和技能
2. 包含技术问题和行为问题
3. 不同难度级别各2题
4. 每题提供参考答案要点
5. 问题应该能考察候选人的真实水平

请用JSON格式输出：{{
    "questions": [
        {{"id": 1, "question": "问题", "category": "technical/behavioral/general", "difficulty": "easy/medium/hard", "sample_answer": "参考答案"}}
    ]
}}"""

        user_prompt = f"简历：\n{resume_text}\n"
        if position:
            user_prompt += f"\n目标职位：{position}\n"
        if company:
            user_prompt += f"\n目标公司：{company}\n"
            system_prompt += f"\n\n请针对{company}的面试风格和常见考题进行出题，包括该公司的常见面试题类型（如项目深挖、算法题、行为面试等）。如果该公司有特定技术栈或业务方向，优先出题考察相关能力。"
            if company in ('字节跳动', '腾讯', '阿里巴巴', '百度', '美团', '京东'):
                system_prompt += ' 建议包含至少2道该公司历年高频面试题改编题目。'

        result = self._call_llm(system_prompt, user_prompt, temperature=0.4)
        return self._parse_json_result(result).get("questions", [])

    # ──────────────── Interview Feedback ────────────────

    def evaluate_answer(self, question: str, user_answer: str, resume_text: str) -> dict:
        """评估面试回答"""
        system_prompt = """你是一名资深面试官。评估候选人的面试回答。

要求：
1. 从完整性、逻辑性、相关性、技术深度4个维度评分
2. 指出回答中的亮点和不足
3. 给出具体的改进建议
4. 提供一份高分参考答案

请用JSON格式输出：{
    "score": 0-100,
    "scores": {"completeness": 0-100, "logic": 0-100, "relevance": 0-100, "depth": 0-100},
    "feedback": "综合评价",
    "improvements": ["改进1", "改进2"],
    "sample_answer": "参考答案"
}"""

        user_prompt = f"面试题：{question}\n\n候选人的回答：{user_answer}\n\n简历背景：{resume_text}"

        result = self._call_llm(system_prompt, user_prompt, temperature=0.3)
        return self._parse_json_result(result)

    # ──────────────── Helpers ────────────────

    def _parse_json_result(self, text: str) -> dict:
        """从 LLM 返回的文本中提取 JSON"""
        try:
            import re
            json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
            if json_match:
                text = json_match.group(1).strip()
            return json.loads(text)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to parse JSON from LLM response: {e}")
            try:
                import re
                obj_match = re.search(r"\{[\s\S]*\}", text)
                if obj_match:
                    return json.loads(obj_match.group())
            except Exception:
                pass
            return {"error": "Failed to parse response", "raw": text}

