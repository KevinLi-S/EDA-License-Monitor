# EDA License Hub 生产部署手册（CentOS 7.9 / Rocky 8.10）

> 目标：在内网 Linux 服务器部署 `License Portal`，接入真实 license/dat/log 数据。

## 一键傻瓜式部署（推荐，按固定目录命名）

适配你的固定布局：

- Synopsys: `/eda/env/license/synopsys_lic01.dat`, `/eda/env/license/synopsys_lic02.dat`
- Cadence: `/eda/env/license/cadence_lic01.dat`, `/eda/env/license/cadence_lic02.dat`
- Mentor: `/eda/env/license/mentor_lic01.dat`, `/eda/env/license/mentor_lic02.dat`
- Logs: `/eda/env/license/log/*.log`（支持 `synopsys_lic01.log` 这类）

部署步骤（离线物理机）：

```bash
# 1) 解压离线全量包到 /opt/license-portal
mkdir -p /opt/license-portal
cd /opt/license-portal
tar -xzf centos7.9-x86_64.tar.gz --strip-components=1
# Rocky 使用 rocky8.10-x86_64.tar.gz

# 2) 执行一键离线部署（需root）
chmod +x deploy/*.sh
./deploy/offline_oneclick.sh
```

可选手工刷新（后续更新 license 文件后执行）：
```bash
./deploy/sync_fixed_layout.sh
```

## 1. 部署模式说明

推荐两种模式：

- **模式A：Docker 部署（推荐 Rocky 8.10）**
  - 优点：隔离好、升级方便
- **模式B：原生部署（CentOS 7.9 推荐）**
  - 优点：兼容老系统、便于与本地工具链集成

---

## 2. 软件包清单

### 通用
- 项目包：`license-portal-release.tar.gz`（本次已打包）

### Docker 模式（Rocky 8.10）
- Docker Engine + Docker Compose plugin

### 原生模式（CentOS 7.9）
- Python 3.9+
- Node.js 20+
- nginx

---

## 3. 快速部署（Docker，Rocky 8.10）

### 3.1 安装 Docker
```bash
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf -y install docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl enable --now docker
```

### 3.2 上传并解压发布包
```bash
mkdir -p /opt/license-portal
cd /opt/license-portal
tar -xzf license-portal-release.tar.gz --strip-components=1
```

### 3.3 配置真实日志挂载路径
编辑 `docker-compose.yml` 中 backend volume：
```yaml
volumes:
  - "/data/eda/logs:/data/logs:ro"
```
要求目录包含：
- `/data/eda/logs/synopsys.log`
- （可选）`/data/eda/logs/ansys.log`

### 3.4 启动
```bash
docker compose up -d --build
```

### 3.5 导入 license dat
```bash
curl -X POST -F "file=@/data/eda/license/synopsys.dat" http://127.0.0.1:8000/api/license/upload
```

### 3.6 验证
```bash
curl http://127.0.0.1:8000/api/health
curl "http://127.0.0.1:8000/api/license-keys?vendor=synopsys&limit=5"
curl "http://127.0.0.1:8000/api/license-logs?vendor=synopsys&mode=full&limit=5"
```

前端访问：`http://<服务器IP>:8080`

---

## 4. 原生部署（CentOS 7.9）

### 4.1 安装依赖
```bash
# Python 3（示例，按你环境调整）
sudo yum -y install epel-release
sudo yum -y install python3 python3-pip nginx git

# Node.js 20（NodeSource）
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo yum -y install nodejs
```

### 4.2 部署后端
```bash
mkdir -p /opt/license-portal
cd /opt/license-portal
tar -xzf license-portal-release.tar.gz --strip-components=1

cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 关键：指向真实日志目录
export LOG_BASE_DIR=/data/eda/logs

uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4.3 部署前端
```bash
cd /opt/license-portal/frontend
cp .env.example .env
sed -i 's#VITE_API_BASE_URL=.*#VITE_API_BASE_URL=http://127.0.0.1:8000/api#g' .env
sed -i 's#VITE_USE_MOCK=.*#VITE_USE_MOCK=false#g' .env

npm install
npm run build

sudo mkdir -p /usr/share/nginx/license-portal
sudo cp -r dist/* /usr/share/nginx/license-portal/
```

### 4.4 Nginx 配置
创建 `/etc/nginx/conf.d/license-portal.conf`：
```nginx
server {
  listen 80;
  server_name _;

  location /api/ {
    proxy_pass http://127.0.0.1:8000/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }

  location / {
    root /usr/share/nginx/license-portal;
    try_files $uri /index.html;
  }
}
```

重启 nginx：
```bash
sudo nginx -t && sudo systemctl restart nginx
```

### 4.5 导入 license dat
```bash
curl -X POST -F "file=@/data/eda/license/synopsys.dat" http://127.0.0.1:8000/api/license/upload
```

---

## 5. 生产接入建议

1. **只读挂载**日志与license目录（避免误写生产文件）
2. 定时任务（每5分钟）调用 upload 接口重刷数据
3. 首期仅开启 dry-run，确认后再开放真实命令执行
4. 建议通过 Nginx + 内网 ACL 限制访问

---

## 6. 常见问题

- Q: Servers 页面动作报 `snpslmdctl not found`
  - A: 当前后端运行环境没有 Synopsys SCL 工具链；需在宿主机安装并加入 PATH，或把命令改为可执行绝对路径。

- Q: Logs 页面为空
  - A: 检查 `LOG_BASE_DIR` 是否正确，且目录内存在 `synopsys.log`。

- Q: Dashboard 使用量与预期不同
  - A: 当前 used 基于日志 OUT/IN 净值；若日志被切割或缺失会影响实时值。
