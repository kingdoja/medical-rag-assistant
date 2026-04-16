# 自动驾驶文档收集指南

本指南提供详细的文档收集方法和资源推荐。

## 收集目标

- **总计**：至少 260 份文档
- **传感器文档**：>= 50 份
- **算法文档**：>= 80 份
- **法规文档**：>= 30 份
- **测试文档**：>= 100 份

## 文档来源推荐

### 1. 传感器文档来源

#### 公开资源
- **厂商官网**：
  - Velodyne（激光雷达）：https://velodynelidar.com/
  - Continental（毫米波雷达）：https://www.continental.com/
  - Bosch（超声波雷达）：https://www.bosch.com/
  - Sony（摄像头传感器）：https://www.sony-semicon.com/

- **技术白皮书**：
  - 各传感器厂商发布的技术白皮书
  - 行业协会发布的传感器技术报告
  - 学术会议论文（CVPR, ICCV, IROS）

- **开源项目文档**：
  - Apollo 传感器标定文档
  - Autoware 传感器配置文档
  - OpenPilot 传感器集成文档

#### 收集方法
1. 访问厂商官网下载产品规格书
2. 搜索技术白皮书和应用指南
3. 查找开源项目中的传感器文档
4. 收集行业报告和对比分析

### 2. 算法文档来源

#### 公开资源
- **开源项目**：
  - Apollo：https://github.com/ApolloAuto/apollo
  - Autoware：https://github.com/autowarefoundation/autoware
  - CARLA：https://carla.org/
  - OpenPilot：https://github.com/commaai/openpilot

- **学术论文**：
  - arXiv：https://arxiv.org/ (搜索 autonomous driving, perception, planning)
  - IEEE Xplore：https://ieeexplore.ieee.org/
  - Google Scholar：https://scholar.google.com/

- **技术博客**：
  - Waymo Blog：https://blog.waymo.com/
  - Tesla AI Day 技术分享
  - 各大科技公司技术博客

#### 收集方法
1. 下载开源项目的算法设计文档
2. 收集学术论文（感知、规划、控制领域）
3. 整理技术博客和技术分享
4. 编写算法综述和对比文档

### 3. 法规文档来源

#### 公开资源
- **国家标准**：
  - 国家标准全文公开系统：http://openstd.samr.gov.cn/
  - GB/T 40429-2021 汽车驾驶自动化分级
  - GB/T 34590 系列功能安全标准

- **国际标准**：
  - ISO 官网：https://www.iso.org/
  - SAE International：https://www.sae.org/
  - ISO 26262 功能安全标准
  - ISO/PAS 21448 (SOTIF)

- **行业规范**：
  - 中国智能网联汽车产业创新联盟
  - 中国汽车工程学会
  - 各地自动驾驶测试管理规范

#### 收集方法
1. 访问国家标准全文公开系统下载 GB/T 标准
2. 购买或查找 ISO 标准文档
3. 收集行业协会发布的规范文件
4. 整理各地测试管理办法

### 4. 测试文档来源

#### 公开资源
- **测试场景库**：
  - NHTSA 测试场景
  - Euro NCAP 测试规程
  - C-NCAP 智能辅助测试规程
  - OpenSCENARIO 场景描述

- **测试标准**：
  - GB/T 测试方法标准
  - ISO 测试标准
  - 行业测试规范

- **测试报告**：
  - 各大车企发布的测试报告
  - 第三方测试机构报告
  - 学术研究测试数据

#### 收集方法
1. 下载公开的测试场景库
2. 收集测试标准和规范
3. 整理测试用例模板
4. 编写测试场景定义文档

## 文档格式要求

### 支持的格式
- **PDF**：首选格式，适合规格书、标准文档
- **DOCX**：适合编辑的文档
- **TXT/MD**：适合纯文本文档
- **HTML**：网页文档（需转换为 PDF）

### 文档质量要求
- **清晰度**：文字清晰可读，图片分辨率足够
- **完整性**：文档内容完整，无缺页
- **准确性**：信息准确，来源可靠
- **时效性**：优先选择最新版本

## 文档整理流程

### 1. 收集阶段
1. 按照文档类型分类收集
2. 记录文档来源和下载日期
3. 检查文档质量和完整性
4. 重命名文档（按命名规范）

### 2. 整理阶段
1. 将文档放入对应目录
2. 更新 `sources.md` 登记表
3. 为文档添加元数据标签
4. 编写文档摘要（可选）

### 3. 验证阶段
1. 检查文档数量是否达标
2. 验证文档类型分布是否合理
3. 确认文档质量符合要求
4. 准备摄取到系统

## 文档元数据标签

### 传感器文档
```yaml
document_type: sensor_doc
sensor_type: camera | lidar | radar | ultrasonic
content_type: specification | calibration | installation | maintenance
manufacturer: 厂商名称
model: 型号
version: 版本号
```

### 算法文档
```yaml
document_type: algorithm_doc
algorithm_type: perception | planning | control | slam
algorithm_category: 具体算法类别
algorithm_name: 算法名称
version: 版本号
```

### 法规文档
```yaml
document_type: regulation_doc
regulation_type: national_standard | iso_standard | test_spec | industry_standard
standard_number: 标准编号
standard_name: 标准名称
publish_date: 发布日期
version: 版本号
```

### 测试文档
```yaml
document_type: test_doc
test_type: functional | safety | boundary | performance | simulation | real_vehicle
test_category: 具体测试类别
scenario_name: 场景名称
version: 版本号
```

## 文档收集进度跟踪

使用 `sources.md` 文件跟踪收集进度：

```markdown
## 文档统计

- **传感器文档**：X / 50+ (目标)
- **算法文档**：X / 80+ (目标)
- **法规文档**：X / 30+ (目标)
- **测试文档**：X / 100+ (目标)
- **总计**：X / 260+ (目标)
```

## 注意事项

### 版权和授权
- ✅ 优先使用公开资料
- ✅ 确保有使用授权
- ❌ 不使用商业机密文档
- ❌ 不侵犯知识产权

### 数据安全
- ✅ 使用公开可获取的资料
- ✅ 遵守数据使用协议
- ❌ 不包含敏感信息
- ❌ 不泄露商业秘密

### 质量控制
- ✅ 验证文档来源可靠性
- ✅ 检查文档内容准确性
- ✅ 确保文档版本最新
- ✅ 保持文档格式统一

## 快速开始

### 第一步：创建目录结构
```bash
mkdir -p demo-data-ad/{sensors,algorithms,regulations,tests}
```

### 第二步：收集文档
按照本指南推荐的来源收集文档

### 第三步：整理文档
将文档放入对应目录并更新 `sources.md`

### 第四步：验证完整性
检查文档数量和质量

### 第五步：准备摄取
运行摄取脚本将文档导入系统

## 参考资源

### 自动驾驶资源汇总
- Awesome Autonomous Vehicles：https://github.com/manfreddiaz/awesome-autonomous-vehicles
- Awesome Self-Driving Cars：https://github.com/takeitallsource/awesome-autonomous-vehicles

### 学术资源
- arXiv 自动驾驶论文：https://arxiv.org/list/cs.RO/recent
- IEEE IV Conference：https://ieee-iv.org/
- CVPR Autonomous Driving Workshop

### 行业资源
- SAE International：https://www.sae.org/
- ISO TC 22/SC 32：道路车辆功能安全
- 中国智能网联汽车产业创新联盟

## 联系方式

如有问题或建议，请联系项目维护者。
