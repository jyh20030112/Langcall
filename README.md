# LangCall Stage 1

这是 `LangCall` 的第一阶段最小可运行版本。

## 目标

先跑通这条主流程：

`txt 对话文件 -> LangGraph -> 脱敏 -> Prompt -> LLM -> 结构化 JSON`

## 目录

- `data/raw_calls/`: 原始测试对话
- `data/outputs/`: 第一阶段本地 JSON 输出
- `app/api/`: FastAPI 接口层
- `app/graph/`: LangGraph 工作流
- `app/services/`: 输入读取、脱敏、模型调用、预留存储接口
- `scripts/run_demo.py`: 启动脚本
- `compose.yaml`: 第二阶段基础服务容器编排
- `sql/init.sql`: PostgreSQL 初始化表结构

## 安装

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 配置

默认启用 `mock LLM`，即使没有真实模型 Key 也能先跑通流程。

如果要直接体验最小版本，`.env` 可以先保持：

```env
USE_MOCK_LLM=true
LITELLM_MODEL=gpt-4o-mini
RAW_CALLS_DIR=data/raw_calls
OUTPUT_DIR=data/outputs
```

如果后面要切换成真实模型：

```env
USE_MOCK_LLM=false
LITELLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_openai_api_key
```

## 运行

查看有哪些输入文件：

```bash
python scripts/run_demo.py --list
```

运行默认的第一个 txt 文件：

```bash
python scripts/run_demo.py
```

运行指定文件：

```bash
python scripts/run_demo.py data/raw_calls/call_003.txt
```

## FastAPI 启动

先安装依赖，然后在项目根目录执行：

```bash
uvicorn app.main:app --reload
```

启动成功后可以访问：

- 接口文档：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/health`

### Webhook 示例

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

这个接口已经改成异步入口：

`保存 raw_calls -> 创建 call_tasks -> 立即返回 task_id`

## 任务表 + Worker

现在 webhook 已经改成“只入库并创建任务”，不会同步等待 LLM 分析完成。

### 1. 先应用任务表 SQL

如果你的 PostgreSQL 容器是在新增 `call_tasks` 之前就已经启动过，`init.sql` 不会自动重新执行。  
这时请手动执行迁移脚本：

```bash
docker compose exec -T postgres psql -U langcall -d langcall < sql/migrations/001_add_call_tasks.sql
```

### 2. 启动 API

```bash
uvicorn app.main:app --reload
```

### 3. 启动 Worker

另开一个终端：

```bash
python -m app.workers.task_worker
```

### 4. 发送 webhook

```bash
curl -X POST "http://127.0.0.1:8000/webhooks/calls" \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "api_call_002",
    "source": "manual_webhook",
    "customer_phone": "13800138000",
    "customer_email": "demo@example.com",
    "transcript_raw": "客服：您好，请问最近有租房计划吗？\n用户：我想先了解一下价格和地段。"
  }'
```

这时接口会快速返回一个 `task_id`，而不是等待分析完成。

### 5. 查询任务状态

```bash
curl "http://127.0.0.1:8000/webhooks/tasks/1"
```

你会看到任务在以下状态之间变化：

- `pending`
- `processing`
- `success`
- `failed`

## 第二步：先起 Docker 基础服务

这一版采用“本机跑 Python，Docker 跑基础服务”的混合模式。

### 先启动容器

```bash
docker compose up -d
```

### 查看容器状态

```bash
docker compose ps
```

正常情况下你会看到这 4 个服务：

1. `postgres`
2. `redis`
3. `adminer`
4. `mailpit`

### 各服务用途

- `postgres`: 后续正式存储原始通话和分析结果
- `redis`: 后续做幂等控制和分布式锁
- `adminer`: 浏览器查看数据库
- `mailpit`: 本地测试邮件，不会真的发给外部邮箱

### 浏览器访问地址

- Adminer: `http://localhost:8080`
- Mailpit: `http://localhost:8025`

### Adminer 登录信息

- System: `PostgreSQL`
- Server: `postgres` 或 `host.docker.internal` 不适用于浏览器登录
- 如果你通过浏览器访问 Adminer，推荐填：
  - Server: `postgres`
  - Username: `langcall`
  - Password: `langcall123`
  - Database: `langcall`

### 本机 Python 连接 Docker 中的 PostgreSQL

因为当前阶段你的 Python 脚本是在本机运行，所以代码里连接数据库时应使用：

- Host: `localhost`
- Port: `5432`
- Database: `langcall`
- User: `langcall`
- Password: `langcall123`

这也是 `.env` 里当前的默认值。

### 停止容器

```bash
docker compose down
```

如果你想连数据卷一起删除：

```bash
docker compose down -v
```

## 输出

运行成功后，你会看到：

1. 原始对话文本
2. 脱敏后的文本
3. 模型原始输出
4. 校验后的 JSON
5. 数据库中的 `raw_calls` 和 `call_analysis` 新记录

## 下一步建议

现在基础服务已经容器化，下一步最合适的工作是：

1. 验证 `raw_call_repository.py` 已经能写入 `raw_calls` 表
2. 验证 `analysis_repository.py` 已经能写入 `call_analysis` 表
3. 再继续扩展批量导入、FastAPI 和 Worker
