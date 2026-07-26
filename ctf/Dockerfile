# CTF 沙箱映像：在 python:3.12-slim 上補齊常用 CTF 工具，
# 讓評測量的是「模型能力」而非「環境有沒有工具」（消除 harness confound）。
FROM python:3.12-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
      binutils file xxd bsdmainutils coreutils \
      steghide libimage-exiftool-perl \
      tshark tcpdump \
      openssl netcat-openbsd \
      unzip p7zip-full curl git \
 && rm -rf /var/lib/apt/lists/*
# Python 常用解題函式庫（pwntools 為 best-effort，失敗不擋建置）
RUN pip install --no-cache-dir pycryptodome cryptography requests z3-solver pillow \
 && (pip install --no-cache-dir pwntools || echo "pwntools skipped")
