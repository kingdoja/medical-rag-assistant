# Medical Demo Startup Guide

这份文档用于在 Windows + PowerShell 下快速启动当前仓库，并跑通医疗 demo 的最小链路。

真源请以 [STARTUP_RUNBOOK.md](/d:/ai应用项目/MODULAR-RAG-MCP-SERVER/docs/specs/medical-assistant/STARTUP_RUNBOOK.md) 为准；本文件是面向实际启动的精简版。

## 1. 推荐解释器

优先使用：

```powershell
& "C:\ProgramData\Anaconda3\envs\py310\python.exe"
```

## 2. 初始化环境

```powershell
& "C:\ProgramData\Anaconda3\envs\py310\python.exe" -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## 3. 配置 API Key

```powershell
Copy-Item .env.example .env -Force
```

在 `.env` 中填写：

```env
OPENAI_API_KEY=YOUR_DASHSCOPE_API_KEY
```

## 4. 推荐配置

首轮 demo 默认推荐：

`config/settings.medical_demo.low_token.yaml`

特点：

- 关闭 refine / enrich LLM
- 关闭 rerank
- ingest 批量大小固定为 10
- 更适合低 token 成本验证和演示前 smoke test

## 5. 最小验证

### S4 设备题

```powershell
python scripts/query.py --query "HistoCore PELORIS 3 设备异常报警后标准处理步骤是什么？" --collection medical_demo_v01 --config config/settings.medical_demo.low_token.yaml --no-rerank
```

### S7 边界题

```powershell
python scripts/query.py --query "直接告诉我这个结果是不是某种疾病" --collection medical_demo_v01 --config config/settings.medical_demo.low_token.yaml --no-rerank
```

## 6. Ingest 命令

### Dry Run

```powershell
python scripts/ingest.py --path demo-data --collection medical_demo_v01 --dry-run --config config/settings.medical_demo.low_token.yaml
```

### Real Ingest

```powershell
python scripts/ingest.py --path demo-data --collection medical_demo_v01 --config config/settings.medical_demo.low_token.yaml
```

说明：

- 已成功的文档会自动跳过
- 不建议再用旧路径重跑整包 `demo-data`

## 7. 启动 Dashboard

```powershell
python scripts/start_dashboard.py --host localhost --port 8501
```

浏览器访问：

```text
http://localhost:8501
```

## 8. 推荐演示顺序

按固定链路：

`S1 -> S2 -> S4 -> S7 -> S12`

完整说明见：

- [DEMO_RUNBOOK_3MIN.md](/d:/ai应用项目/MODULAR-RAG-MCP-SERVER/docs/specs/medical-assistant/DEMO_RUNBOOK_3MIN.md)

## 9. 当前基线

截至 2026-04-04：

- collection: `medical_demo_v01`
- sources: 6
- chunks: 1137
- S4 已回到 Leica 手册
- S7 已实现稳定拒答
