# 自动驾驶文档元数据标签指南

本指南说明如何为自动驾驶文档添加元数据标签，以支持智能检索和分类。

## 概述

元数据标签系统根据文档的位置和文件名自动识别文档类型，并添加相应的元数据标签。系统支持四种文档类型：

1. **传感器文档** (sensor_doc)
2. **算法文档** (algorithm_doc)
3. **法规文档** (regulation_doc)
4. **测试文档** (test_doc)

## 元数据标签结构

### 1. 传感器文档 (sensor_doc)

**目录位置**: `demo-data-ad/sensors/`

**元数据字段**:
```yaml
document_type: sensor_doc
sensor_type: camera | lidar | radar | ultrasonic
content_type: specification | calibration | installation | maintenance
```

**识别规则**:
- **sensor_type**: 根据文件路径和文件名中的关键词识别
  - `camera`: camera, 摄像头, 相机, vision
  - `lidar`: lidar, 激光雷达, velodyne, hesai
  - `radar`: radar, 毫米波, continental, bosch_radar
  - `ultrasonic`: ultrasonic, 超声波, uss

- **content_type**: 根据文件名中的关键词识别
  - `specification`: spec, 规格, datasheet, 参数
  - `calibration`: calib, 标定, intrinsic, extrinsic
  - `installation`: install, 安装, mount
  - `maintenance`: maintain, 维护, service

**示例**:
```
demo-data-ad/sensors/camera/sony_imx490_spec.pdf
→ document_type: sensor_doc
→ sensor_type: camera
→ content_type: specification

demo-data-ad/sensors/lidar/velodyne_calibration_guide.pdf
→ document_type: sensor_doc
→ sensor_type: lidar
→ content_type: calibration
```

### 2. 算法文档 (algorithm_doc)

**目录位置**: `demo-data-ad/algorithms/`

**元数据字段**:
```yaml
document_type: algorithm_doc
algorithm_type: perception | planning | control | slam
algorithm_category: 具体算法类别
```

**识别规则**:
- **algorithm_type**: 根据文件路径和文件名中的关键词识别
  - `perception`: perception, 感知, detect, 检测, recognition, yolo
  - `planning`: planning, 规划, path, 路径, trajectory, 轨迹
  - `control`: control, 控制, pid, mpc, lateral, longitudinal
  - `slam`: slam, localization, 定位, mapping

- **algorithm_category**: 根据文件名自动推断
  - 感知算法: object_detection, lane_detection, segmentation
  - 规划算法: path_planning, trajectory_planning
  - 控制算法: lateral_control, longitudinal_control

**示例**:
```
demo-data-ad/algorithms/perception/yolo_object_detection.pdf
→ document_type: algorithm_doc
→ algorithm_type: perception
→ algorithm_category: object_detection

demo-data-ad/algorithms/planning/path_planning_algorithm.pdf
→ document_type: algorithm_doc
→ algorithm_type: planning
→ algorithm_category: path_planning
```

### 3. 法规文档 (regulation_doc)

**目录位置**: `demo-data-ad/regulations/`

**元数据字段**:
```yaml
document_type: regulation_doc
regulation_type: national_standard | iso_standard | test_spec | industry_standard
standard_number: 标准编号
```

**识别规则**:
- **regulation_type**: 根据文件路径和文件名中的关键词识别
  - `national_standard`: gb/t, 国标, 国家标准
  - `iso_standard`: iso, 国际标准
  - `test_spec`: test.*spec, 测试规范
  - `industry_standard`: industry, 行业标准, sae

- **standard_number**: 从文件名中提取
  - GB/T 格式: `GB_T_40429-2021.pdf` → `GB/T 40429-2021`
  - ISO 格式: `ISO_26262.pdf` → `ISO 26262`

**示例**:
```
demo-data-ad/regulations/national/GB_T_40429-2021.pdf
→ document_type: regulation_doc
→ regulation_type: national_standard
→ standard_number: GB/T 40429-2021

demo-data-ad/regulations/iso/ISO_26262_part3.pdf
→ document_type: regulation_doc
→ regulation_type: iso_standard
→ standard_number: ISO 26262
```

### 4. 测试文档 (test_doc)

**目录位置**: `demo-data-ad/tests/`

**元数据字段**:
```yaml
document_type: test_doc
test_type: functional | safety | boundary | performance | simulation | real_vehicle
test_category: 具体测试类别
```

**识别规则**:
- **test_type**: 根据文件路径和文件名中的关键词识别
  - `functional`: functional, 功能测试
  - `safety`: safety, 安全测试, collision
  - `boundary`: boundary, 边界, edge_case
  - `performance`: performance, 性能, benchmark
  - `simulation`: simulation, 仿真, carla
  - `real_vehicle`: real.*vehicle, 实车, road_test

