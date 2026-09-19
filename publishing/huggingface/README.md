# Hugging Face dataset export / 資料集發布

[Published dataset / 已發布資料集](https://huggingface.co/datasets/Sean-Hawks/ais3-bench27) · [Publication record / 發布驗證](publication.json)

Hub tag `v0.1.0` points to `0e2077ee3418985662250d8374ff4c623aa3fd5d`. All 11 uploaded files were downloaded without authentication and matched the local hashes; the three public configurations loaded 803/27/7 rows. Use this revision in `load_dataset(..., revision="v0.1.0")` to reproduce the published projection.

The exporter prepares a fixed, auditable projection of GitHub v0.1.0. It never authenticates, uploads, reads credentials or changes the historical snapshot.

```bash
python3 -m ais3_bench hub-export --output output/huggingface/bench27-v0.1.0
```

The output contains three JSONL tables (803 attempts, 27 tasks, 7 exclusions), an English/Traditional Chinese Dataset Card, citation files, license scope, an outcome figure, provenance and checksums. A field allowlist excludes raw conversations, submissions, flags, log filenames and third-party challenge attachments. Source hashes must match `source-lock.json`; changed inputs require a deliberate new dataset version.

Use the official Hugging Face CLI to authenticate locally, then upload only the generated directory to a **dataset** repository. Review its file list before upload. The repository ID defaults to `Sean-Hawks/ais3-bench27` and can be changed with `--repo-id owner/name`.

```bash
uvx --from huggingface_hub hf auth login
uvx --from huggingface_hub hf upload Sean-Hawks/ais3-bench27 \
  output/huggingface/bench27-v0.1.0 . --repo-type dataset
```

After publishing, verify the three viewer configurations, remote row counts and checksums. Pin the same Hub revision when loading related tables. A static Space can consume these public measurements separately; this dataset does not run a model or challenge service.

## 繁體中文

正式資料集已發布並建立 `v0.1.0` 標籤；以未登入的方式完成 11 個檔案的雜湊核對及三個資料表的載入測試。發布版本與驗證紀錄見上方連結。

此匯出器將 GitHub v0.1.0 固定成適合 Hugging Face 預覽的資料包，保留原始分數及排除規則。它只在本機產生檔案，不登入、不上傳、不讀金鑰。已有輸出目錄會拒絕覆蓋，以免混入舊檔。

資料表、雙語說明、來源雜湊、引用檔與結果圖會一起輸出。只發布明確允許的欄位；不含完整對話、提交、flag、原始 log 檔名或第三方題檔。正式發布時僅上傳產生的資料夾，並確認三個檢視器的筆數與版本一致。登入在官方流程內完成，無須將 token 寫入 repo。
