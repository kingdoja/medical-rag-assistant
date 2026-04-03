# Demo Data Sources

## 目标

给出 `v0.1` 首轮医疗 demo 数据包的真实公开来源清单，确保后续下载、导入、演示和回归都能基于可说明来源的正式资料开展。

## 选材原则

- 优先官方机构、国际组织或设备厂商官网
- 优先 PDF 或可稳定导出的正式资料
- 优先能同时支撑检索、引用回答、边界说明和演示效果的文档
- 优先覆盖病理 / 检验科近邻场景，而不是追求“完全真实医院生产资料”

## 现实约束

公开可用、可稳定下载、又足够贴近病理 / 检验科内部 SOP 的中文资料并不多。

因此 `v0.1` 的首轮 demo 数据包采用“近邻场景”策略：

- 用 WHO 类实验室质量与样本管理资料支撑规范、质控、流程问答
- 用 Leica / Roche 类设备资料支撑设备操作、异常处理、图文检索
- 用 WHO 培训工具包支撑新人培训、文档管理、质量管理问答

等 `v0.1` 跑通后，再逐步替换为更贴近病理 / 检验科语境的公开中文资料或去敏内部资料。

## 推荐下载顺序

1. 先下 2 份规范 / 指南
2. 再下 2 份 SOP / 流程相关资料
3. 再下 1 到 2 份设备说明书
4. 最后补 1 到 2 份培训资料

## v0.1 推荐来源清单

| 建议文件名 | 类型 | 官方来源 | 官方链接 | 推荐级别 | 主要用途 | 映射场景 |
|---|---|---|---|---|---|---|
| `guideline_lab_quality_management_system_who_2011.pdf` | guideline | WHO IRIS | [Laboratory quality management system: handbook](https://iris.who.int/handle/10665/44665) | P0 | 质量管理、文件管理、规范引用、边界说明 | S2, S3, S8, S10, S12 |
| `guideline_transport_infectious_substances_who_2024.pdf` | guideline | WHO IRIS | [Guidance on regulations for the transport of infectious substances, 2023-2024](https://iris.who.int/handle/10665/376214) | P0 | 标本运输、包装、标签、流程规范 | S1, S2, S8, S9 |
| `sop_sample_management_who_toolkit_module5.pdf` | sop | WHO HSLP Toolkit | [Laboratory Quality Management System Training Toolkit](https://extranet.who.int/hslp/content/LQMS-training-toolkit) | P0 | 样本管理、接收、处理、拒收规则 | S1, S6, S9, S10 |
| `sop_documents_records_who_toolkit_module16.pdf` | sop | WHO HSLP Toolkit | [Laboratory Quality Management System Training Toolkit](https://extranet.who.int/hslp/content/LQMS-training-toolkit) | P0 | SOP 结构、文档与记录管理 | S1, S8, S10, S12 |
| `training_quality_control_who_toolkit_module7.pdf` | training | WHO HSLP Toolkit | [Laboratory Quality Management System Training Toolkit](https://extranet.who.int/hslp/content/LQMS-training-toolkit) | P0 | 质量控制、复核、培训问答 | S2, S6, S10 |
| `training_equipment_management_who_toolkit_module3.pdf` | training | WHO HSLP Toolkit | [Laboratory Quality Management System Training Toolkit](https://extranet.who.int/hslp/content/LQMS-training-toolkit) | P1 | 设备管理、维护、培训场景 | S4, S6, S11 |
| `manual_histocore_peloris3_user_manual_zh-cn.pdf` | manual | Leica Biosystems | [HistoCore PELORIS 3 product page](https://www.leicabiosystems.com/us/histology-equipment/tissue-processors/histocore-peloris-3/) | P0 | 病理组织处理设备、报警、操作流程、图文检索 | S4, S5, S11, S12 |
| `manual_aperio_gt450_users_guide_en.pdf` | manual | Leica Biosystems | [Aperio GT 450 resource page](https://www.leicabiosystems.com/us/digital-pathology/scan/aperio-gt-450-ruo/) | P1 | 数字病理扫描、图文说明、界面与流程展示 | S5, S10, S12 |
| `manual_cobas_liat_system_user_guide_v11.pdf` | manual | Roche Diagnostics | [cobas Liat System User Guide](https://diagnostics.roche.com/content/dam/diagnostics/us/en/products/c/cobas-liat-support/cobas-liat-system-user-guide-sw-v3.4-v11.pdf) | P1 | 检验设备操作、维护、故障与限制说明 | S4, S11, S12 |

## 使用说明

### WHO HSLP Toolkit

该页面包含多个模块的下载入口。`v0.1` 首轮建议优先下载以下模块的 `Content sheet` PDF：

- Module 3: Equipment
- Module 5: Sample management
- Module 7: Process control - Quantitative quality control
- Module 16: Documents and records

### Leica Biosystems

优先下载：

- `HistoCore PELORIS 3 用户手册 ZH-CN`
- `Aperio GT 450 User's Guide - English`

如果需要更适合演示的图文资料，也可以补充对应产品 brochure。

### Roche Diagnostics

优先下载：

- `cobas Liat System User Guide`

适合用于展示设备操作、维护、报警与限制说明。

## 推荐最小下载组合

如果只想先跑一个最小可展示组合，建议先下载这 6 份：

1. `guideline_lab_quality_management_system_who_2011.pdf`
2. `guideline_transport_infectious_substances_who_2024.pdf`
3. `sop_sample_management_who_toolkit_module5.pdf`
4. `sop_documents_records_who_toolkit_module16.pdf`
5. `training_quality_control_who_toolkit_module7.pdf`
6. `manual_histocore_peloris3_user_manual_zh-cn.pdf`

这 6 份足以支撑 `v0.1` 的首轮问答与演示。

## 下载后必须登记

每下载一份资料，都要同步记录到 `demo-data/sources.md`，最少包含：

- 建议文件名
- 实际文件名
- 来源机构
- 来源链接
- 版本 / 年份
- 下载日期
- 数据类型
- 对应场景
- 备注
