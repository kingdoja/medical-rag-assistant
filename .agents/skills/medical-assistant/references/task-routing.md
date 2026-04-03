# Task Routing

本文件将常见任务固定路由到对应 spec，避免 agent 在执行时自行猜测。

## 1. 产品定义类

适用任务：

- 改产品定位
- 写产品说明
- 同步求职版项目描述
- 调整目标用户与边界

读取顺序：

1. `PRODUCT_BRIEF.md`
2. `PRD.md`

## 2. 开发规范类

适用任务：

- 制定开发流程
- 校验实现是否越界
- 约束测试、发布、命名、文档更新

读取顺序：

1. `DEVELOPMENT_SPEC.md`
2. `PRD.md`

## 3. Demo 数据类

适用任务：

- 准备公开数据
- 校验去敏
- 审核命名规则
- 判断是否允许入库

读取顺序：

1. `DEMO_DATA_CHECKLIST.md`
2. `DEMO_DATA_SOURCES.md`
3. `PRD.md`

## 4. 演示回归类

适用任务：

- 准备标准演示问题
- 检查引用回答
- 校验拒答边界
- 判断 demo 是否可展示

读取顺序：

1. `DEMO_SCENARIOS.md`
2. `DEMO_SCENARIO_MAPPING.md`
3. `PRD.md`
4. `DEVELOPMENT_SPEC.md`

## 5. 展示材料同步类

适用任务：

- 输出求职版材料
- 输出 GitHub 展示内容
- 生成面试讲稿

读取顺序：

1. `PRODUCT_BRIEF.md`
2. `PRD.md`
3. 展示目录现有文件

## Output Rule

- 先保证真源一致
- 再同步展示层
- 禁止展示层先行、真源补录


