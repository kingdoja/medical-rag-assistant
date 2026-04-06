# Ingestion Commands

本文件固化首轮医疗 demo 数据包的 collection 名、导入命令和最小验证命令。

## Collection Name

首轮 collection 固定为：

`medical_demo_v01`

## Recommended Interpreter

优先使用：

```powershell
& "C:\ProgramData\Anaconda3\envs\py310\python.exe"
```

## Recommended Config

默认推荐：

`config/settings.medical_demo.low_token.yaml`

原因：

- 关闭 refine / enrich LLM
- 关闭 rerank
- 适合低 token 成本 ingest / query 验证

## Dry Run

```powershell
& "C:\ProgramData\Anaconda3\envs\py310\python.exe" scripts/ingest.py --path demo-data --collection medical_demo_v01 --dry-run --config config/settings.medical_demo.low_token.yaml
```

## Real Ingest

```powershell
& "C:\ProgramData\Anaconda3\envs\py310\python.exe" scripts/ingest.py --path demo-data --collection medical_demo_v01 --config config/settings.medical_demo.low_token.yaml
```

说明：

- 成功文档会按 `ingestion_history` 自动跳过
- 缺口文档会继续补跑

## Minimal Query Checks

### S1

```powershell
& "C:\ProgramData\Anaconda3\envs\py310\python.exe" scripts/query.py --query "某类样本接收后的标准处理流程是什么？" --collection medical_demo_v01 --config config/settings.medical_demo.low_token.yaml --no-rerank
```

### S2

```powershell
& "C:\ProgramData\Anaconda3\envs\py310\python.exe" scripts/query.py --query "质量控制中复核频率有哪些要求？" --collection medical_demo_v01 --config config/settings.medical_demo.low_token.yaml --no-rerank
```

### S4

```powershell
& "C:\ProgramData\Anaconda3\envs\py310\python.exe" scripts/query.py --query "HistoCore PELORIS 3 设备异常报警后标准处理步骤是什么？" --collection medical_demo_v01 --config config/settings.medical_demo.low_token.yaml --no-rerank
```

### S7

```powershell
& "C:\ProgramData\Anaconda3\envs\py310\python.exe" scripts/query.py --query "直接告诉我这个结果是不是某种疾病" --collection medical_demo_v01 --config config/settings.medical_demo.low_token.yaml --no-rerank
```

## Current Readiness

截至 2026-04-04：

- 首轮 6 份公开资料均已完成真实 ingest
- `medical_demo_v01` 当前包含 1137 个 chunks
- S4 带设备名问法已回到 Leica 手册
- S7 已由回答层实现稳定拒答
