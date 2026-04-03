# Medical Assistant Specs

本目录是 `PathoMind 医疗知识与质控助手` 的**工程真源**。

## 真源原则

- 与该项目相关的产品定义、开发规范、演示规则、agent 执行协议，以本目录为准。
- `简历/项目改造方案-医疗知识助手/` 仅保留求职展示材料。
- 当展示材料与本目录内容冲突时，以本目录为准。

## 阅读顺序

1. `PRODUCT_BRIEF.md`
2. `PRD.md`
3. `DEVELOPMENT_SPEC.md`
4. `DEMO_DATA_CHECKLIST.md`
5. `DEMO_DATA_SOURCES.md`
6. `DEMO_SCENARIOS.md`
7. `DEMO_SCENARIO_MAPPING.md`
8. `AGENT_RUNBOOK.md`
9. `SPEC_MANIFEST.yaml`
10. `EXECUTION_STATUS.yaml`
11. `CHANGELOG.md`

## 文档职责

- `PRODUCT_BRIEF.md`: 产品定位、用户、场景、求职叙事
- `PRD.md`: 功能范围、验收标准、版本边界
- `DEVELOPMENT_SPEC.md`: 开发、测试、发布规范
- `DEMO_DATA_CHECKLIST.md`: demo 数据准备规范
- `DEMO_DATA_SOURCES.md`: demo 数据真实公开来源清单
- `DEMO_SCENARIOS.md`: 标准演示题集与回归场景
- `DEMO_SCENARIO_MAPPING.md`: 标准题集到真实文档的首轮映射
- `AGENT_RUNBOOK.md`: agent 执行协议
- `SPEC_MANIFEST.yaml`: 机器可读索引
- `EXECUTION_STATUS.yaml`: 当前状态真源
- `CHANGELOG.md`: 历史变更记录

## 更新协议

- 任何重要变更都必须同步更新：
  - `EXECUTION_STATUS.yaml`
  - `CHANGELOG.md`
- 新增 spec 文件时，必须同时更新 `SPEC_MANIFEST.yaml`
- 版本号格式统一为 `v主版本.次版本`
