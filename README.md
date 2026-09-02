# CUMCM Codex Workflow

[English](README.en.md) | 简体中文

一个面向真实全国大学生数学建模竞赛的 Codex 工作流：contest-native、evidence-focused、low-friction。

> 当前版本：**v0.5**。检查通过只证明当前 provenance、执行记录和工作流一致，不代表数学模型必然正确。

## 1. 为什么升级到 v0.5

v0.5 保留 v0.4 最有价值的部分：官方来源保护、真实执行、精确结果定位、claim-bearing output 跟踪、最终 PDF 绑定、决策记录、可复现性和局限说明；同时把不适合比赛节奏的审计负担降下来。

- 影响真实性的 hard invariant 继续阻断。
- 模型强度问题降为 warning。
- 表达和可选优化不进入 gate。
- paper 优先通过精简 handoff 进入 fresh-context task。
- MATLAB/Python 按任务择优；同一正式任务默认只做一种正式实现。
- 已批准且未变化的阶段使用 trusted snapshot，不反复完整复核。

## 2. 架构

```text
orchestrator
  -> modeling
  -> computation（MATLAB 或 Python）
  -> independent validation
  -> fresh paper task
  -> delivery
```

这些是职责边界，不是一组细碎 Skill。主 `cumcm-workflow` Skill 负责路由；随复核包提供的 Reviewer Skill 负责 context-separated validation。

一场比赛中的推荐推进方式如下：

| 阶段 | 主要任务 | Canonical 产物 | 下一阶段如何接手 |
|---|---|---|---|
| `intake` | 保护并盘点官方题目、附件和格式文件 | `SOURCE_MANIFEST.json` | 同一 modeling task 读取官方材料 |
| `problem-analysis` | 拆解小问、事实、歧义、假设和验收目标 | `PROBLEM_FACTS.json`、`TASK_CAPABILITIES.json` | 进入模型设计 |
| `model-design` | 定义数学模型、边界、输入输出和验证计划 | `MODEL_CONTRACT.json` | 生成 modeling→computation handoff |
| `computation` | 选择 MATLAB 或 Python，正式实现并真实运行 | official run、`RESULTS_INDEX.json` | 生成 computation→validation handoff 和复核包 |
| `validation` | 独立检查 P0，记录 P1/P2 concern | review result、`CLAIM_LEDGER.json` | 生成精简 validation→paper handoff |
| `paper` | 选择论断及最佳表达方式，写作并完成 PDF QA | paper plan、LaTeX、QA sidecars、PDF | 生成 paper→delivery handoff |
| `delivery` | 对照用户提供的官方规则冻结提交版本 | PDF、可编辑 LaTeX、计算源码 | 人工确认后交付 |

原则上，modeling、computation、validation 和 paper 使用不同的 fresh task。新 task 先读 handoff，再按 handoff 指向的路径补充读取；不要先扫描整个 workspace 和旧对话。

正式跨阶段接口只有四个：

```text
modeling-computation
computation-validation
validation-paper
paper-delivery
```

## 3. 模式与证据 Gate

默认是 `working`：保护官方输入、要求引用前真实执行、检查源码/结果 provenance 与精确 locator，并禁止伪造数据或审批；探索期不因为缺少最终论文、完整 review 或可选验证而阻塞。

`finalizing` 用于冻结 claim-bearing results，并启用阶段 decision/snapshot、fresh handoff、独立复核、论文/PDF QA 和 delivery binding。

问题按后果分级：

| 等级 | 含义 | Gate |
|---|---|---|
| Hard invariant / P0 | 真实数据或计算错误、答非所问、关键 claim 无证据、stale provenance、伪造复核或最终版本不一致 | blocking |
| Warning / P1 | 假设、baseline、模型适配、敏感性或验证方面的 concern | 不阻断 |
| Suggestion / P2 | 表达、可选图表、排版或额外实验 | 不进入 gate |

`enforce` 不能靠改 state 绕过：在 finalizing 中，请求阶段及其全部上游都必须为 `passed`，且有当前有效的 accepted decision。

## 4. Fresh Task 与 Handoff

`build_handoff.py` 生成精简的 `HANDOFF.json`：包含 canonical artifact 路径/hash、upstream digest 和阶段 payload，不包含完整 logs、失败 run、debug 记录或旧 review 对话。

paper handoff 包含：

- problem/model summary；
- verified results 与 selected claims；
- limitations；
- figure/table 的初步表达计划；
- 已识别的官方格式文件。

新 task 先读 handoff。任一 canonical 上游产物变化后，handoff 会 stale，必须刷新。

推荐的任务切换示例：

```text
Modeling task：完成问题拆解和模型合同，生成 modeling-computation handoff。
Computation task：只读 handoff，选择一个后端，正式运行并生成结果。
Validation task：使用独立复核包做 full/targeted review，不继承 debug 对话。
Paper task：只读 validation-paper handoff，从 verified claims 开始组织图表和正文。
```

## 5. Independent Validation

第一次 review 是 full 且 context-separated。复核包同时绑定复制材料和当前上游产物。用户记录不同的 originating/reviewer task ref。同模型 fresh-context 仍然相关；task metadata 能增强证据，但不能从密码学上证明 reviewer 真正独立。

Verdict 支持：

- `accepted`
- `accepted_with_concerns`
- `revision_required`
- `inconclusive`

只有开放 P0 才允许 `revision_required`。full review 出现 P0 后，下一次打包默认进行 targeted re-review，覆盖全部原 P0。新增 P1/P2 不阻断；只有有明确证据的新 P0 才能新增 blocking。

## 6. MATLAB 与 Python

新项目默认：

```json
{"preferred":"matlab","fallback":"python","selection":"auto"}
```

