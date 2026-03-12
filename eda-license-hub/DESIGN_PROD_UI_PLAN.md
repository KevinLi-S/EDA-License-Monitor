# EDA License Hub 页面改造与联调方案（生产化设计）

> 适用版本：`build/eda-license-hub-v1.3.2.tar.gz`
> 
> 测试环境：`192.168.110.128`
> 
> 目标：在现有 MVP 基础上，完成面向“模拟生产环境”的 EDA License 监控与管理页面设计，并为后续前后端联调提供直接可执行的实现路线。

---

## 1. 当前版本现状

当前项目已经具备以下基础能力：

### 1.1 后端现有接口
- `GET /api/dashboard`
- `GET /api/servers`
- `POST /api/servers`
- `PUT /api/servers/{id}`
- `DELETE /api/servers/{id}`
- `GET /api/servers/{id}/action-preview`
- `POST /api/servers/{id}/action`
- `GET /api/server-actions`
- `GET /api/features`
- `POST /api/license/upload`
- `GET /api/license-keys`
- `GET /api/license-logs`
- `GET /api/alerts`

### 1.2 前端现有页面
- Dashboard
- Servers
- License Keys
- Logs
- Alerts

### 1.3 当前版本优势
- 已具备基础导航和主页面框架
- 已支持 license 文件上传与 key 明细展示
- 已支持命令预览、Dry Run、Start/Stop/Restart 操作
- 已支持从日志中解析 Synopsys 活跃用户
- 已有风险摘要和日志检索基础能力

### 1.4 当前版本不足
当前更像“功能演示版”，离生产管理控制台还差以下几类能力：
- 首页缺少完整健康态视角
- 服务管理缺少聚合信息与详情下钻
- 告警页只有列表，没有处理闭环
- 日志页偏原始，不利于快速排障
- 缺少接入页/导入历史页
- 缺少面向真实环境 `192.168.110.128` 的联调说明和验收口径

---

## 2. 改造目标

本次改造不建议推翻重做，而建议按“**保留框架、补强信息架构、补齐生产管理闭环**”进行升级。

### 2.1 总目标
把系统从 MVP 升级为：
- 可日常值守的 License 监控首页
- 可安全操作的 License 服务管理页
- 可排障的日志与告警中心
- 可初始化与回放的 License 数据接入页

### 2.2 用户视角目标
页面需要同时满足两类使用者：

#### A. 运维/管理员
最关心：
- 哪台服务挂了
- 哪些 Feature 快满了
- 有没有高风险日志
- 操作能不能可控、可追溯

#### B. EDA 管理人员 / 团队负责人
最关心：
- 哪些 License 最紧张
- 哪些 Server 压力最大
- 哪些用户/主机正在占用资源
- 最近风险/异常是否增多

---

## 3. 页面信息架构

建议导航调整为：

- **总览 Dashboard**
- **服务管理 Servers**
- **Feature 使用情况 License Keys**
- **告警中心 Alerts**
- **日志中心 Logs**
- **数据接入 Upload / Ingestion**（新增）

说明：
- 当前已有页面不要大拆，只做升级。
- Upload 页面建议从 Servers 页面拆出，避免“服务管理页职责过重”。

---

## 4. 各页面详细设计

# 4.1 总览页 Dashboard

## 目标
让用户在 10 秒内回答下面几个问题：
- 系统是不是健康
- 有没有高风险问题
- 哪些资源最紧张
- 哪些服务最值得立刻关注

## 推荐布局

### 区块 A：顶部总览卡片
建议展示：
- Vendor 数
- Server 总数
- 在线 Server 数（新增）
- 离线 / stale Server 数（新增）
- Open Alerts 数
- Critical Risks 数
- 高利用率 Feature 数（新增）
- 即将到期 License 数（新增）

### 区块 B：服务健康总览
建议新增一个按 Vendor 聚合的服务健康区块：
- Vendor
- 服务总数
- 在线数
- 异常数
- 最近采集时间

这块信息可以先由后端新增 dashboard 聚合字段实现，也可以前端先基于 `/servers` 做临时聚合。

### 区块 C：Top Busy Features
保留当前表格，但增强：
- 使用率百分比
- 红黄绿阈值高亮
- 点击一行跳转到 License Keys 并带筛选条件

