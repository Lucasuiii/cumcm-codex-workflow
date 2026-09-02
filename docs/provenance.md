# 项目 Provenance

本仓库面向可复现 CUMCM 工作独立设计和编写。

项目围绕以下机制构建：版本化 contract、跨产物稳定 ID、精确 result locator、选定源码 snapshot、精简 handoff/review digest、与具体版本绑定的论文审查、追加式人工 decision，以及适合公开仓库的合成回归用例。

SHA-256 只用于字节身份确实会影响证据的对象：官方来源、formal input、claim-bearing output、selected source tree、stage snapshot/handoff、review package 和最终批准 PDF。Digest 证明身份，不证明数学正确性。

Independent review package 的 package/upstream digest 只覆盖正式结果引用的 canonical evidence 与复核说明；失败/探索 run、stdout/stderr、旧实验和 debug history 默认不进入包，也不扩大 freshness 范围。

Computation→validation handoff、independent review package 与 paper→delivery handoff 共用 `canonical_evidence.py` 解析 `RESULTS_INDEX → official run → source snapshot`。这样不同接口不会一个忽略坏引用、另一个才报错。Paper→delivery 只提供 canonical pointers 和 digest，不复制完整 runs。

如果引入公开上游软件，在合并前记录其仓库 URL、精确 revision、许可证、实际使用文件和本项目修改。不要把第三方设计、模板或代码描述为本仓库原创。
