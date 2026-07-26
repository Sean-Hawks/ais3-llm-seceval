#!/usr/bin/env python3
"""Bench25 視覺儀表板：產生自我更新的單檔 HTML。

用法：
  python3 ctf/bench25/dashboard_bench25.py --out ctf/bench25/dashboard.html
  python3 ctf/bench25/dashboard_bench25.py --watch 180 --out ctf/bench25/dashboard.html
"""
import html
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
try:
    import analyze_bench25 as A
except ModuleNotFoundError:
    _venv = Path(__file__).resolve().parents[2] / ".venv" / "bin" / "python"
    if _venv.exists() and not os.environ.get("_BENCH25_REEXEC"):
        os.environ["_BENCH25_REEXEC"] = "1"
        os.execv(str(_venv), [str(_venv), *sys.argv])
    raise

MODELS = A.MODELS
CATS = A.CATS
DIFFS = A.DIFFS
MANIFEST = A.MANIFEST
META = A.META

# 頁面內 <meta refresh> 的秒數。由 --watch 覆寫，讓「重新產生 HTML 的間隔」與
# 「瀏覽器重載的間隔」一致——兩者不同步的話，畫面不是看到舊快照就是白刷。
REFRESH = 120

SHORT = {
    "llama-3.1-8b": "Llama 3.1 8B",
    "gemma-4-12b": "Gemma 4 12B",
    "gemma-4-26b": "Gemma 4 26B",
    "nemotron-cascade-2-30b": "Nemotron 30B",
    "llama-3.3-70b": "Llama 3.3 70B",
    "nemotron-3-ultra-550b": "Nemotron 550B",
}
CAT_ZH = {"crypto": "密碼學", "rev": "逆向", "forensics": "數位鑑識",
          "misc": "雜項", "web": "Web", "pwn": "Pwn"}
DIFF_ZH = {"easy": "易", "medium": "中", "hard": "難"}

# 在本 harness 中確認無解的題目（見 memo.md「harness confound」）。
# 這些題不該計入能力分，儀表板單獨標示。
KNOWN_UNSOLVABLE = {
    "intercode/12": "沙箱斷網無法查 factordb，且未裝 GNFS 工具；270-bit 半質數用初等方法不可解",
}

# 狀態色取自 dataviz 參考 palette 的 status 槽位（固定、不隨主題變）。
# 淺色底 warning 對比僅 1.79 → 一律搭配符號與文字標籤，顏色不單獨表意。
CELL = {
    "solved":  ("✓", "good",     "解出"),
    "limit":   ("⏱", "warning",  "撞預算上限"),
    "error":   ("!", "critical", "harness 錯誤"),
    "unsolved": ("·", "muted",   "未解出"),
    "pending": ("",  "pending",  "尚未執行"),
    "blocked": ("⊘", "serious",  "題目在本 harness 無解"),
}


def sequential(frac):
    """單一藍色 sequential ramp（dataviz palette 100→700），供 heatmap 用。"""
    steps = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec",
             "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95"]
    if frac is None:
        return None
    return steps[max(0, min(len(steps) - 1, round(frac * (len(steps) - 1))))]


def build():
    logs, skipped = A.load_logs()
    results, errors, steps, limits, thru = A.collect(logs)
    done = 0
    for ref in logs:
        try:
            if A.read_eval_log(ref, header_only=True).status == "success":
                done += 1
        except Exception:
            pass

    def cell_state(m, item):
        tid = item["id"]
        src, short = tid.split("/", 1)
        key = (src, short)
        if m in errors and tid in dict(errors[m]):
            return "error"
        if m not in results or key not in results[m]:
            return "pending"
        if sum(results[m][key]):
            return "solved"
        if tid in limits.get(m, {}):
            return "limit"
        return "unsolved"

    # ---- 每模型總計（排除已知無解題）----
    rows = []
    for m in MODELS:
        k = n = lim = err = 0
        for it in MANIFEST:
            if it["id"] in KNOWN_UNSOLVABLE:
                continue
            st = cell_state(m, it)
            if st == "pending":
                continue
            n += 1
            if st == "solved":
                k += 1
            elif st == "limit":
                lim += 1
            elif st == "error":
                err += 1
        lo, hi = A.wilson(k, n) if n else (0, 0)
        rows.append(dict(model=m, k=k, n=n, acc=(k / n if n else None),
                         lo=lo, hi=hi, lim=lim, err=err))

    return dict(rows=rows, results=results, errors=errors, steps=steps,
                limits=limits, cell_state=cell_state, done=done,
                skipped=skipped)


