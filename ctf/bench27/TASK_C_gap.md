# 任務 C ── 污染組 vs 近代組 gap（核心產出）

本檔彙整 gap 分析。gap 有**兩個互補視角**：frontier 參考錨點（現已完成）＋六受測模型 eval gap（夜間補齊）。
指令一律從 `inspect-test/` 跑（自動讀 .env）。

---

## 視角 ① · Frontier（Opus）參考 gap ── 能力上緣（現已完成）

來源：`frontier_manual/`（Opus 手解全 27 題，見 `SUMMARY.md` 與儀表板 artifact）。
**誠實框定**：出題方持 ground truth＝非盲測；此為「能力上緣參考錨點／checkpoint 覆蓋」。

| arm | 嚴格解出（flag 等價） | 計入「方法完備」 |
|---|---|---|
| contaminated | 10/12 = **0.83** | 10/12 = 0.83 |
| recent2026 | 8/12 = **0.67** | 12/12 = **1.00** |
| deep_hard | 2/3 = 0.67 | 2/3 = 0.67 |

**核心觀察（佐證專案抗污染論點）**：
- 嚴格 solve 率呈現污染臂 **+0.16 假性優勢**（0.83 vs 0.67）。
- 但這差異**純是題目結構混淆**，非記憶效應：近代組服務題較多（pwn×2、web×2 需 live victim service），
  被「護過夜跑批」的 no-Docker 資源規則卡成 partial。4 題 exploit 其實皆已**離線逐步驗證**
  （scrabasm shellcode 經 capstone＋glibc rand 重現、tic-tac-no 對實際 binary 證明、glotq/single-trust forgery 逐 byte 驗）。
- 計入方法完備後，近代臂達 **1.00**、gap 消失甚至反轉。
- → **Opus 在能力上緣對兩臂皆近飽和，無污染/記憶 gap**（後截止的 2026 真題解得跟公開題一樣好）。
- → 這正示範 **raw pass/fail gap 受題目結構混淆、須用 checkpoint／方法視角校正**——與本專案方法主幹（對照配對＋沙箱＋checkpoint 語意命中）一致。

**用途**：Opus 這條線＝六受測模型 gap 的**上緣參考**。小模型若在污染臂明顯 > 近代臂（且非題目難度造成），
才是污染/記憶訊號；對照 Opus（gap≈0）可校準「難度差」與「記憶差」。

---

## 視角 ② · 六受測模型 eval gap ── 進行中（夜間補齊）

**現況（部分）**：`python3 ctf/bench27/analyze_bench27.py`
- gemma-4-26b 污染臂 = **0.94**（intercode 35 樣本完成：crypto 1.00 / misc 1.00 / rev 0.90 / forensics 0.90；cybench 階段進行中）。
- 其餘 5 模型 × 兩臂尚未跑完。

**為何本 session 無法產出完整 gap（實測踩雷）**：受**單一 ais3 gateway 序列化**限制。
試過併行跑近代組取 gap → **15 分鐘 status=started、0 樣本完成**，RAM 全程穩（非 OOM），
是污染組佔滿 gateway 吞吐、近代組呼叫全卡 429/retry backoff（＝記憶警告的「gateway 排隊偽裝成慢」被實證）。
**通則：此 gateway 下兩個 inspect eval 不能併行取分，只能串接**（accuracy 不受影響，但吞吐序列化、弱者完全餓死）。

**夜間如何補齊**：串接器 `chain_after_contaminated.sh`（背景執行中）輪詢等污染組（PID 55472）跑完 →
自動跑 `run_recent2026.sh`（近代已就緒 5 題）→ `ctf/deep/cybench/run_cybench_deep.sh`（deep 3 題）。

**早上取用**：
```bash
tail -n 40 logs/bench27/overnight_contaminated.out   # 污染組進度
tail -n 40 logs/bench27/chain.out                    # 串接器進度
python3 ctf/bench27/analyze_bench27.py               # 完整六模型污染 vs 近代 gap 表
```
判讀提醒：analyze 自動排除底線目錄；「慢」看 working_time/tok/s 非 total（gateway 排隊偽裝）。
目標「至少 3 epochs 跑完」；跑不完 analyze 讀已完成部分即可。

---

## 待辦（不阻塞）
- 5 個未 wire 的近代服務題（見 `recent2026/SERVICE_WIRING.md`）→ 補齊後近代臂 pwn/web/crypto-again 領域才完整。
- 完整六模型 gap 出爐後，可用 dataviz 把儀表板 artifact 的視角 ② 從「進行中」換成實際數字。
