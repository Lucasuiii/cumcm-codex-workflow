# 工作流合同

| 职责 | Hard invariant（阻断） | Non-blocking concern |
|---|---|---|
| Intake | 官方输入保持不变且身份正确 | 可选来源元数据的完善 |
| Modeling | 每个官方小问都有明确输出负责人；模型范围不与题意冲突 | 备选模型广度、更强或更弱的假设比较 |
| Computation | 一个成功 official backend、当前 source snapshot、formal input/output 和精确 result locator | 更多断言、诊断或性能优化 |
| Validation | Fresh package、没有开放 P0、claim 有证据和适用范围 | P1 验证/敏感性/泛化 concern；P2 suggestion |
| Paper | 回答每个小问；不发明结果、不泄露内部元数据；没有开放 paper P0 | 图表密度、章节强度和可选润色 |
| Delivery | 精确的 reviewed PDF、当前 editable source snapshot、成功编译、官方格式审查和三类交付角色 | 非关键展示优化 |

## Gate 语义

在 `working` 模式中，下游 artifact 不完整时仍可继续探索。`finalizing` 的 `enforce` 要求目标阶段及全部上游阶段为 `passed`，并由当前 accepted decision 和派生 snapshot 覆盖。编辑 state 不能代替 decision。

自动错误分为两类：

- hard invariant：在 working/finalizing 中都不能降级；
- finalizing completeness：working 中可以暂缺，进入 finalizing 后必须满足。

Warning 和 suggestion 会进入报告，但不改变通过状态，除非新的证据表明它实际上属于 P0。

## Review 语义

Independent review 从 full pass 开始。如果返回开放 P0，下一轮默认 targeted re-review。`accepted_with_concerns` 足以进入 paper，因为开放 P1 只说明仍有改进空间，并未证明结果为假。

同一上下文不能满足 independent review。Same-model fresh task 仍标记为 correlated；different model 或 human 也只表示 independence evidence 更强，不构成数学证明。

## 变化与重验范围

Change impact 控制 revalidation scope。Cosmetic/local change 不触发 full-workspace review；semantic、claim-changing 和 global change 只扩展到真正受影响的下游阶段。

Snapshot trusted 不会跳过官方输入、official run、result/output、review package、handoff 或 final PDF 的 identity 检查。
