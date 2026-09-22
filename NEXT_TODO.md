# 1.6 下一步 TODO

以下 TODO 均基于当前仓库已经存在的模块、接口、配置和代码风险，不要求当前已有对应 Commit。

| 优先级 | TODO | 对应模块/接口 | 验收方式 |
|---|---|---|---|
| P0 | 将 `interview_sessions` 从内存字典迁移到持久化存储，并增加过期策略 | `backend/main.py` `/api/interview/*` | 重启服务后会话行为符合设计；过期会话返回 404 |
| P0 | 将支付订单与学生认证从内存字典迁移到持久化存储，并实现支付回调/签名校验 | `backend/payment.py` `/api/payment/*` | 支付成功后状态可恢复；非法回调不能改变订单状态 |
| P0 | 修复支付创建接口的参数校验顺序和重复字段声明 | `backend/payment.py` `CheckoutRequest` / `create_payment` | 无效 `plan_id` 返回 400，而不是触发 `None.get`；模型字段唯一 |
| P1 | 移除学生认证接口返回 `debug_code` 的行为，接入真实邮件验证码服务并增加验证码过期/限流 | `backend/payment.py` `/send-code` `/verify-code` | API 响应不泄露验证码；验证码超时和重复请求受控 |
| P1 | 收紧 CORS、上传限制和错误信息，避免生产环境使用 `allow_origins=["*"]` + credentials | `backend/main.py` | 配置生产允许域名后跨域请求正常，未授权来源被拒绝 |
| P1 | 为 LLM JSON 输出增加 Pydantic schema 校验、字段默认值和失败重试/降级策略 | `backend/ai_service.py` / `backend/models.py` | 非法模型输出不会直接污染 API 响应；错误有稳定结构 |
| P1 | 增加 PDF/DOCX、AI 分析、面试和支付接口的自动化测试 | `backend/*` | CI 中核心 API 和解析路径有可重复测试 |
| P2 | 增加上传文件生命周期管理与清理任务，避免 `uploads/` 长期堆积 | `backend/main.py` | 成功/失败解析后的文件按策略保留或清理 |
| P2 | 为 `count`、`question_id`、空答案等面试参数增加边界校验 | `backend/main.py` `/api/interview/start` `/answer` | 非法参数返回明确 4xx，不调用 LLM |
