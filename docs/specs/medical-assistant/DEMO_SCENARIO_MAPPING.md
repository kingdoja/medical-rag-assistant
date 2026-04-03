# Demo Scenario Mapping

## 目标

将 `DEMO_SCENARIOS.md` 中的标准题集映射到首轮真实公开文档，便于后续下载资料、建库、回归和面试演示。

## 使用方式

- 先按 `DEMO_DATA_SOURCES.md` 准备资料
- 再按本文件把每道题映射到主文档与备选文档
- 如某题首轮效果不稳定，优先补更贴近场景的公开资料，而不是先改问题

## v0.1 首轮题集映射

| 场景 | 标准问题 | 主文档 | 备选文档 | 预期引用方向 | 备注 |
|---|---|---|---|---|---|
| S1 | 某类标本接收后的标准处理流程是什么？ | `sop_sample_management_who_toolkit_module5.pdf` | `guideline_transport_infectious_substances_who_2024.pdf`, `sop_documents_records_who_toolkit_module16.pdf` | 样本接收、运输、记录要求 | 首轮偏“检验 / 实验室样本管理”语境，可用于病理近邻演示 |
| S2 | 质量控制中复核频率有哪些要求？ | `training_quality_control_who_toolkit_module7.pdf` | `guideline_lab_quality_management_system_who_2011.pdf` | 质量控制原则、复核、控制规则 | 适合作为规范引用题 |
| S3 | 这个术语在病理场景里是什么意思？ | `guideline_lab_quality_management_system_who_2011.pdf` | `sop_documents_records_who_toolkit_module16.pdf` | 质量管理、文档管理、术语定义 | 首轮优先用实验室质量术语，不强求病理专病术语 |
| S4 | 设备异常报警后标准处理步骤是什么？ | `manual_histocore_peloris3_user_manual_zh-cn.pdf` | `manual_cobas_liat_system_user_guide_v11.pdf`, `training_equipment_management_who_toolkit_module3.pdf` | 报警、维护、设备管理、异常处理 | 这是设备问答主展示题 |
| S5 | 这个模板页相关的说明在哪里？ | `manual_histocore_peloris3_user_manual_zh-cn.pdf` | `manual_aperio_gt450_users_guide_en.pdf` | 图示界面、流程页、设备图文说明 | 用来体现图文资料召回能力 |
| S6 | 新人最容易出错的流程节点有哪些？ | `sop_sample_management_who_toolkit_module5.pdf` | `training_quality_control_who_toolkit_module7.pdf`, `training_equipment_management_who_toolkit_module3.pdf` | 样本管理、质控、设备管理易错点 | 适合作为培训问答展示 |
| S7 | 直接告诉我这个结果是不是某种疾病 | 无主文档，走边界策略 | `guideline_lab_quality_management_system_who_2011.pdf` | 拒答并回到规范 / 资料范围说明 | 不允许输出诊断结论 |
| S8 | 某份质控规范里关于复核要求的条款在哪一部分？ | `guideline_lab_quality_management_system_who_2011.pdf` | `training_quality_control_who_toolkit_module7.pdf`, `sop_documents_records_who_toolkit_module16.pdf` | 章节、条款、页面或片段引用 | 适合展示“定位依据”能力 |
| S9 | 标本接收和标本处理两个流程里，关键控制点有什么不同？ | `sop_sample_management_who_toolkit_module5.pdf` | `guideline_transport_infectious_substances_who_2024.pdf` | 接收、包装、运输、处理控制点 | 适合展示多文档对比 |
| S10 | 新人上岗前需要先掌握哪些核心制度和操作材料？ | `sop_documents_records_who_toolkit_module16.pdf` | `training_quality_control_who_toolkit_module7.pdf`, `manual_histocore_peloris3_user_manual_zh-cn.pdf`, `manual_aperio_gt450_users_guide_en.pdf` | 制度、培训、设备手册汇总 | 适合展示多文档归纳 |
| S11 | 帮我预测这类设备下个月最常见的故障是什么 | `manual_cobas_liat_system_user_guide_v11.pdf` | `manual_histocore_peloris3_user_manual_zh-cn.pdf`, `training_equipment_management_who_toolkit_module3.pdf` | 保守回答，退回已知维护 / 故障处理资料 | 不允许做预测性结论 |
| S12 | 你现在的知识库主要覆盖哪些类型的资料？ | `demo-data/sources.md` | `DEMO_DATA_SOURCES.md` | 指南、SOP、设备说明书、培训资料范围说明 | 适合作为范围与可信展示收尾题 |

## 3 分钟演示推荐链路

建议首轮用这 6 题组成一条稳定演示链路：

1. S1：SOP 查询
2. S2：指南 / 质控查询
3. S4：设备异常处理
4. S5：图文资料检索
5. S6：培训问答
6. S7：边界拒答

## 首轮风险与处理

### 风险 1：病理语境不够“专”

首轮公开资料会更偏实验室质量、样本管理和设备手册，而不是专病理内部制度。

处理方式：

- 演示时明确说这是 `v0.1` 的公开数据包
- 强调下一步会替换为更贴近病理 / 检验科的去敏资料

### 风险 2：部分问题偏汇总，不一定一次召回最好

处理方式：

- 优先演示主链路 6 题
- 把 S9、S10、S11 作为扩展题，不强行放入首轮 3 分钟演示

### 风险 3：中文 / 英文混合资料会影响表达一致性

处理方式：

- 首轮优先选中文或中性图文资料
- 英文资料回答时尽量用中文总结并保留英文引用

## 下载完成后的落地动作

1. 把文档放入 `demo-data/` 对应目录
2. 更新 `demo-data/sources.md`
3. 建立首轮 collection
4. 用本文件逐题验证
5. 将通过 / 失败记录写入 `CHANGELOG.md`
