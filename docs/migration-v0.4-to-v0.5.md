# 将 v0.4 workspace 迁移到 v0.5

迁移必须使用新的目标目录：

```bash
python3 .agents/skills/cumcm-workflow/scripts/migrate_v04_to_v05.py \
  --source /path/to/v04-workspace \
  --target /path/to/v05-workspace
```

迁移脚本不会修改来源目录。它会：

- 复制可用产物，并从副本中排除 cache/temp 文件；
- 把兼容的 contract envelope 和 state 升级到 v0.5；
- 将新 workspace 设置为 `working`；
- 在存在旧 review 时转换 verdict/severity 词汇；
- 尽可能派生兼容的 claim selection、representation plan 和 paper structure；
- 在可能时绑定已有 editable LaTeX source；
- 把所有迁移 run 标记为 `official_run: false`。

最后一条是有意的安全边界。v0.4 不要求 v0.5 的 selected-backend source snapshot，因此迁移不能诚实地声称旧 run 与当前源码绑定。

迁移完成后应：

1. 根据任务选择 MATLAB 或 Python；
2. 重新执行 claim-bearing computation；
3. 重建 `RESULTS_INDEX.json`、handoff 和 independent review package；
4. 完成当前 review 后再进入 `finalizing`。

如果迁移后的旧合同不满足新 schema，不要伪造缺失字段。保留原始证据，在 working 模式中重新生成受影响产物。
