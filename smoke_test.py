"""
Inspect AI 冒煙測試 — 確認能連上 AIS3 的 OpenAI-compatible endpoint。

這是最小可跑的評測：6 題資安選擇題，用 Inspect 的三件套：
  dataset (題目)  ->  solver: multiple_choice (作答)  ->  scorer: choice (對答案)

跑法（先設好 AIS3_BASE_URL / AIS3_API_KEY，見 README）：
  # 注意模型 ID 要帶 gateway 的 ais3/ 前綴，所以 ais3 會出現兩次：
  inspect eval smoke_test.py --model openai-api/ais3/ais3/llama-3.1-8b --limit 6
  inspect view          # 開瀏覽器看每一題的輸入/輸出/對錯
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import choice
from inspect_ai.solver import multiple_choice

# 每個 Sample = 一題。choices 是選項，target 是正確選項的字母(A/B/C/D)。
DATASET = [
    Sample(
        input="哪一個 HTTP 回應標頭主要用來緩解 clickjacking？",
        choices=["X-Frame-Options", "Accept-Language", "X-Powered-By", "Referer"],
        target="A",
    ),
    Sample(
        input="對抗 SQL injection 最穩健的防禦是？",
        choices=[
            "手動跳脫單引號",
            "參數化查詢 (prepared statements)",
            "隱藏錯誤訊息",
            "只靠 WAF",
        ],
        target="B",
    ),
    Sample(
        input="CWE-79 一般俗稱為？",
        choices=["SQL Injection", "跨站腳本 (XSS)", "路徑遍歷", "SSRF"],
        target="B",
    ),
    Sample(
        input="儲存使用者密碼時，下列何者最合適？",
        choices=["MD5", "SHA-1", "bcrypt", "Base64"],
        target="C",
    ),
    Sample(
        input="下列哪一個工具主要是網路封包/協定分析器？",
        choices=["Nmap", "Wireshark", "John the Ripper", "Hydra"],
        target="B",
    ),
    Sample(
        input="TOCTOU 漏洞屬於哪一類問題？",
        choices=["競態條件 (race condition)", "緩衝區溢位", "注入", "設定錯誤"],
        target="A",
    ),
]


@task
def sec_smoke():
    return Task(
        dataset=DATASET,
        solver=multiple_choice(),
        scorer=choice(),
    )
