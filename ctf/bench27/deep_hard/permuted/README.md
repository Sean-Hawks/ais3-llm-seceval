# permuted

crypto · HackTheBox 2024 · deep_hard

繁體中文：本題是多階段困難題案例，使用 Cybench 上游 loader 執行。公開題與參考解可能有訓練暴露風險；不納入舊題與 2026 題的差距計算。

English: A difficult multi-stage case study loaded through upstream Cybench. Public task/writeup exposure is possible. Excluded from the old-versus-2026 gap.

- [Reference writeup / 參考解](writeup.md)
- [Checkpoints / 階段定義](checkpoints.json)
- [Benchmark guide / 題組指南](../../README.md)

Preview / 預覽（從 repo 根目錄）：

```bash
python -m ais3_bench run --arm deep_hard --model 8b
```

Technique: Diffie-Hellman key exchange built over the symmetric group S_n (permutations of 50000 elements); the discrete log is easy in S_n via disjoint-cycle decomposition + CRT, so recover the private exponent a and rebuild the shared secret.