推荐阈值：
- `< 75%` 正常
- `75% ~ 89%` 预警
- `>= 90%` 高危

### 区块 D：风险摘要
保留当前 `risk_summary`，增强展示为：
- critical / high / medium 数量卡片
- 风险明细小表格
- 支持跳转日志页并带关键词过滤

### 区块 E：最近事件流（建议新增）
聚合以下事件：
- server action 执行
- license upload
- alerts 新增
- 高风险日志命中

如果后端暂时不提供统一事件流，可先由前端拼接：
- `/server-actions`
- `/alerts`

---

# 4.2 服务管理页 Servers

## 目标
把它从“服务列表页”升级成“管理控制台入口”。

## 当前问题
当前列表字段偏少，主要只能看：
- 名称
- vendor
- host
- port
- status

不足以支撑生产排查。

## 推荐字段
建议表格展示：
- 服务名
- Vendor
- Host
- Port
- 状态
- 最后采集时间
- 当前 Feature 数（新增）
- 当前总量 / 已用 / 空闲（新增）
- 风险等级（新增）
- 操作

## 状态定义建议
统一状态语义：
- `online`：在线可用
- `offline`：明确离线
- `restarting`：执行重启中
- `stale`：最近一段时间无数据更新，疑似异常
- `unknown`：初始或不可判断

推荐 `stale` 判断：
- `last_seen_at` 超过 5 分钟/10 分钟未更新

## 操作区建议
保留：
- Start
- Stop
- Restart
- Preview Cmd
- Edit
- Delete

增强：
- 默认打开 `Dry Run`
- 真执行前显示确认内容
- 将“Preview”和“Execute”串起来，避免盲操作
- 支持查看最近操作日志抽屉

## 详情能力（建议新增）
点击服务名进入详情抽屉或详情页，展示：
- 基本信息
- 当前 Feature 明细
- 最近操作日志
- 关联告警
- 近期异常日志
- 最近采集时间与状态演变

如果当前后端无聚合接口，前端第一版可通过以下接口拼装：
- `/servers`
- `/license-keys`
- `/server-actions`
- `/alerts`
- `/license-logs`

---

# 4.3 Feature 使用情况页 License Keys

## 目标
把它从“Key 列表页”升级成“资源占用分析页”。

## 当前页面优点
- 已有 vendor 筛选
- 已有 keyword 搜索
- 已有 usage 进度条
- 已有 active user 展示

## 推荐增强
### 筛选条件
建议增加：
- Vendor
- Server
- Feature 名称
- 使用率区间
- 是否临近耗尽
- 是否临近到期

### 表格字段建议
保留并增强：
- Feature
- Vendor
- Version
- Server
- Total
- Used
- Free（新增列）
- Utilization %
- Active User Count
- Expiry
- Collected At（建议新增）

### 交互建议
- 使用率高于阈值时高亮整行
- Active Users 支持展开或 Drawer 查看
- 点击 Feature 可以跳转到“按 Feature 过滤后的日志/告警”

### 页面补强建议
增加两个统计卡片：
- 总 Feature 数
- 高利用率 Feature 数
- 即将到期数
- 有活跃用户的 Feature 数

---

# 4.4 告警中心 Alerts

## 目标
从“告警查看”升级到“告警处理入口”。

## 当前问题
当前只有简单表格，不够管理化。

## 推荐展示字段
- Type
- Severity
- Status
- Message
- Source Server（建议后端补）
- Source Feature（建议后端补）
- Created At
- Last Seen At（建议新增）
- Duration（建议前端/后端补）

## 页面分区建议
- 未处理告警
- 已恢复 / 已关闭告警
- 告警趋势摘要

## 告警类型建议规范化
- `server_down`
- `collect_timeout`
- `low_free_license`
- `license_expiring`
- `log_error_hit`
- `risk_finding`
- `action_failed`
- `license_upload`

## 交互建议
- 严重性颜色标准化：critical/red，high/volcano，medium/gold，low/blue
- 支持按 severity、status、type 过滤
- 支持从告警跳转到对应 server / feature / logs

---

# 4.5 日志中心 Logs

