# 自动驾驶文档摄取命令

本文档提供将自动驾驶文档摄取到系统的命令和配置。

## 前置条件

1. 确保已安装所有依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 配置环境变量（`.env` 文件）：
   ```bash
   OPENAI_API_KEY=your_api_key_here
   ```

3. 准备配置文件：
   ```bash
   cp config/settings.yaml config/settings.ad_knowledge.yaml
   ```

## 配置文件示例

`config/settings.ad_knowledge.yaml`:

```yaml
# Collection 配置
collection:
  name: ad_knowledge_v01
  description: "自动驾驶知识库 v0.1"

# LLM 配置
llm:
  provider: openai
  model: gpt-4o-mini
  temperature: 0.1
  max_tokens: 2000

# Embedding 配置
embedding:
  provider: openai
  model: text-embedding-3-small
  batch_size: 100
  dimensions: 1536

# 检索配置
retrieval:
  top_k: 20
  rerank_top_k: 5
  fusion_method: rrf
  bm25_weight: 0.5
  dense_weight: 0.5

# Reranker 配置
reranker:
  provider: cross_encoder
  model: BAAI/bge-reranker-base
  top_k: 5

# 向量数据库配置
vector_store:
  provider: chroma
  persist_directory: data/db/chroma
  collection_name: ad_knowledge_v01

# BM25 配置
bm25:
  persist_directory: data/db/bm25
  collection_name: ad_knowledge_v01

# 分块配置
chunking:
  chunk_size: 800
  chunk_overlap: 200
  separators: ["\n\n", "\n", "。", "！", "？", ". ", "! ", "? "]

# 元数据配置
metadata:
  boost_config:
    sensor_query:
      sensor_doc: 1.5
      algorithm_doc: 0.8
    algorithm_query:
      algorithm_doc: 1.3
      sensor_doc: 0.9
    regulation_query:
      regulation_doc: 1.6
      test_doc: 1.2
  
  authority_scores:
    regulation_doc: 1.0
    algorithm_doc: 0.8
    sensor_doc: 0.6
    test_doc: 0.4
```

## 摄取命令

### 1. 摄取所有文档

```bash
python scripts/ingest.py \
  --collection ad_knowledge_v01 \
  --source demo-data-ad \
  --config config/settings.ad_knowledge.yaml \
  --recursive
```

### 2. 分类摄取

#### 摄取传感器文档
```bash
python scripts/ingest.py \
  --collection ad_knowledge_v01 \
  --source demo-data-ad/sensors \
  --config config/settings.ad_knowledge.yaml \
  --metadata '{"document_type": "sensor_doc"}' \
  --recursive
```

#### 摄取算法文档
```bash
python scripts/ingest.py \
  --collection ad_knowledge_v01 \
  --source demo-data-ad/algorithms \
  --config config/settings.ad_knowledge.yaml \
  --metadata '{"document_type": "algorithm_doc"}' \
  --recursive
```

#### 摄取法规文档
```bash
python scripts/ingest.py \
  --collection ad_knowledge_v01 \
  --source demo-data-ad/regulations \
  --config config/settings.ad_knowledge.yaml \
  --metadata '{"document_type": "regulation_doc"}' \
  --recursive
```

#### 摄取测试文档
```bash
python scripts/ingest.py \
  --collection ad_knowledge_v01 \
  --source demo-data-ad/tests \
  --config config/settings.ad_knowledge.yaml \
  --metadata '{"document_type": "test_doc"}' \
  --recursive
```

### 3. 增量摄取

如果已经摄取过部分文档，可以使用增量摄取（跳过已处理的文档）：

```bash
python scripts/ingest.py \
  --collection ad_knowledge_v01 \
  --source demo-data-ad \
  --config config/settings.ad_knowledge.yaml \
  --incremental \
  --recursive
```

### 4. 强制重新摄取

如果需要重新处理所有文档：

```bash
python scripts/ingest.py \
  --collection ad_knowledge_v01 \
  --source demo-data-ad \
  --config config/settings.ad_knowledge.yaml \
  --force \
  --recursive
```

## 摄取参数说明

- `--collection`：Collection 名称
- `--source`：文档源目录
- `--config`：配置文件路径
- `--metadata`：额外的元数据（JSON 格式）
- `--recursive`：递归处理子目录
- `--incremental`：增量摄取（跳过已处理文档）
- `--force`：强制重新处理所有文档
- `--batch-size`：批处理大小（默认 10）
- `--skip-images`：跳过图片处理

## 验证摄取结果

### 1. 检查 Collection 统计

```bash
python scripts/check_collection.py \
  --collection ad_knowledge_v01 \
  --config config/settings.ad_knowledge.yaml
```

### 2. 查询测试

```bash
python scripts/query.py \
  --collection ad_knowledge_v01 \
  --query "激光雷达的探测距离是多少？" \
  --config config/settings.ad_knowledge.yaml
```

### 3. 查看摄取报告

摄取完成后会生成报告文件：
- `data/ingestion_reports/ad_knowledge_v01_YYYYMMDD_HHMMSS.json`

报告内容包括：
- 处理的文档数量
- 生成的 chunk 数量
- 处理时间
- 错误和警告

## 元数据标签示例

### 传感器文档元数据
```json
{
  "document_type": "sensor_doc",
  "sensor_type": "lidar",
  "content_type": "specification",
  "manufacturer": "Velodyne",
  "model": "VLS-128",
  "version": "v1.0"
}
```

### 算法文档元数据
```json
{
  "document_type": "algorithm_doc",
  "algorithm_type": "perception",
  "algorithm_category": "object_detection",
  "algorithm_name": "YOLO",
  "version": "v3.0"
}
```

### 法规文档元数据
```json
{
  "document_type": "regulation_doc",
  "regulation_type": "national_standard",
  "standard_number": "GB/T 40429-2021",
  "standard_name": "汽车驾驶自动化分级",
  "publish_date": "2021-03-09"
}
```

### 测试文档元数据
```json
{
  "document_type": "test_doc",
  "test_type": "functional",
  "test_category": "following",
  "scenario_name": "ACC跟车场景",
  "version": "v1.0"
}
```

## 常见问题

### Q1: 摄取速度慢怎么办？
A: 可以调整以下参数：
- 增加 `--batch-size`
- 使用更快的 embedding 模型
- 减小 chunk_size

### Q2: 如何处理大文件？
A: 系统会自动分块处理，但可以：
- 调整 chunk_size 和 chunk_overlap
- 使用 `--skip-images` 跳过图片处理
- 分批摄取

### Q3: 如何更新已摄取的文档？
A: 使用增量摄取：
```bash
python scripts/ingest.py \
  --collection ad_knowledge_v01 \
  --source demo-data-ad \
  --incremental
```

### Q4: 如何删除 Collection？
A: 使用清理脚本：
```bash
python scripts/clean_collection.py \
  --collection ad_knowledge_v01 \
  --confirm
```

## 性能优化建议

1. **批处理**：使用合适的 batch_size（推荐 10-50）
2. **并行处理**：使用多进程处理（需要修改脚本）
3. **缓存**：启用 embedding 缓存
4. **增量更新**：使用 `--incremental` 避免重复处理

## 监控和日志

### 查看摄取日志
```bash
tail -f logs/ingestion.log
```

### 查看错误日志
```bash
grep ERROR logs/ingestion.log
```

### 监控进度
摄取过程中会显示进度条和统计信息。

## 下一步

摄取完成后：
1. 运行查询测试验证系统功能
2. 运行评估脚本检查质量
3. 启动 Dashboard 查看统计信息
4. 开始使用系统进行知识检索
