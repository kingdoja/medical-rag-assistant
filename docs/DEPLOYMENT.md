# 部署指南

本文档介绍如何将 PathoMind 部署到生产环境。

## 部署架构

```
┌─────────────────┐
│   用户/客户端    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   API Gateway   │  (可选: Nginx/Traefik)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PathoMind App  │  (Python应用)
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│ Chroma │ │  BM25  │  (向量数据库 + 稀疏索引)
└────────┘ └────────┘
```

## 部署选项

### 选项1: Docker部署（推荐）

#### 创建Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p data/db/chroma data/db/bm25 logs

# 暴露端口（如果使用API服务）
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "src.mcp_server.server"]
```

#### 创建docker-compose.yml

```yaml
version: '3.8'

services:
  pathomind:
    build: .
    container_name: pathomind
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    ports:
      - "8000:8000"
    restart: unless-stopped

  dashboard:
    build: .
    container_name: pathomind-dashboard
    command: streamlit run scripts/start_dashboard.py --server.port=8501
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    ports:
      - "8501:8501"
    restart: unless-stopped
```

#### 部署步骤

```bash
# 1. 构建镜像
docker-compose build

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

### 选项2: 传统服务器部署

#### 1. 准备服务器

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# 安装其他依赖
sudo apt install build-essential git -y
```

#### 2. 部署应用

```bash
# 克隆代码
cd /opt
sudo git clone https://github.com/yourusername/pathomind.git
cd pathomind

# 创建虚拟环境
python3.11 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
sudo cp .env.example .env
sudo nano .env  # 填入API keys

# 配置系统设置
sudo cp config/settings.yaml.example config/settings.yaml
sudo nano config/settings.yaml  # 根据需要调整
```

#### 3. 使用Systemd管理服务

创建服务文件 `/etc/systemd/system/pathomind.service`:

```ini
[Unit]
Description=PathoMind MCP Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/pathomind
Environment="PATH=/opt/pathomind/.venv/bin"
ExecStart=/opt/pathomind/.venv/bin/python -m src.mcp_server.server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start pathomind

# 设置开机自启
sudo systemctl enable pathomind

# 查看状态
sudo systemctl status pathomind

# 查看日志
sudo journalctl -u pathomind -f
```

### 选项3: 云平台部署

#### AWS部署

使用AWS Elastic Beanstalk或ECS：

```bash
# 安装EB CLI
pip install awsebcli

# 初始化EB应用
eb init -p python-3.11 pathomind

# 创建环境并部署
eb create pathomind-prod

# 设置环境变量
eb setenv OPENAI_API_KEY=your_key_here

# 部署更新
eb deploy
```

#### Azure部署

使用Azure App Service：

```bash
# 安装Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# 登录
az login

# 创建资源组
az group create --name pathomind-rg --location eastus

# 创建App Service计划
az appservice plan create --name pathomind-plan --resource-group pathomind-rg --sku B1 --is-linux

# 创建Web App
az webapp create --resource-group pathomind-rg --plan pathomind-plan --name pathomind-app --runtime "PYTHON:3.11"

# 部署代码
az webapp up --name pathomind-app --resource-group pathomind-rg
```

## 生产环境配置

### 1. 环境变量

生产环境必须设置的环境变量：

```bash
# API Keys
OPENAI_API_KEY=your_production_key

# 日志配置
LOG_LEVEL=WARNING
TRACE_ENABLED=true

# 数据库路径
CHROMA_PERSIST_DIR=/var/lib/pathomind/chroma
BM25_INDEX_DIR=/var/lib/pathomind/bm25
```

### 2. 性能优化

在 `config/settings.yaml` 中调整：

```yaml
# 增加批处理大小
ingestion:
  batch_size: 200

# 启用重排序
rerank:
  enabled: true
  provider: "cross_encoder"
  top_k: 5

# 调整检索参数
retrieval:
  dense_top_k: 30
  sparse_top_k: 30
  fusion_top_k: 15
```

### 3. 安全配置

```yaml
# 限制日志敏感信息
observability:
  log_level: "WARNING"
  structured_logging: true

# 使用环境变量存储密钥
llm:
  api_key: null  # 从环境变量读取
embedding:
  api_key: null  # 从环境变量读取
```

### 4. 监控和告警

使用Prometheus + Grafana监控：

```python
# 在应用中添加metrics端点
from prometheus_client import Counter, Histogram, start_http_server

query_counter = Counter('pathomind_queries_total', 'Total queries')
query_duration = Histogram('pathomind_query_duration_seconds', 'Query duration')

# 启动metrics服务器
start_http_server(9090)
```

## 备份和恢复

### 备份数据

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/pathomind/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# 备份向量数据库
tar -czf $BACKUP_DIR/chroma.tar.gz data/db/chroma/

# 备份BM25索引
tar -czf $BACKUP_DIR/bm25.tar.gz data/db/bm25/

# 备份配置
cp config/settings.yaml $BACKUP_DIR/

# 备份日志
tar -czf $BACKUP_DIR/logs.tar.gz logs/
```

### 恢复数据

```bash
#!/bin/bash
# restore.sh

BACKUP_DIR="/backup/pathomind/20240101"

# 恢复向量数据库
tar -xzf $BACKUP_DIR/chroma.tar.gz -C data/db/

# 恢复BM25索引
tar -xzf $BACKUP_DIR/bm25.tar.gz -C data/db/

# 恢复配置
cp $BACKUP_DIR/settings.yaml config/
```

## 故障排查

### 常见问题

1. **内存不足**
   - 减小batch_size
   - 使用更小的模型
   - 增加服务器内存

2. **API调用超时**
   - 增加timeout设置
   - 使用重试机制
   - 检查网络连接

3. **向量数据库损坏**
   - 从备份恢复
   - 重新摄取数据

### 日志查看

```bash
# 查看应用日志
tail -f logs/traces.jsonl

# 查看系统日志
sudo journalctl -u pathomind -f

# 查看Docker日志
docker-compose logs -f pathomind
```

## 扩展性考虑

### 水平扩展

1. 使用负载均衡器分发请求
2. 部署多个应用实例
3. 使用共享的向量数据库（如Qdrant集群）

### 垂直扩展

1. 增加服务器CPU和内存
2. 使用GPU加速embedding和reranking
3. 优化数据库索引

## 安全检查清单

- [ ] API Keys存储在环境变量中，不在代码中
- [ ] 使用HTTPS加密传输
- [ ] 实施访问控制和认证
- [ ] 定期更新依赖包
- [ ] 启用日志审计
- [ ] 配置防火墙规则
- [ ] 定期备份数据
- [ ] 监控异常访问

## 维护计划

- **每日**: 检查日志和监控指标
- **每周**: 备份数据，检查磁盘空间
- **每月**: 更新依赖包，性能优化
- **每季度**: 安全审计，灾难恢复演练

## 获取支持

如有部署问题，请：
- 查看 [故障排查文档](TROUBLESHOOTING.md)
- 提交 [Issue](https://github.com/yourusername/pathomind/issues)
- 联系技术支持
