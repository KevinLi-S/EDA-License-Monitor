# EDA-License-Monitor — Phase 2 baseline

这是基于全新架构继续推进的 **phase-2 可跑版本**，目标是：

- 保持 `backend/ + frontend/ + celery + postgres` 新架构
- 不回退到旧 v1.4.x 修补路线
- 接入可运行的 FlexLM/lmutil 数据采集链路
- 引入 PostgreSQL / Alembic 初始化方案
- 让 Dashboard / Overview / Servers 至少一条主链路返回真实或准真实落库数据

## 本次已完成

### 1. Collector service（真实/准真实数据链路）
- 新增 `backend/app/services/flexlm_parser.py`
  - 解析通用 `lmutil lmstat -a` 风格输出
  - 支持识别：server up/down、vendor daemon status、feature total/used、checkout 明细
- 新增 `backend/app/services/collector_service.py`
  - 支持两类采集源：
    - `source_type=lmutil`：执行真实 `lmutil lmstat ...`
    - `source_type=sample_file`：读取样本输出文件，便于本地联调/回归
  - 采集结果落库到：
    - `license_servers`
    - `license_features`
    - `license_usage_history`
    - `license_checkouts`
- Celery beat 已继续复用 `app.tasks.collectors.collect_license_snapshots`

### 2. PostgreSQL / migration / init
- Alembic env 已切到 `app.core.*` 新结构
- 首版 migration：`backend/alembic/versions/001_initial.py`
- 新增：
  - `backend/scripts/init_db.py`：建表并初始化 sample server 配置
  - `backend/scripts/run_collection_once.py`：手工触发一次采集
- `.env.example` 增加：
  - `SYNC_DATABASE_URL`（Alembic 用）
  - `COLLECTOR_TIMEOUT_SECONDS`

### 3. 已接真数据的接口
- `GET /api/v1/overview`
  - 已从 PostgreSQL 聚合 KPI / server snapshot / collector alerts
- `GET /api/v1/servers`
  - 已从 PostgreSQL 返回真实 server + feature 聚合信息
- `POST /api/v1/servers/refresh`
  - 已触发一次 collector（便于前端按钮手动刷新）
- `GET /api/v1/analytics/usage-trend`
  - 已从 `license_usage_history` 读取趋势点（前端暂未做图表）
- `GET /api/v1/health`
  - 已增加 DB 探活

## 样本与真实 lmutil 的关系

当前仓库自带两个 sample：
- `backend/samples/lmstat/synopsys_main.txt`
- `backend/samples/lmstat/cadence_pool.txt`

所以你即使本地没有真实 lmutil，也可以先完整跑通：
**sample_file -> parser -> collector -> postgres -> overview/servers**

当切到真实环境时，只需要把 `license_servers` 中某条记录改成：
- `source_type=lmutil`
- `lmutil_path=/path/to/lmutil`（或保持系统 PATH 可直接执行）
- `lmstat_args="lmstat -a -c 27000@your-license-host"`

## 本地运行

### 方式一：Docker Compose
```bash
cp .env.example .env
docker compose up --build
```

然后另开一个 shell：
```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python -m scripts.init_db
docker compose exec backend python -m scripts.run_collection_once
```

访问：
- Frontend: <http://localhost>
- Health: <http://localhost/api/v1/health>
- Overview: <http://localhost/api/v1/overview>
- Servers: <http://localhost/api/v1/servers>

### 方式二：本地分别运行
```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
set DATABASE_URL=postgresql+asyncpg://eda_admin:eda_admin_change_me@localhost:5432/eda_license
set SYNC_DATABASE_URL=postgresql+psycopg://eda_admin:eda_admin_change_me@localhost:5432/eda_license
alembic upgrade head
python -m scripts.init_db
python -m scripts.run_collection_once
uvicorn app.main:app --reload
```

前端：
```bash
cd frontend
npm install
npm run dev
```

## 还缺什么
- 真实生产环境的多厂商 lmstat 样本还不够，当前 parser 是通用版 + sample 验证版，不是完整 vendor-special parser
- 还没做 SSH 跳板/远程执行 lmutil（当前是本机执行 lmutil 或读取 sample file）
- WebSocket 增量广播仍是 phase-1 占位
- 前端 Alerts / Analytics 页面还是轻量占位
- 没做登录、权限、服务器控制操作
- 没做 collector 失败重试、告警规则、清理历史数据策略

## 结论
这版已经不是纯 mock：
- Dashboard / overview / servers 主链路已接 PostgreSQL 落库数据
- collector service 可跑
- 可用 sample_file 做准真实联调，也可切到真实 lmutil 命令模式
- 架构仍保持 phase-1 新骨架，没有回退到旧版目录和实现方式
