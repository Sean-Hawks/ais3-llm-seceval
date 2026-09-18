# Service topology / 服務配置

All six custom service tasks have `challenge.json` and `compose.yaml`. 六個服務題均已配置，舊的「待 wiring」清單已過時。

| Task | Victim port | Build context | Notes |
|---|---:|---|---|
| crypto_six-seven | 1337 | `service/` | Python + socat |
| crypto_six-seven-again | 1337 | `service/` | Solver may require SageMath; not guaranteed in agent image |
| pwn_tic-tac-no | 5000 | `files/Dockerfile.socat` | x86-64 adaptation; differs from upstream nsjail |
| pwn_scrabasm | 5000 | `service/Dockerfile.socat` | x86-64 adaptation; differs from upstream nsjail |
| web_glotq | 8080 | `files/` | Go service |
| web_single-trust | 8080 | `files/` | Node service |

`default` is the agent sandbox; `victim` is the challenge service. Both use the project-specific default network, now configured as `internal: true`. No host port publishing is added. Images may need network access during build. 此網路改善不代表已確認歷史實驗斷網，也不是容器完整安全性的保證。

Validate without launching containers / 不啟動容器的設定檢查：

```bash
docker compose -f ctf/bench27/recent2026/web_glotq/compose.yaml config --quiet
```

Use the maintained runner from the repository root. 正式跑法與限制請見[中文指南](../../../docs/zh-TW/SETUP.md) / [English setup](../../../docs/en/SETUP.md)。
