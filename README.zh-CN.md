# CUMCM Codex Workflow

[English](README.md) | 简体中文

一个面向全国大学生数学建模竞赛（CUMCM）的 Codex 原生工作流，强调证据边界、可复现计算和完整交付。

> 当前版本：**v0.4**。本 Skill 仅接受 v0.4 项目合同。通过检查只代表工作流内部一致，不代表数学模型或论文必然正确。

## v0.4 要解决什么

- 在一次 Codex 对话中，从用户提供的官方文件直接建立完整竞赛工作区。
- 让官方来源、建模决策、实际运行的计算、论文主张、图件和交付产物保持可追溯。
- 在重要决策处停下来等待人工确认，不静默选择关键解释，也不自行批准自己的工作。
- 在 validation 前，把计算证据交给用户选择的独立任务进行复核。
- 生成面向评委阅读的 LaTeX/PDF 论文，同时把内部 ID、证据状态、本地路径和工作流术语留在 sidecar 文件中。
- 将已审阅 PDF、可编辑 LaTeX 源码和计算源码作为三个独立交付项。
- 依靠磁盘上的项目文件恢复进度，而不是依赖对话历史。

## 工作流

```text
官方文件
   |
   v
intake -> problem analysis -> model design -> computation
                                                   |
                                                   v
                                      independent review package
                                                   |
                                        用户转交给独立复核者
                                                   |
                                                   v
validation -> paper -> delivery -> 用户按需发起最终审计
```

项目仍由七个阶段组成：`intake`、`problem-analysis`、`model-design`、`computation`、`validation`、`paper` 和 `delivery`。独立复核是 computation 与 validation 之间的阻断门禁，不是一个可以由原对话自行通过的第八阶段。

| 阶段 | 主要产物 | 人工门禁 |
|---|---|---|
| Intake | 官方输入、来源清单和项目状态 | 确认官方输入集合完整 |
| Problem analysis | 事实、题意解释、假设和能力需求 | 批准题意解释与问题覆盖 |
| Model design | 模型合同、备选方案、依赖关系和主张范围 | 选择模型并确认其适用边界 |
| Computation | 可运行代码、保留的运行记录、日志和索引结果 | 批准进入复核的实际计算证据 |
| Independent review gate | 隐去原结论的复核包和结构化复核结果 | 用户选择独立的人或模型；原对话自审会被拒绝 |
| Validation | 证据状态、一致性检查、局限性和主张台账 | 确认现有证据实际支持哪些结论 |
| Paper | 模块化 LaTeX、追溯 sidecar、内容/版式/可见文本检查 | 批准精确版本的论文并关闭严重问题 |
| Delivery | 编译凭据、最终 PDF、可编辑 LaTeX、计算源码和清单 | 确认官方格式合规性与最终交付包 |

如果发现冲突，流程回退到最早负责该问题的阶段。下游文件会保留，但相关阶段必须在修正并重新审阅后才能通过。

## 在 Codex 对话中开始

用 Codex 打开本仓库，把官方题目、附件和当年规则放在本机可访问的位置，然后直接提供路径：

```text
使用 $cumcm-workflow 初始化国赛项目，官方题目和附件在 /absolute/path/to/2026B。
```

当请求明确属于国赛项目时，可以不显式写 `$cumcm-workflow`。Codex 会：

1. 只读检查用户提供的文件或目录；
2. 推断 `CUMCM-2026-B` 这样的稳定项目 ID；
3. 在用户没有指定目标时选择安全的同级工作区；
4. 使用绝对路径运行初始化器；
5. 报告新建工作区，并停在 intake 人工审查门禁。

只有在来源不存在、年份或题号仍然无法判断、或者目标位置会覆盖现有工作时，Codex 才会询问。初始化过程只复制官方输入，不会编辑或删除原文件，也不会虚构事实、模型、结果、复核或批准。

维护者和自动化流程也可以直接调用底层初始化器：

```bash
python3 .agents/skills/cumcm-workflow/scripts/init_project.py \
  --project /path/to/new-project \
  --project-id CUMCM-2026-B \
  --official /path/to/official-files
```

## validation 前的独立复核

computation 完成后，Skill 会生成 `validation/independent-review-package/`。其中包含必要的官方输入、题意与模型合同、计算入口、运行记录、实际输出、复核请求以及专用 Reviewer Skill。原任务在此停止，由用户把复核包交给新的任务或人类复核者。

