# Execution and reporting / 執行與問題回報

This repository intentionally contains vulnerable CTF fixtures, public challenge flags and exploit examples for local evaluation. These are distinct from real API credentials. Run them only in an isolated environment you control; keep the model's agent inside the provided sandbox and do not mount the repository, credentials or the Docker socket into it.

Static tasks use `network_mode: none`; the six local service tasks use internal Compose networks. Upstream task sandboxes are managed separately. These settings restrict connectivity but are not a proof of containment. Some historical/upstream setups use privileged containers; review them before execution. Do not expose victim ports to the internet.

A reference writeup, checkpoint target or transcript is evaluator material. Only allowlisted `challenge.json.files` should enter the agent sandbox. Raw logs may contain submitted prompts, tool output or environment details; review/redact them before publication. Never post API keys in an issue.

For an unintended vulnerability in the harness or an exposed credential, use the repository's private GitHub vulnerability-reporting facility if enabled. If unavailable, open a minimal issue requesting a private contact **without** exploit details or secrets. Ordinary known challenge weaknesses should be labeled as intended CTF behavior.

---

本 repo 刻意包含有漏洞的 CTF 題目、公開 flag 與解題範例，這與真實 API 憑證不同。請只在自己控制的隔離環境執行，不把整個 repo、金鑰或 Docker socket 掛入 agent 沙箱，不公開 victim port。

靜態題斷網、自訂服務題採內部網路；上游沙箱須另外檢查。限制網路不等於完整防護，舊／上游 privileged 設定也需先檢視。參考解、checkpoints 與 target 留在評分端，只將明確允許的題目附件給模型。

公開 raw logs 前檢查是否有金鑰、個資或環境資訊。非預期 harness 漏洞或憑證外洩可使用 repo 已啟用的 GitHub 私密回報；若未啟用，只開不含敏感細節的 issue 取得私下聯絡方式。已知 CTF 漏洞請標明為題目預期行為。
