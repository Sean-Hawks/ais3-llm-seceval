# CTF evaluation / CTF 評測

**Current entry point / 目前主入口：[Bench27](bench27/README.md)。**

- [繁體中文總覽](../README.zh-TW.md) / [English overview](../README.en.md)
- [繁體中文操作指南](../docs/zh-TW/SETUP.md) / [English setup](../docs/en/SETUP.md)
- [題目索引 / Task catalog](../results/TASK_CATALOG.md)

| Path | Status / 狀態 |
|---|---|
| `bench27/` | Primary benchmark: 27 tasks, committed result evidence / 主題組與研究資料 |
| `compose.yaml`, `Dockerfile` | Shared agent sandbox for static tasks / 靜態題共用沙箱 |
| `ctf_eval.py@ctf` | Historical synthetic tasks under `_archive_20260726/challenges/` / 舊自製題 |
| `ctf_eval.py@ctf_pico` | Historical synthetic year comparison under `_archive_20260726/picoctf/` / 舊年份對照試作 |
| `ctf_eval.py@ctf_deep` | Three earlier synthetic checkpoint examples / 三題早期 checkpoint 範例 |
| `deep/cybench/` | Historical three-task trajectory pilot / 真題軌跡先導實驗 |
| `_archive_20260726/` | Archived Bench25 and earlier tasks / 封存題組 |
| `DATA_PROVENANCE.md` | Historical source notes, mostly Bench25 / 多為 Bench25 的歷史來源紀錄 |

Old synthetic year labels do not establish a real-world post-cutoff benchmark. 早期自製題的年份標籤不能當成真實賽事的 cutoff 證據。

The shared image has historically used best-effort pwntools installation and does not guarantee SageMath/complete QR tooling. Verify actual tool availability before interpreting failures. 不同工具或映像版本應記為不同實驗條件。