原始复核意见会被逐字保留，`INDEPENDENT_REVIEW_RESULT.json` 则记录复核者身份、范围、发现和结论。在原对话内完成的复核不能通过门禁；使用同一模型的新任务会标记为 correlated，而不是完全 independent。复核通过是一项证据，不是数学正确性的证明。

## 面向评委的论文与交付

内置的 `cumcm-contest-ctex` 模板采用模块化、按问题组织的结构，默认不生成目录。每一问都应形成连贯论证，包括任务解释、机理、模型、算法、结果、验证与局限。

内部追溯信息保存在 `PAPER_TRACEABILITY.json` 等 sidecar 文件中。可见文本检查会阻止内部 ID、证据状态枚举、本地路径和门禁术语进入最终 PDF。小数精度过高或一句话堆叠过多数字时，必须修改，或提供面向读者的明确保留理由。

delivery 必须包含三个可以分别定位的角色：

1. 经审阅的精确版本最终 PDF；
2. 可编辑 LaTeX 源码，包括入口文件和必要资产；
3. 计算源码，包括入口和复现说明。

内置模板保持投稿中立。最终合规检查必须依据用户提供的当年官方规则或模板。缺少官方材料时，delivery 会被阻断；这不构成自动联网搜索或代替用户提交的授权。

## 校验与门禁模式

在仓库根目录运行：

```bash
python3 .agents/skills/cumcm-workflow/scripts/cumcm_check.py \
  --project /path/to/project \
  --stage validation \
  --profile strict \
  --gate-mode enforce
```

报告会写入 `.cumcm/validation-report.json`。

- `strict` 是默认配置。`sprint` 可以减少探索和润色，但不会降低来源、执行、一致性、证据和交付检查。
- `preflight` 用来区分“自动检查完成，等待人工决定”和“构建失败”。只有剩余问题全部属于人工决定时，才可以以 `gate_status=awaiting_review` 返回零退出码。
- 一个阶段只有通过 `enforce` 才能视为正式通过。

两种模式都不是数学正确性、统计有效性或全局最优性的证书。

## 收窄后的 SHA-256 政策

只有确实需要逐字节确认身份时，SHA-256 才作为后台机制使用：

- 用户提供的官方来源；
- 正式计算输入与承载论文主张的输出；
- 被明确人工批准覆盖的少量阶段合同；
- 论文检查和交付实际审阅的最终 PDF。

普通代码、LaTeX、文档、编辑阶段图件、日志、缓存、临时文件和辅助文件不强制摘要。决策事件保持追加式记录，但不再形成 hash 链。复核者审查的是产物及摘要，而不是 64 字符的摘要字符串。

## 仓库结构

```text
.agents/skills/cumcm-workflow/
├── SKILL.md                 # 工作流路由与核心不变量
├── agents/openai.yaml       # Codex 界面信息与调用策略
├── references/              # 各阶段指南和证据合同
├── schemas/                 # v0.4 机器可读合同
├── scripts/                 # 初始化、校验、复核打包和论文检查
└── assets/
    ├── independent-review/  # Reviewer Skill 与复核请求模板
    └── latex-template/      # 模块化 CTeX 论文模板
docs/                        # 架构、工作流合同与 v0.4 设计
examples/                    # 不含官方竞赛资产的回归合同
tests/                       # 合同与行为测试
```

官方赛题、私有试跑资产、生成的工作区和参赛提交文件都不应进入本仓库。

## 开发验收

环境要求：Python 3.10+、`jsonschema>=4.18`。

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/cumcm-workflow
```

第二条命令在环境可用时调用 Codex 内置 Skill 校验器。真正发布论文前仍需进行 XeLaTeX 编译和逐页渲染检查；单元测试通过不等于视觉质量检查通过。

## 文档

- [v0.4 设计](docs/v0.4-design.md)
- [工作流合同](docs/workflow-contract.md)
- [架构](docs/architecture.md)
- [局限](docs/limitations.md)
- [来源说明](docs/provenance.md)
- [v0.3 历史设计](docs/v0.3-design.md)

最终 `model-xray` 审计仍是由用户按需调用的可选环节，不会自动执行。

## 安全边界与许可

- 不得为了让某个方法看起来更好而虚构经验数据。
- 没有证书和明确适用范围时，不得把近似解或受限策略类结果称为全局最优。
- 不得在论文中写入无法追溯到实际运行输出的主张。
- 不得把 Schema、关键词检查、求解器成功标志或复核通过当作数学正确性的证明。

本仓库是面向可复现 CUMCM 工作的独立设计与实现，采用 [MIT License](LICENSE) 开源。
