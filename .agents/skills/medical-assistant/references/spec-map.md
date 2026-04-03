# Spec Map

本文件定义“任务类型 -> 必读文件 -> 验收依据 -> 必回写文件”的映射，供 agent / skill 稳定消费。

| 任务类型 | 必读文件 | 验收依据 | 必回写文件 |
|---|---|---|---|
| 产品定义 | `PRODUCT_BRIEF.md`, `PRD.md` | 定位、目标用户、边界、核心功能一致 | `EXECUTION_STATUS.yaml`, `CHANGELOG.md` |
| 开发规范 | `DEVELOPMENT_SPEC.md` | 范围、数据规范、测试规范、发布规范一致 | `EXECUTION_STATUS.yaml`, `CHANGELOG.md` |
| demo 数据准备 | `DEMO_DATA_CHECKLIST.md`, `DEMO_DATA_SOURCES.md` | 来源合法、命名规范、去敏通过、禁止项未触发 | `EXECUTION_STATUS.yaml`, `CHANGELOG.md` |
| 演示与回归 | `DEMO_SCENARIOS.md`, `DEMO_SCENARIO_MAPPING.md` | 预期行为、引用要求、拒答边界、失败判定符合 | `EXECUTION_STATUS.yaml`, `CHANGELOG.md` |
| 展示材料同步 | `PRODUCT_BRIEF.md`, `PRD.md` | 展示材料不与真源冲突，表述适合求职输出 | `EXECUTION_STATUS.yaml`, `CHANGELOG.md` |
| 状态回写 | `EXECUTION_STATUS.yaml`, `CHANGELOG.md` | 状态字段完整、动作记录可追溯 | `EXECUTION_STATUS.yaml`, `CHANGELOG.md` |

## Notes

- 展示目录不是规范真源，只能作为导出层。
- 只有新增、删除或重命名 spec 文件时，才需要额外更新 `SPEC_MANIFEST.yaml`。
- 任何医疗边界判断，以 `PRD.md` 和 `PRODUCT_BRIEF.md` 为准。