## 目标
用于快速定位异常，而不是简单滚日志。

## 当前优点
- 已有 vendor 筛选
- 已有 keyword 搜索
- 已有 full/error 模式切换

## 推荐增强
### 筛选器
- Vendor
- Mode: full / error
- Keyword
- 时间范围（后端后续补）
- 自动刷新（前端控制）

### 表格建议字段
- Vendor
- Line
- Severity（前端基于关键词推断）
- Content
- Matched Keyword（前端解析）

### 交互建议
- 对 `error/denied/failed/tampered/expired` 等词高亮
- 支持点击行查看上下文
- 支持跳转来源 server / vendor

### 备注
后端当前日志接口不带时间戳结构化字段，因此第一阶段日志中心先做“增强检索和高亮”，暂不做完整时间轴。

---

# 4.6 数据接入页 Upload / Ingestion（新增）

## 目标
把当前散落在 Servers 页中的 upload 功能独立出来，变成“数据接入页”。

## 建议页面内容
### 模块 A：上传文件
- 选择文件
- 上传按钮
- 上传结果提示

### 模块 B：解析预览
- server name
- vendor
- port
- parsed features 数量

### 模块 C：导入历史（后端后续可补）
- 文件名
- 上传时间
- 识别结果
- 处理状态

### 模块 D：测试环境提示
明确显示当前联调目标：
- 环境 IP：`192.168.110.128`
- 使用说明：在测试环境中验证 license 数据导入后，返回 Dashboard / License Keys / Alerts 页面确认联动结果

---

## 5. 前后端字段映射建议

# 5.1 Dashboard

## 现有可用字段
来自 `/api/dashboard`：
- `vendor_count`
- `server_count`
- `open_alerts`
- `top_busy_features[]`
- `risk_summary`

## 建议新增字段
- `online_server_count`
- `offline_server_count`
- `stale_server_count`
- `hot_feature_count`
- `expiring_soon_count`
- `vendors[]`（每个 vendor 的健康摘要）
- `recent_events[]`

---

# 5.2 Servers

## 现有可用字段
来自 `/api/servers`：
- `id`
- `name`
- `vendor`
- `host`
- `port`
- `status`
- `last_seen_at`

## 建议新增字段
- `feature_count`
- `total_licenses`
- `used_licenses`
- `free_licenses`
- `risk_level`
- `alert_count`

---

# 5.3 License Keys

## 现有可用字段
来自 `/api/license-keys`：
- `feature`
- `vendor`
- `version`
- `total`
- `used`
- `expiry`
- `server`
- `active_user_count`
- `active_users`

## 建议新增字段
- `free`
- `utilization`
- `collected_at`
- `status`
- `is_expiring_soon`

其中：
- `free`、`utilization` 可由前端先计算
- `collected_at` 建议后端补回

---

# 5.4 Alerts

## 现有可用字段
来自 `/api/alerts`：
- `id`
- `type`
- `severity`
- `message`
- `status`
- `created_at`

## 建议新增字段
- `server`
- `feature`
- `last_seen_at`
- `duration_sec`
- `source_type`
- `source_ref`

---

# 5.5 Logs

## 现有可用字段
来自 `/api/license-logs`：
- `id`
- `vendor`
- `line`
- `content`

## 建议新增字段
- `timestamp`
- `severity`
- `matched_keyword`
- `server`

第一阶段这些可以先由前端进行轻量推断，不阻塞 UI 改造。

---

## 6. 推荐开发顺序

### P1：前端先行可见改造
1. Dashboard 样式和结构升级
2. Servers 列表增强
3. License Keys 增加 Free / Utilization 维度
4. Alerts 增加筛选和严重等级视觉规范
5. Logs 增加高亮和错误标注
6. Upload 从 Servers 页拆成独立页面

### P2：后端聚合增强
1. Dashboard 增加在线/离线/stale/热点/到期统计
2. Servers 增加聚合字段
3. License Keys 增加 `collected_at`
4. Alerts 增加来源定位字段
5. 增加服务详情聚合接口

### P3：测试环境联调
在 `192.168.110.128` 上执行：
1. 联 Dashboard
2. 联 Servers
3. 联 License Keys
4. 联 Alerts
5. 联 Logs
6. 联 Upload
7. 人工构造异常场景做验收

