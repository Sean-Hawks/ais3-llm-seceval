#!/usr/bin/env python3
"""替 Opus 盲解服務題預先啟動 victim（發佈到 host port，5 個 epoch agent 共用同一 victim）。
用法：start_opus_victims.py up  <clear1> <clear2> ...   → 啟動並印 opus_victims.json
      start_opus_victims.py down <clear1> ...            → 收掉
每題用獨立 compose project + 唯一 host port；jail 的 privileged/cgroup 已在原 compose。"""
import json, os, sys, re, subprocess, time
ROOT = os.path.dirname(os.path.abspath(__file__))
TASKS = {t["clear"]: t for t in json.load(open(os.path.join(ROOT, "opus_tasks.json"), encoding="utf-8"))}
VJSON = os.path.join(ROOT, "opus_victims.json")
BASE_PORT = 19000

def internal_port(compose_txt):
    m = re.search(r'victim:.*?expose:\s*\[?"?(\d+)', compose_txt, re.S)
    return m.group(1) if m else "1337"

def proj(clear): return "opus_" + clear.lower().replace("_","").replace("-","")[:20]

def up(clears):
    vic = json.load(open(VJSON)) if os.path.exists(VJSON) else {}
    for i, clear in enumerate(clears):
        t = TASKS[clear]; compose = os.path.join(ROOT, "..", "..", t["compose"]) if not os.path.isabs(t["compose"]) else t["compose"]
        compose = os.path.abspath(compose); cdir = os.path.dirname(compose)
        txt = open(compose).read(); ip = internal_port(txt)
        hp = BASE_PORT + 1 + len(vic) + i
        override = os.path.join(cdir, "_opus_override.yaml")
        open(override, "w").write(f"services:\n  victim:\n    ports:\n      - \"{hp}:{ip}\"\n")
        print(f"[up] {clear} port {hp}->{ip} …", flush=True)
        r = subprocess.run(["docker","compose","-p",proj(clear),"-f",compose,"-f",override,
                            "up","-d","--build","victim"], capture_output=True, text=True)
        ok = r.returncode==0
        vic[clear] = {"host":"127.0.0.1","port":hp,"internal":ip,"proj":proj(clear),"ok":ok}
        if not ok: print("  ERR:", r.stderr.strip()[-200:])
    json.dump(vic, open(VJSON,"w"), ensure_ascii=False, indent=1)
    time.sleep(6)
    for clear,v in vic.items():
        st = subprocess.run(["docker","compose","-p",v["proj"],"ps","--format","{{.State}} {{.Health}}"],
                            capture_output=True,text=True).stdout.strip()
        print(f"  {clear:38} :{v['port']} → {st or '?'}")
    print(json.dumps(vic, ensure_ascii=False))

def down(clears):
    vic = json.load(open(VJSON)) if os.path.exists(VJSON) else {}
    for clear in (clears or list(vic)):
        if clear in vic:
            subprocess.run(["docker","compose","-p",vic[clear]["proj"],"down","-v"],capture_output=True)
            print("[down]", clear)

if __name__=="__main__":
    cmd = sys.argv[1] if len(sys.argv)>1 else "up"
    (up if cmd=="up" else down)(sys.argv[2:])