def render(d):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    import subprocess
    running = subprocess.run(["pgrep", "-f", "run_bench25.sh"],
                             capture_output=True).returncode == 0
    rows = d["rows"]
    cell_state = d["cell_state"]

    graded = max((r["n"] for r in rows), default=0)
    best = max((r for r in rows if r["n"]), key=lambda r: r["acc"], default=None)

    # ---------- 統計磚 ----------
    tiles = f"""
    <div class="tiles">
      <div class="tile"><div class="tile-l">跑批進度</div>
        <div class="tile-v">{d['done']}<span class="tile-u">/12</span></div>
        <div class="tile-s">模型 × 階段（6 模型 × intercode/cybench）</div></div>
      <div class="tile"><div class="tile-l">已評分題數</div>
        <div class="tile-v">{graded}<span class="tile-u">/24</span></div>
        <div class="tile-s">領先模型已完成；24 = 25 題扣除 1 題無解題</div></div>
      <div class="tile"><div class="tile-l">目前最佳</div>
        <div class="tile-v">{(f"{best['acc']*100:.0f}" if best and best['acc'] is not None else "—")}<span class="tile-u">%</span></div>
        <div class="tile-s">{(html.escape(SHORT[best['model']]) + f"（{best['k']}/{best['n']} 題，樣本少）") if best else '尚無資料'}</div></div>
      <div class="tile"><div class="tile-l">狀態</div>
        <div class="tile-v" style="font-size:1.5rem;line-height:2.6rem">
          {'進行中' if running else '已結束'}</div>
        <div class="tile-s">最後更新 {now}</div></div>
    </div>"""

    # ---------- 準確率長條 ----------
    bars = []
    for r in rows:
        if not r["n"]:
            bars.append(f"""<tr><th>{html.escape(SHORT[r['model']])}</th>
              <td class="barcell"><div class="bartrack"></div></td>
              <td class="barval muted">尚未執行</td></tr>""")
            continue
        pct = r["acc"] * 100
        bars.append(f"""<tr><th>{html.escape(SHORT[r['model']])}</th>
          <td class="barcell">
            <div class="bartrack">
              <div class="ci" style="left:{r['lo']*100:.1f}%;width:{(r['hi']-r['lo'])*100:.1f}%"
                   title="95% CI {r['lo']*100:.0f}–{r['hi']*100:.0f}%"></div>
              <div class="bar" style="width:{pct:.1f}%"></div>
            </div></td>
          <td class="barval">{r['k']}/{r['n']} <span class="muted">({pct:.0f}%)</span></td></tr>""")
    bars_html = f"""
    <section class="card">
      <h2>整體準確率</h2>
      <p class="note">深藍為準確率，淺色區段為 95% Wilson 信賴區間。<strong>目前 epochs=1，區間普遍重疊，尚不足以排名。</strong></p>
      <table class="bars"><tbody>{''.join(bars)}</tbody></table>
    </section>"""

    # ---------- 領域 heatmap ----------
    heat = ["<tr><th></th>" + "".join(
        f"<th class='rot'>{html.escape(SHORT[m]).replace(' ', '<br>')}</th>" for m in MODELS) + "</tr>"]
    for c in CATS:
        tds = []
        for m in MODELS:
            items = [it for it in MANIFEST if it["category"] == c
                     and it["id"] not in KNOWN_UNSOLVABLE]
            sts = [cell_state(m, it) for it in items]
            graded_c = [s for s in sts if s != "pending"]
            if not graded_c:
                tds.append("<td class='hc pending' title='尚未執行'>–</td>")
                continue
            k = sum(1 for s in graded_c if s == "solved")
            frac = k / len(graded_c)
            bg = sequential(frac)
            ink = "#ffffff" if frac > 0.55 else "#0b0b0b"
            tds.append(f"<td class='hc' style='background:{bg};color:{ink}' "
                       f"title='{CAT_ZH[c]} · {SHORT[m]}：{k}/{len(graded_c)}'>"
                       f"{k}/{len(graded_c)}</td>")
        heat.append(f"<tr><th>{CAT_ZH[c]}</th>{''.join(tds)}</tr>")
    heat_html = f"""
    <section class="card">
      <h2>領域 × 模型</h2>
      <p class="note">色深表示該領域解出比例（單一藍色 sequential ramp），數字為 解出/已評分。</p>
      <div class="scroll"><table class="heat">{''.join(heat)}</table></div>
    </section>"""

    # ---------- 逐題矩陣 ----------
    grid = ["<tr><th class='qh'>題目</th><th>領域</th><th>難度</th>" + "".join(
        f"<th class='rot'>{html.escape(SHORT[m]).replace(' ', '<br>')}</th>" for m in MODELS) + "</tr>"]
    for it in MANIFEST:
        blocked = it["id"] in KNOWN_UNSOLVABLE
        tds = []
        for m in MODELS:
            st = "blocked" if blocked else cell_state(m, it)
            glyph, cls, label = CELL[st]
            note = KNOWN_UNSOLVABLE.get(it["id"], "") if blocked else ""
            tip = f"{it['id']} · {SHORT[m]}：{label}"
            if note:
                tip += f"（{note}）"
            n_msg = d["steps"].get(m, {}).get(it["id"])
            if n_msg and st in ("solved", "limit", "unsolved"):
                tip += f" · {n_msg} 則訊息"
            tds.append(f"<td class='cell {cls}' title='{html.escape(tip)}'>{glyph}</td>")
        cls_row = " blockedrow" if blocked else ""
        grid.append(
            f"<tr class='{cls_row.strip()}'><th class='qh'>{html.escape(it['id'])}</th>"
            f"<td class='dim'>{CAT_ZH[it['category']]}</td>"
            f"<td class='dim'>{DIFF_ZH[it['difficulty']]}</td>{''.join(tds)}</tr>")

    legend = " ".join(
        f"<span class='lg'><i class='cell {cls}'>{g}</i>{lab}</span>"
        for g, cls, lab in CELL.values())
    grid_html = f"""
    <section class="card">
      <h2>逐題結果（25 題 × 6 模型）</h2>
      <p class="note">每格皆帶符號與文字說明，顏色不單獨表意。滑鼠移上去看訊息數與備註。</p>
      <div class="legend">{legend}</div>
      <div class="scroll"><table class="grid">{''.join(grid)}</table></div>
    </section>"""

    # ---------- confound 警示 ----------
    warn_items = "".join(
        f"<li><code>{html.escape(k)}</code> — {html.escape(v)}</li>"
        for k, v in KNOWN_UNSOLVABLE.items())
    total_lim = sum(r["lim"] for r in rows)
    warn_html = f"""
    <section class="card warn">
      <h2>⚠ 判讀前必讀</h2>
      <ul>
        <li><strong>epochs=1，不能排名。</strong>同題同模型不同次會翻盤，需 ≥5 次跑才有可用信賴區間。</li>
        <li><strong>借用 harness 用 <code>includes()</code> 子字串評分</strong>，可被候選轟炸，分數是上界；
            與自製題的 <code>exact_flag()</code> 結果不可並列比較。</li>
        <li><strong>題目皆有公開 writeup</strong>，必然污染；只能看能力覆蓋輪廓，不能主張抗污染泛化。</li>
        <li><strong>撞預算上限共 {total_lim} 例</strong>（⏱）：那是預算耗盡不是能力不足，需與未解出分開解讀。</li>
        <li><strong>已知在本 harness 無解的題（⊘，已排除於計分）：</strong><ul>{warn_items}</ul></li>
      </ul>
    </section>"""

    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bench25 儀表板</title>
{f'<meta http-equiv="refresh" content="{REFRESH}">' if running else ''}
<style>
:root{{color-scheme:light;--surface:#fcfcfb;--plane:#f9f9f7;--ink:#0b0b0b;
--ink2:#52514e;--muted:#898781;--grid:#e1e0d9;--axis:#c3c2b7;
--ring:rgba(11,11,11,.10);--seq:#2a78d6;
--good:#0ca30c;--warning:#fab219;--serious:#ec835a;--critical:#d03b3b;}}
@media (prefers-color-scheme:dark){{:root:where(:not([data-theme=light])){{
color-scheme:dark;--surface:#1a1a19;--plane:#0d0d0d;--ink:#fff;--ink2:#c3c2b7;
--muted:#898781;--grid:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);
--seq:#3987e5;}}}}
:root[data-theme=dark]{{color-scheme:dark;--surface:#1a1a19;--plane:#0d0d0d;
--ink:#fff;--ink2:#c3c2b7;--grid:#2c2c2a;--axis:#383835;
--ring:rgba(255,255,255,.10);--seq:#3987e5;}}
*{{box-sizing:border-box}}
body{{margin:0;padding:24px;background:var(--plane);color:var(--ink);
font-family:system-ui,-apple-system,"Segoe UI",sans-serif;line-height:1.55}}
.wrap{{max-width:1180px;margin:0 auto}}
h1{{font-size:1.6rem;margin:0 0 4px}}
h2{{font-size:1.05rem;margin:0 0 6px}}
.sub{{color:var(--ink2);margin:0 0 20px;font-size:.9rem}}
.card{{background:var(--surface);border:1px solid var(--ring);border-radius:10px;
padding:18px 20px;margin-bottom:16px}}
.note{{color:var(--ink2);font-size:.85rem;margin:0 0 14px}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));
gap:12px;margin-bottom:16px}}
.tile{{background:var(--surface);border:1px solid var(--ring);border-radius:10px;padding:14px 16px}}
.tile-l{{color:var(--ink2);font-size:.8rem}}
.tile-v{{font-size:2.1rem;font-weight:600;line-height:2.6rem}}
.tile-u{{font-size:1rem;color:var(--muted);font-weight:400}}
.tile-s{{color:var(--muted);font-size:.75rem;margin-top:2px}}
table{{border-collapse:collapse;width:100%}}
.bars th{{text-align:left;font-weight:500;padding:5px 12px 5px 0;white-space:nowrap;font-size:.88rem}}
.bars td{{padding:5px 0}}
.barcell{{width:100%}}
.bartrack{{position:relative;height:16px;background:var(--grid);border-radius:3px}}
.bar{{position:absolute;inset-block:0;left:0;background:var(--seq);
border-radius:0 4px 4px 0;box-shadow:0 0 0 2px var(--surface)}}
.ci{{position:absolute;inset-block:3px;background:var(--axis);border-radius:2px;opacity:.75}}
.barval{{padding-left:12px;white-space:nowrap;font-variant-numeric:tabular-nums;font-size:.88rem}}
.muted{{color:var(--muted)}}
.scroll{{overflow-x:auto}}
.heat th,.grid th{{font-weight:500;font-size:.8rem;color:var(--ink2);padding:4px 6px;text-align:center}}
.heat th:first-child,.grid .qh{{text-align:left;white-space:nowrap}}
.rot{{font-size:.72rem;line-height:1.15}}
.hc{{text-align:center;padding:8px 6px;font-size:.82rem;font-variant-numeric:tabular-nums;
border:2px solid var(--surface);border-radius:4px}}
.hc.pending{{background:var(--grid);color:var(--muted)}}
.grid td.dim{{font-size:.78rem;color:var(--ink2);text-align:center;white-space:nowrap}}
.grid tr:nth-child(even) td.dim,.grid tr:nth-child(even) .qh{{background:rgba(137,135,129,.06)}}
.qh{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.76rem}}
.cell{{text-align:center;font-size:.95rem;font-weight:700;padding:5px 6px;
border:2px solid var(--surface);border-radius:4px;min-width:34px}}
.cell.good{{background:var(--good);color:#fff}}
.cell.warning{{background:var(--warning);color:#0b0b0b}}
.cell.critical{{background:var(--critical);color:#fff}}
.cell.serious{{background:var(--serious);color:#0b0b0b}}
.cell.muted{{background:var(--grid);color:var(--muted)}}
.cell.pending{{background:transparent;color:var(--muted);border:2px dashed var(--grid)}}
.blockedrow .qh,.blockedrow td.dim{{opacity:.6;text-decoration:line-through}}
.legend{{display:flex;flex-wrap:wrap;gap:14px;margin-bottom:12px;font-size:.8rem;color:var(--ink2)}}
.lg{{display:inline-flex;align-items:center;gap:6px}}
.lg i{{display:inline-block;font-style:normal;min-width:26px}}
.warn{{border-left:3px solid var(--warning)}}
.warn ul{{margin:0;padding-left:20px;font-size:.87rem;color:var(--ink2)}}
.warn li{{margin:5px 0}}
code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.85em}}
footer{{color:var(--muted);font-size:.78rem;margin-top:18px}}
</style>
<div class="wrap">
  <h1>Bench25 評測儀表板</h1>
  <p class="sub">6 個解題模型 × 25 題（cybench 19 ＋ InterCode 6）·
     {f'每 {REFRESH} 秒自動更新' if running else '跑批已結束，此為最終快照'}</p>
  {tiles}
  {warn_html}
  {bars_html}
  {heat_html}
  {grid_html}
  <footer>由 <code>dashboard_bench25.py</code> 產生，請勿手動編輯。
     設定：epochs=1 · message-limit=50 · time-limit=900 · max-tool-output=32768 ·
     --no-parallel-tool-calls。已排除 {d['skipped']} 個底線目錄下的中止批次 log。</footer>
</div>"""


def main():
    import argparse
    import subprocess
    import time
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="ctf/bench25/dashboard.html")
    ap.add_argument("--watch", type=int, default=0)
    args = ap.parse_args()

    global REFRESH
    if args.watch:
        REFRESH = args.watch

    def once():
        t0 = time.time()
        Path(args.out).write_text(render(build()))
        return datetime.now().strftime("%F %T"), time.time() - t0

    if not args.watch:
        ts, _ = once()
        print(f"[{ts}] 已寫入 {args.out}")
        return
    while True:
        ts, cost = once()
        # 印出產生耗時：它會隨 log 數成長（每次都要重讀全部 .eval）。
        # 一旦 cost 逼近 --watch 間隔，watcher 就會變成連續重建、吃滿一顆 CPU
        # 並和跑批搶資源，此時應把間隔調回大一點。
        warn = "  ⚠ 產生耗時已接近刷新間隔，建議調大 --watch" if cost > args.watch * 0.6 else ""
        print(f"[{ts}] 已更新 {args.out}（耗時 {cost:.1f}s）{warn}", flush=True)
        if subprocess.run(["pgrep", "-f", "run_bench25.sh"],
                          capture_output=True).returncode != 0:
            print("跑批結束，已產生最終快照，watcher 退出。", flush=True)
            break
        time.sleep(max(0, args.watch - cost))


if __name__ == "__main__":
    main()