---

## 7. 面向 192.168.110.128 的联调建议

## 7.1 联调目标
测试环境已经部署完整的 license 与 license 服务，因此应把它视为“准生产环境”：
- 用于验证页面信息是否真实完整
- 用于验证操作链路是否安全可控
- 用于验证告警和日志是否能反映实际异常

## 7.2 建议联调顺序
### Step 1：只读联调
验证这些接口返回是否满足页面设计：
- `/api/dashboard`
- `/api/servers`
- `/api/license-keys`
- `/api/alerts`
- `/api/license-logs`

### Step 2：管理动作联调
验证：
- `/api/servers/{id}/action-preview`
- `/api/servers/{id}/action`

要求：
- 先 preview
- 默认 dry run
- 再做真实 start/stop/restart 验证

### Step 3：异常演练
在测试环境上人为制造：
- 停掉一个服务
- 构造高占用 feature
- 构造风险日志关键字
- 上传临近到期或不同 vendor 的 license 文件

验证页面是否出现正确联动：
- Dashboard 卡片变化
- Alerts 生成
- Logs 可检索
- License Keys 数据刷新

---

## 8. 建议验收标准

### 8.1 Dashboard 验收
- 能一眼看出整体健康态
- 高危 feature 有明显标识
- 风险摘要可定位到日志视图

### 8.2 Servers 验收
- 能查看服务列表和基础状态
- 支持 Add/Edit/Delete
- 支持 Preview / Dry Run / Real Action
- 操作后日志可追溯

### 8.3 License Keys 验收
- 能筛选 vendor / feature / server
- 能展示 active users
- 能识别高利用率项

### 8.4 Alerts 验收
- 能按 severity / status 筛选
- 未处理与已处理状态清晰
- 告警能指向具体问题对象

### 8.5 Logs 验收
- 能筛选 vendor
- 能搜索关键词
- Error 模式能快速定位异常
- 高风险关键字有视觉高亮

### 8.6 Upload 验收
- 上传成功后能看到解析结果
- 数据会反映到 Dashboard / License Keys / Alerts

---

## 9. 直接落地的前端改造建议

## 9.1 最小改动策略
为了减少返工，推荐这样改：

- 保留 `App.jsx` 主体布局
- 保留现有页面文件名
- 新增 `UploadPage.jsx`
- 调整菜单顺序和文案
- 在现有页面内部逐步增强，不大规模重写路由

## 9.2 建议新增公共工具
建议在 `frontend/src` 下后续增加：
- `utils/format.js`：格式化时间、百分比、状态文案
- `utils/status.js`：状态颜色与 severity 映射
- `components/StatusTag.jsx`
- `components/MetricCard.jsx`
- `components/FilterBar.jsx`

这样后面 UI 风格会统一很多。

---

## 10. 分工建议（按你的命名习惯）

### 石榴
负责：
- 需求分析
- 页面信息架构
- 前后端接口对齐
- 前端页面实现

### 麻薯
负责：
- 联调测试
- 测试环境回归验证
- 异常场景演练
- 缺陷记录与维护

### 榴莲
负责：
- Code Review
- 重点审查：服务操作安全性、状态表达、异常场景处理

---

## 11. 下一步建议

建议按以下顺序继续推进：

### 方案 A：先改文档再开发
适合先达成共识
1. 确认本方案
2. 输出页面字段清单
3. 开始前端改造

### 方案 B：直接进入前端改造
适合现在立刻开发
1. 调整导航结构
2. 新增 Upload 页面
3. 升级 Dashboard / Servers / Alerts / Logs / License Keys
4. 本地 build 验证
5. 再上 `192.168.110.128` 联调

---

## 12. 推荐结论

对当前 `v1.3.2`，最合理的演进方式不是“重新设计一套全新系统”，而是：

**以现有页面为骨架，补齐生产化管理闭环。**

优先顺序建议为：
1. Dashboard 升级
2. Servers 管理增强
3. Upload 页面拆分
4. License Keys 分析增强
5. Alerts / Logs 管理化
6. 测试环境 `192.168.110.128` 联调和验收

这样收益最大，改动成本也最低。
