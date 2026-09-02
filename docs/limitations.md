# 已知限制

- v0.5 检查通过不代表模型、统计设计或全局最优性已经被证明。
- Fresh context 能减少上下文污染，但不能证明 reviewer 真正独立；origin/reviewer task ref 仍是用户和工具记录的证据。
- 同一模型的 fresh task 仍具有相关性，只能标记为 context-separated model correlated。
- 后端选择依据声明的任务特征、已有代码和运行环境，不能自动 benchmark 所有 MATLAB toolbox 或 Python package。
- 文件与 source-tree digest 能证明身份一致，不能证明代码实现了预期数学公式。
- Targeted re-review 依赖正确的 P0 分类；reviewer 可能漏掉严重问题，也可能把普通 concern 误判为 P0。
- `cosmetic/local/semantic/claim_changing/global` 的影响分类需要判断。Hard invariant 仍会检查，以降低错误缩小范围的风险。
- 可见文本检查器能识别已知内部 ID 和常见本地 home 路径，但不能发现所有敏感字符串，也不能判断整体文风质量。
- Generic LaTeX scaffold 与具体年份提交格式无关。正式合规依赖用户提供当年规则或官方模板，并完成逐页视觉 QA。
- `paper_structure` 与通用间距能改善初始骨架，但不能预测真实长文中的 float 漂移、跨页表格、局部页面过空/过密或图中文字可读性；这些仍需下一次完整 CUMCM PDF 与质量参考进行人工逐页对比。
- v0.4 迁移保留旧产物，但不会重新认证旧 run；正式 claim 必须重新执行。
- Claim-level `model-xray` 审计仍是用户按需调用的可选增强，不是默认 gate。
