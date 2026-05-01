# LangCall

`LangCall` 是一个面向客服/销售通话场景的 AI 智能分析与自动化系统。  
当前版本已经完成从 `API 接收 -> 数据入库 -> 任务异步处理 -> LangGraph 分析 -> Redis 幂等与锁 -> 重试/死信 -> 日报汇总 -> Mailpit 邮件发送` 的完整闭环。

## 当前已实现模块

当前项目已经落地的模块有：

1. `LangGraph` 分析工作流
2. `FastAPI` 接口层
3. `PostgreSQL` 原始数据、任务、分析结果、死信、日报持久化
4. `Redis` 幂等保护与分布式锁
5. `Worker` 异步任务处理
6. `指数退避重试 + 死信队列`
7. `Mailpit` 测试邮件
8. `日报汇总 + HTML 邮件发送`

## 系统整体流程

当前系统的完整业务流程如下：

```text
Webhook / API 请求
  -> 保存 raw_calls
  -> Redis webhook 幂等判断
  -> 创建 call_tasks
  -> API 立即返回 task_id
  -> Worker 轮询 call_tasks
  -> Redis call_id 分布式锁
  -> 读取 raw_calls
  -> LangGraph 分析工作流
  -> 保存 call_analysis
  -> 更新任务状态
  -> 失败时按指数退避重试
  -> 超过阈值写入 dead_letter_queue
  -> 日报汇总 daily_reports
  -> Mailpit 发送测试邮件
```

## LangGraph 子工作流

当前 LangGraph 图内流程是：

```text
normalize_input
-> mask_pii
-> build_prompt
-> run_llm
-> validate_output
```

也就是说：

- `FastAPI / Worker / Redis / PostgreSQL` 属于系统工作流
- `LangGraph` 属于系统工作流中的分析子流程

## 项目目录

```text
第一阶段可运行版本/
├── app/
│   ├── api/
│   │   └── routes/
│   ├── core/
│   ├── graph/
│   ├── schemas/
│   ├── services/
│   └── workers/
├── data/
│   └── raw_calls/
├── scripts/
├── sql/
│   ├── init.sql
│   └── migrations/
├── compose.yaml
├── requirements.txt
└── .env
```

各目录职责：

- `app/api/`: FastAPI 接口
- `app/graph/`: LangGraph 工作流
- `app/services/`: 业务服务层
- `app/workers/`: 异步 Worker 与调度器
- `sql/`: 建表与迁移脚本
- `scripts/`: 手动测试脚本
- `data/raw_calls/`: 本地 txt 输入样本

## 数据库表

当前项目已经使用的核心表：

1. `raw_calls`
   - 保存原始通话文本和基础字段

2. `call_tasks`
   - 保存异步任务状态
   - 当前可能状态：
     - `pending`
     - `processing`
     - `retrying`
     - `success`
     - `dead`

3. `call_analysis`
   - 保存 LangGraph 结构化分析结果

4. `dead_letter_queue`
   - 保存超过最大重试次数的失败任务

5. `daily_reports`
   - 保存日报发送记录和 HTML 内容

## 运行模式

当前项目采用“本机跑 Python，Docker 跑基础服务”的混合模式。

本机运行：

- FastAPI
- Worker
- report scheduler
- 本地脚本

Docker 运行：

- PostgreSQL
- Redis
- Adminer
- Mailpit

## 安装依赖

在项目根目录执行：

```bash
pip install -r requirements.txt
```

## 环境变量

请在 `.env` 中配置你自己的参数。关键项如下：

```env

USE_MOCK_LLM=false
LITELLM_MODEL=dashscope/qwen3-max-2026-01-23
RAW_CALLS_DIR=data/raw_calls
OUTPUT_DIR=data/outputs
DASHSCOPE_API_KEY=your_dashscope_api_key

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=langcall
POSTGRES_USER=langcall
POSTGRES_PASSWORD=langcall123

REDIS_HOST=localhost
REDIS_PORT=6379

SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_FROM=langcall@example.com
REPORT_TO=manager@example.com

REPORT_TIMEZONE=Asia/Shanghai
REPORT_HOUR=8
REPORT_MINUTE=0

WORKER_POLL_INTERVAL_SECONDS=3
WEBHOOK_IDEMPOTENCY_TTL_SECONDS=30
CALL_PROCESSING_LOCK_TTL_SECONDS=120
MAX_RETRY_COUNT=3
RETRY_BACKOFF_BASE_SECONDS=2

API_PORT=8000
ADMINER_PORT=8080
MAILPIT_WEB_PORT=8025

```

## 启动基础服务

### 启动 Docker 服务

```bash
docker compose up -d
```

### 查看容器状态

```bash
docker compose ps
```

正常情况下会看到：

1. `postgres`
2. `redis`
3. `adminer`
4. `mailpit`

### 访问地址

- Adminer: `http://127.0.0.1:8080`
- Mailpit: `http://127.0.0.1:8025`

### Adminer 登录

- System: `PostgreSQL`
- Server: `postgres`
- Username: `langcall`
- Password: `langcall123`
- Database: `langcall`

