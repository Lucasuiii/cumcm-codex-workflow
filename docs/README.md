# 文档导航

本目录使用中文说明当前工作流及其历史设计。第一次阅读建议按以下顺序：

1. [v0.5 竞赛原生设计](v0.5-design.md)：理解为什么从 schema-heavy 调整为 evidence-focused。
2. [架构](architecture.md)：理解 orchestrator、fresh task、handoff、snapshot 和两个运行模式。
3. [工作流合同](workflow-contract.md)：查看各职责的 hard invariant、warning 和 gate 语义。
4. [项目 provenance](provenance.md)：理解哪些对象需要 digest，以及 digest 不能证明什么。
5. [v0.4→v0.5 迁移](migration-v0.4-to-v0.5.md)：迁移已有 workspace。
6. [已知限制](limitations.md)：了解 reviewer independence、后端选择和语义检查的边界。

历史设计仅用于解释演进，不代表当前规则：

- [v0.4 独立复核与读者导向论文设计](v0.4-design.md)
- [v0.3 论文质量设计](v0.3-design.md)

实际使用从仓库根目录的 [中文 README](../README.md) 开始；机器可执行规则以 `.agents/skills/cumcm-workflow/` 中的当前 Skill、schema 和 script 为准。