- **test_category**: 根据文件名自动推断
  - `following`: acc, 跟车
  - `lane_change`: lane, 变道
  - `overtaking`: overtake, 超车
  - `parking`: parking, 泊车

**示例**:
```
demo-data-ad/tests/functional/acc_following_test.pdf
→ document_type: test_doc
→ test_type: functional
→ test_category: following

demo-data-ad/tests/safety/collision_avoidance_test.pdf
→ document_type: test_doc
→ test_type: safety
```

## 使用方法

### 1. 自动标签工具

使用 `tag_ad_documents.py` 脚本自动分析和标记文档：

```bash
# 查看所有文档的元数据标签
python scripts/tag_ad_documents.py --path demo-data-ad --verbose

# 查看统计摘要
python scripts/tag_ad_documents.py --path demo-data-ad --summary

# 生成元数据 JSON 文件
python scripts/tag_ad_documents.py --path demo-data-ad --generate-json

# 验证现有元数据文件
python scripts/tag_ad_documents.py --path demo-data-ad --validate
```

### 2. 在摄取流程中使用

元数据标签将在文档摄取时自动应用。修改 `scripts/ingest.py` 以集成元数据标签：

```python
from src.ingestion.metadata import ADMetadataTagger

# 初始化标签器
tagger = ADMetadataTagger()

# 为文档添加元数据
metadata = tagger.tag_document(file_path)
if metadata:
    # 将元数据添加到文档
    document.metadata.update(metadata.to_dict())
```

### 3. 在查询中使用

元数据标签可用于过滤和提升检索结果：

```python
# 查询传感器文档
results = query_engine.query(
    "激光雷达的探测距离",
    filters={"document_type": "sensor_doc", "sensor_type": "lidar"}
)

# 查询算法文档
results = query_engine.query(
    "目标检测算法",
    filters={"document_type": "algorithm_doc", "algorithm_type": "perception"}
)
```

## 元数据示例文件

在 `demo-data-ad/examples/` 目录中提供了四种文档类型的元数据示例：

1. `sensor_metadata_example.json` - 传感器文档元数据示例
2. `algorithm_metadata_example.json` - 算法文档元数据示例
3. `regulation_metadata_example.json` - 法规文档元数据示例
4. `test_metadata_example.json` - 测试文档元数据示例

## 文件命名建议

为了确保元数据标签的准确性，建议遵循以下命名规范：

### 传感器文档
```
{厂商}_{型号}_{内容类型}.pdf
例如: velodyne_vls128_spec.pdf
     sony_imx490_calibration.pdf
```

### 算法文档
```
{算法名称}_{算法类别}.pdf
例如: yolo_object_detection.pdf
     mpc_lateral_control.pdf
```

### 法规文档
```
{标准编号}_{标准名称}.pdf
例如: GB_T_40429-2021_自动驾驶分级.pdf
     ISO_26262_part3_功能安全.pdf
```

### 测试文档
```
{测试类型}_{场景名称}_test.pdf
例如: functional_acc_following_test.pdf
     safety_collision_avoidance_test.pdf
```

## 扩展元数据标签

如需添加新的文档类型或标签，可以修改 `src/ingestion/metadata/ad_metadata_tagger.py`：

1. 在相应的 `PATTERNS` 字典中添加新的模式
2. 在 `tag_document()` 方法中添加新的文档类型检测逻辑
3. 更新 `DocumentMetadata` 数据类以包含新字段
4. 添加相应的单元测试

## 常见问题

### Q1: 文档类型识别不准确怎么办？
A: 确保文档放在正确的目录下（sensors/, algorithms/, regulations/, tests/），并且文件名包含相关关键词。

### Q2: 如何手动指定元数据？
A: 可以创建 `.metadata.json` 文件与文档同名，手动指定元数据。摄取时会优先使用手动指定的元数据。

### Q3: 支持哪些文件格式？
A: 目前支持 PDF、Markdown、TXT 等文本格式。图片和视频文件需要先转换为文本描述。

### Q4: 元数据标签会影响检索性能吗？
A: 元数据标签会提升检索准确性，对性能影响很小。建议在查询时使用元数据过滤以提高相关性。

## 参考资料

- [COLLECTION_GUIDE.md](COLLECTION_GUIDE.md) - 文档收集指南
- [INGESTION_COMMANDS.md](INGESTION_COMMANDS.md) - 文档摄取命令
- [Design Document](../.kiro/specs/autonomous-driving-knowledge-retrieval/design.md) - 系统设计文档