## 数据库迁移

如果你的 PostgreSQL 是很早之前就创建好的，需要按顺序补迁移。

### 任务表迁移

```bash
docker compose exec -T postgres psql -U langcall -d langcall < sql/migrations/001_add_call_tasks.sql
```

### 重试与死信迁移

```bash
docker compose exec -T postgres psql -U langcall -d langcall < sql/migrations/002_add_retry_and_dead_letter.sql
```

### 日报表迁移

```bash
docker compose exec -T postgres psql -U langcall -d langcall < sql/migrations/003_add_daily_reports.sql
```

如果你是全新启动的数据库，`sql/init.sql` 会自动执行，一般不需要手动补迁移。

## 启动应用

### 1. 启动 FastAPI

```bash
uvicorn app.main:app --reload
```

可访问：

- OpenAPI 文档：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/health`

### 2. 启动任务 Worker

另开一个终端：

```bash
python -m app.workers.task_worker
```

### 3. 启动日报调度器

另开一个终端：

```bash
python -m app.workers.report_scheduler
```

## API 接口

### 健康检查

```bash
curl "http://127.0.0.1:8000/health"
```

### 创建通话任务

```bash
curl -X POST "http://127.0.0.1:8000/webhooks/calls" \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "api_call_001",
    "source": "manual_webhook",
    "customer_phone": "13800138000",
    "customer_email": "demo@example.com",
    "transcript_raw": "客服：您好，请问最近有租房计划吗？\n用户：我想先了解一下价格和地段。"
  }'
```

当前接口行为：

- 只保存 `raw_calls`
- 创建 `call_tasks`
- 快速返回 `task_id`
- 不同步等待模型分析

### 查询任务状态

```bash
curl "http://127.0.0.1:8000/webhooks/tasks/1"
```

### 发送测试邮件

```bash
curl -X POST "http://127.0.0.1:8000/mail/test" \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "manager@example.com",
    "subject": "LangCall Mailpit Test",
    "message": "This is a test email sent to Mailpit."
  }'
```

### 发送日报

```bash
curl -X POST "http://127.0.0.1:8000/reports/daily/send" \
  -H "Content-Type: application/json" \
  -d '{
    "report_date": "2026-04-30",
    "recipient": "manager@example.com"
  }'
```

### 查询已保存日报

```bash
curl "http://127.0.0.1:8000/reports/daily/2026-04-30"
```

## Worker、Redis 与重试机制

### 任务处理

Worker 会不断轮询 `call_tasks`，取出：

- `pending`
- `retrying` 且 `next_attempt_at <= now()`

的任务进行处理。

### Redis 幂等

在 API 入口：

- 同一个 `call_id` 的短时间重复请求会被 Redis 幂等键拦截
- 已有任务不会重复创建

### Redis 分布式锁

在 Worker 处理前：

- 按 `call_id` 获取 Redis 锁
- 避免多个 Worker 并发分析同一条通话

### 重试机制

失败后按指数退避重试：

- 第 1 次失败：2 秒
- 第 2 次失败：4 秒
- 第 3 次失败：8 秒

对应配置：

```env
MAX_RETRY_COUNT=3
RETRY_BACKOFF_BASE_SECONDS=2
```

### 死信队列

超过最大重试次数后：

- 任务状态改成 `dead`
- 详细失败上下文写入 `dead_letter_queue`

## Mailpit 测试邮件

除了 API，你也可以直接用脚本发送测试邮件：

```bash
python scripts/send_test_email.py
```

发送成功后去浏览器查看：

```text
http://127.0.0.1:8025
```

## 日报汇总

日报模块会从 `call_analysis` 中按天汇总：

- 总通话数
- 正向数量
- 中性数量
- 负向数量
- 混合数量
- 需跟进数量
- 每通电话的摘要与建议动作

然后：

1. 生成 HTML 内容
2. 通过 Mailpit 发送
3. 落库到 `daily_reports`

### 手动脚本发送日报

发送当天日报：

```bash
python scripts/send_daily_report.py
```

发送指定日期日报：

```bash
python scripts/send_daily_report.py 2026-04-30
```

## 本地 txt 演示

如果你想继续用本地样本快速验证 LangGraph 主链，也可以执行：

查看可用输入：

```bash
python scripts/run_demo.py --list
```

运行默认样本：

```bash
python scripts/run_demo.py
```

运行指定文件：

```bash
python scripts/run_demo.py data/raw_calls/call_003.txt
```

## 当前推荐测试顺序

建议按下面顺序验证整个系统：

1. `docker compose up -d`
2. `pip install -r requirements.txt`
3. `uvicorn app.main:app --reload`
4. `python -m app.workers.task_worker`
5. 调用 `POST /webhooks/calls`
6. 查看 `call_tasks` 状态变化
7. 查看 `call_analysis` 是否生成
8. 调用 `POST /mail/test`
9. 查看 `http://127.0.0.1:8025`
10. 调用 `POST /reports/daily/send`
11. 查看 `daily_reports` 与 Mailpit 邮件内容






