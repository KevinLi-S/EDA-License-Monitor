# Python 依赖版本说明

## 当前版本（Python 3.6+ 兼容）

```
fastapi==0.68.2          # 最后支持 Python 3.6 的稳定版本
uvicorn==0.15.0          # 兼容 FastAPI 0.68.2
sqlalchemy==1.4.48       # SQLAlchemy 1.4 系列，稳定且兼容
pydantic==1.10.13        # Pydantic v1，Python 3.6 兼容
python-dateutil==2.8.2   # 日期处理库
python-multipart==0.0.6  # 文件上传支持
```

## 版本选择理由

### FastAPI 0.68.2
- ✅ 支持 Python 3.6+
- ✅ 包含所有核心功能（路由、依赖注入、自动文档）
- ✅ 稳定版本，生产环境验证
- ⚠️ FastAPI 0.70+ 开始要求 Python 3.7+
- ⚠️ FastAPI 0.100+ 要求 Python 3.8+

### SQLAlchemy 1.4.48
- ✅ 支持 Python 3.6+
- ✅ 功能完整（ORM、查询构建器）
- ✅ 向后兼容 1.3.x
- ⚠️ SQLAlchemy 2.0+ 要求 Python 3.7+

### Pydantic 1.10.13
- ✅ 支持 Python 3.6+
- ✅ 数据验证和序列化
- ✅ 与 FastAPI 0.68 完美配合
- ⚠️ Pydantic 2.0+ 要求 Python 3.7+

## CentOS 7.9 2009 默认环境

- Python 版本：3.6.8（yum install python3）
- pip 版本：9.0.3（需要升级到 21.x）

## 升级路径

如果服务器有 Python 3.8+，可以使用新版本：

### Python 3.8+ 版本（可选）

```txt
fastapi==0.100.0
uvicorn==0.22.0
sqlalchemy==2.0.20
pydantic==2.0.0
python-dateutil==2.8.2
python-multipart==0.0.9
```

### Python 3.10+ 版本（推荐）

```txt
fastapi==0.115.0
uvicorn==0.30.6
sqlalchemy==2.0.35
pydantic==2.9.2
python-dateutil==2.9.0.post0
python-multipart==0.0.9
```

## 安装 Python 3.8+ (CentOS 7)

如果需要使用新版本：

```bash
# 安装 SCL 仓库
yum install -y centos-release-scl

# 安装 Python 3.8
yum install -y rh-python38

# 启用 Python 3.8
scl enable rh-python38 bash

# 或安装 Python 3.9
yum install -y rh-python39
scl enable rh-python39 bash
```

## 验证安装

```bash
# 检查 Python 版本
python3 --version

# 测试安装
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -c "import fastapi; print(fastapi.__version__)"
```

## 功能支持

### 当前版本（0.68.2）支持的功能

✅ 完整的 REST API 支持
✅ 依赖注入系统
✅ 自动 API 文档（/docs）
✅ Pydantic 数据验证
✅ WebSocket 支持
✅ 后台任务
✅ 文件上传
✅ CORS 中间件
✅ 所有本项目需要的功能

### 不支持的功能（vs 最新版）

❌ Pydantic v2 的性能优化
❌ 某些最新的类型注解特性
❌ Python 3.10+ 的语法特性

**结论：对于本项目完全够用，无功能缺失。**

## 生产环境建议

- **CentOS 7.9**: 使用当前版本（Python 3.6 兼容）
- **CentOS 8/Rocky 8**: 可以考虑升级到 Python 3.8+
- **Ubuntu 20.04+**: 建议使用 Python 3.10+ 和最新版本

---

**当前配置已针对 CentOS 7.9 2009 优化，可直接部署使用。**
