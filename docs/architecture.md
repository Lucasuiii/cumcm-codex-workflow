# 架构

v0.5 把可恢复状态保存在 workspace 文件中，同时把“编排任务”与“具体工作产物”分离。目标不是增加更多流程角色，而是让建模、计算、复核和论文写作能够在 fresh task 中可靠接手。

```text
orchestrator
  -> modeling artifacts
  -> modeling-computation handoff
  -> 单一选定计算后端 + official run
  -> computation-validation handoff + review package
  -> 有边界的 independent validation
  -> validation-paper handoff
  -> fresh paper task
  -> paper-delivery handoff
  -> compile receipt + 三类交付物
```

## 职责与状态机

顶层状态机仍保留七个阶段，以兼容现有 workspace：

```text
intake -> problem-analysis -> model-design -> computation
       -> validation -> paper -> delivery
```

实际职责归并为 orchestrator、modeling、computation、validation、paper 和 delivery。Independent review 属于 validation gate，不是一个可以由主任务自行批准的新阶段。

Orchestrator 负责识别当前阶段、选择下一职责、检查 handoff freshness 和保存决策；它不应同时承担长周期 debug、独立复核和论文写作。每个 fresh task 先读取对应 handoff，再按需打开少量 canonical artifact。

## 两种运行模式

- `working`：维护官方输入保护、真实执行、结果定位和关键 provenance；允许下游产物暂时不完整。
- `finalizing`：要求目标阶段及上游阶段均通过，并具有当前 accepted decision、stage snapshot、fresh handoff、独立复核和精确的最终版本绑定。

模式控制检查强度，`strict`/`sprint` 仍是兼容的检查 profile。修改 state 字段不能代替人工 decision。

## Snapshot 与 Handoff

Accepted decision 的 artifact scope 是 stage snapshot 的来源。Snapshot 由脚本自动生成，不要求人工重复填写；`revision_requested` 会使对应 snapshot 失效。

Handoff 复用少量阶段产物并计算 upstream digest，因此不再建立另一套人工维护的大型 schema。普通 handoff 只保存路径、角色、摘要和 digest，不复制完整历史。Independent review package 是例外：reviewer 可能在另一个 task 或 workspace 工作，所以复核包只复制正式结果对应的 canonical evidence，并单独绑定 package/upstream digest；失败/探索 run、stdout/stderr 和 debug history 不参与打包或 freshness。Targeted review 后，paper brief 只沿结构化 review lineage 合并最新 finding 状态，以保留有效 P1 而不复制旧 review 对话。

`workflow_checks.py` 始终重新检查成本较低的 hard invariant。Trusted snapshot 只减少重复的人工/语义复核，不跳过官方来源、official run、result locator、review package、handoff 和最终 PDF 身份检查。

## 计算与论文绑定

正式计算把一个选定的 MATLAB/Python 实现绑定到 source-tree snapshot、成功命令、formal inputs、claim-bearing outputs、日志、断言和结果索引。同一正式任务默认不建立双语言 parity 实现。Computation handoff、独立复核包和 paper→delivery 通过同一 `RESULTS_INDEX → official run → source snapshot` resolver 解释正式源码。

最终编译使用相同原则：compile receipt 把最终 PDF 绑定到实际参与编译的 editable LaTeX source-tree snapshot，以及已经批准的 paper QA 版本；paper→delivery handoff 同时携带该绑定、正式计算源码指针和官方材料角色。
