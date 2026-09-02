# 项目 Provenance

本仓库面向可复现 CUMCM 工作独立设计和编写。

项目围绕以下机制构建：版本化 contract、跨产物稳定 ID、精确 result locator、选定源码 snapshot、精简 handoff/review digest、与具体版本绑定的论文审查、追加式人工 decision，以及适合公开仓库的合成回归用例。

SHA-256 只用于字节身份确实会影响证据的对象：官方来源、formal input、claim-bearing output、selected source tree、stage snapshot/handoff、review package 和最终批准 PDF。Digest 证明身份，不证明数学正确性。

如果引入公开上游软件，在合并前记录其仓库 URL、精确 revision、许可证、实际使用文件和本项目修改。不要把第三方设计、模板或代码描述为本仓库原创。