MATLAB preference 只是同等条件下的 tie-break，不是强制。选择综合考虑数值线性代数、优化、ODE/PDE、信号处理、数据清洗、Excel/CSV、机器学习、toolbox/package、已有代码、实现复杂度和运行稳定性。

一旦选定，只正式实现并运行这一种后端。若无法可靠运行，记录原因并切换 fallback。只有用户明确要求时才建立 Python/MATLAB parity。

每个 official run 记录 selected language、rationale、runtime、dependencies/toolboxes、entry point、source-tree snapshot、command、logs、输入输出、assertions 和 `official_run: true`。正式结果只能引用成功 official run。

## 7. Paper 与 LaTeX

论文流程改为：

```text
verified results
  -> claim selection
  -> prose/equation/table/figure planning
  -> generate representations
  -> paper structure
  -> LaTeX writing
  -> rendered PDF QA
```

不设置最少图数或页数。图表偏少只会提醒重新考虑表达方式，不直接失败。v0.5 模板使用宽松的叙事单元并允许重组，避免每问机械重复“分析—假设—建模—求解”。

最终 QA 检查 caption、table、equation、页面密度、figure placement、字体/缺字、overflow、裁切、留白和跨页连续性。内部 ID、evidence state、本机路径和 workflow 术语仍是可见文本 hard error；精度过高和一句话数字过密是 warning。

Compile receipt 会把已审阅 PDF 绑定到实际编译使用的完整 editable LaTeX source-tree snapshot。

## 8. 初始化、检查与迁移

### 三步开始

1. 在 Codex 对话中提供官方本地路径：

```text
使用 $cumcm-workflow，从 /absolute/path/to/2026B 初始化国赛项目。
```

2. 在 `working` 模式完成建模、后端选择和正式计算；每次跨职责前生成 handoff。

3. 结果稳定后切到 `finalizing`，依次完成 validation、fresh paper task、PDF QA 和 delivery。

### 维护命令

```bash
python3 .agents/skills/cumcm-workflow/scripts/init_project.py \
  --project /path/to/new-project --project-id CUMCM-2026-B \
  --official /path/to/official-files

python3 .agents/skills/cumcm-workflow/scripts/cumcm_check.py \
  --project /path/to/project --stage validation \
  --profile strict --gate-mode enforce

python3 .agents/skills/cumcm-workflow/scripts/set_mode.py \
  --project /path/to/project --mode finalizing

python3 .agents/skills/cumcm-workflow/scripts/build_handoff.py \
  --project /path/to/project --transition validation-paper

python3 .agents/skills/cumcm-workflow/scripts/build_independent_review_package.py \
  --project /path/to/project --review-mode auto

python3 .agents/skills/cumcm-workflow/scripts/migrate_v04_to_v05.py \
  --source /path/to/v04-workspace --target /path/to/v05-workspace
```

迁移只复制到新目录，不修改 v0.4 来源；新工作区从 working 开始，旧 run 会标记为 non-official，必须用择优后端重新正式执行后才能 finalizing。

局部重验可增加 `--changed <path>` 和 `--impact cosmetic|local|semantic|claim_changing|global`。

## 9. Hard Invariant 与 Provenance

下列问题继续 blocking：

- 官方输入被修改或 identity 不一致；
- 把模拟数据冒充观测数据；
- claim-bearing computation 没有成功 official run；
- code source snapshot、formal input 或 claim-bearing output 漂移；
- result locator 错误或索引值与输出不一致；
- 独立复核包或 stage handoff stale；
- 伪造人工审批或独立复核；
- validation/paper 存在开放 P0；
- 最终 PDF 不可读或版本不一致；
- PDF 未绑定 approved QA 与 editable source；
- PDF/LaTeX/计算程序三类交付不完整。

accepted decision 会自动生成轻量 stage snapshot。关键产物未变时 snapshot 可 trusted；一旦变化，该阶段及下游 trust 失效。Hard invariant 仍会检查。

## 10. 仓库与开发

```text
.agents/skills/cumcm-workflow/
├── SKILL.md
├── references/
├── schemas/
├── scripts/
└── assets/
docs/
├── README.md                    # 中文文档导航
├── architecture.md              # 架构和职责边界
├── workflow-contract.md         # 工作流状态与 gate 合同
├── provenance.md                # 证据与摘要边界
├── migration-v0.4-to-v0.5.md   # 迁移说明
├── v0.5-design.md               # 当前设计
└── limitations.md               # 已知限制
examples/
tests/
.github/workflows/ci.yml
```

开发验收：

```bash
python3 -m pip install -r requirements-ci.txt
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m compileall -q .agents/skills/cumcm-workflow/scripts tests
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/cumcm-workflow
```

CI 使用固定依赖，在 Python 3.10 和 3.13 运行。真实论文发布仍需要 XeLaTeX 编译和逐页渲染检查。

## 11. 局限与许可

fresh context 能降低上下文污染，但不能保证 reviewer 正确或真正独立。digest 证明 artifact identity，不证明数学有效性。后端选择是确定性指导，不是所有 toolbox/package 的完整 benchmark。视觉与语义质量仍需要具体问题判断。

进一步阅读从 [中文文档导航](docs/README.md) 开始，也可直接查看[架构](docs/architecture.md)、[工作流合同](docs/workflow-contract.md)、[provenance](docs/provenance.md)、[v0.4→v0.5 迁移](docs/migration-v0.4-to-v0.5.md)和[已知限制](docs/limitations.md)。历史设计见 [v0.4](docs/v0.4-design.md) 与 [v0.3](docs/v0.3-design.md)；当前设计见 [v0.5](docs/v0.5-design.md)。

本仓库采用 [MIT License](LICENSE)。
