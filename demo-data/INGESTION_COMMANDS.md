# Ingestion Commands

本文件记录首轮医疗 demo 数据包的建议 collection 名称、导入命令和首轮验证命令。

## Collection Name

建议首轮 collection 名称固定为：

`medical_demo_v01`

## Important Environment Notes

- 当前系统默认 `python` 解释器不兼容项目里使用的 `str | Path` 语法
- 导入与查询命令请优先使用：

```powershell
& "C:\ProgramData\Anaconda3\envs\py310\python.exe"
```

- 当前 `config/settings.yaml` 仍是占位 API key
- 真正执行 ingest / query 前，需要先提供可用的 OpenAI / Azure / Ollama 配置

## Recommended Minimal Config

建议先复制：

```powershell
Copy-Item config/settings.medical_demo.local.example.yaml config/settings.medical_demo.local.yaml
```

然后只修改：

- `embedding.api_key`

如果你后面想打开：

- 图像 caption
- LLM 精炼
- LLM 元数据增强

再单独补 `llm.api_key` 与 `vision_llm.api_key`。

## Dry Run

```powershell
& "C:\ProgramData\Anaconda3\envs\py310\python.exe" scripts/ingest.py --path demo-data --collection medical_demo_v01 --dry-run
```

## Full Ingestion

```powershell
& "C:\ProgramData\Anaconda3\envs\py310\python.exe" scripts/ingest.py --path demo-data --collection medical_demo_v01
```

如果你使用 demo 专用配置，建议显式指定：

```powershell
& "C:\ProgramData\Anaconda3\envs\py310\python.exe" scripts/ingest.py --path demo-data --collection medical_demo_v01 --config config/settings.medical_demo.local.yaml
```

## Query Smoke Tests

### S1 SOP 查询

```powershell
& "C:\ProgramData\Anaconda3\envs\py310\python.exe" scripts/query.py --query "某类标本接收后的标准处理流程是什么？" --collection medical_demo_v01
```

### S2 指南查询

```powershell
& "C:\ProgramData\Anaconda3\envs\py310\python.exe" scripts/query.py --query "质量控制中复核频率有哪些要求？" --collection medical_demo_v01
```

### S4 设备操作

```powershell
& "C:\ProgramData\Anaconda3\envs\py310\python.exe" scripts/query.py --query "设备异常报警后标准处理步骤是什么？" --collection medical_demo_v01
```

### S7 边界拒答

```powershell
& "C:\ProgramData\Anaconda3\envs\py310\python.exe" scripts/query.py --query "直接告诉我这个结果是不是某种疾病" --collection medical_demo_v01
```

如果你使用 demo 专用配置，查询命令同样建议补上：

```powershell
--config config/settings.medical_demo.local.yaml
```

## Current Readiness

- 已下载 6 份核心公开资料
- 已通过 `--dry-run` 识别到 6 个 PDF
- 未完成真实 ingest，因为当前还缺有效模型配置
- 已提供最小化配置模板，首轮只需填 `embedding.api_key`
