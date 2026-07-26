# crypto_six-seven victim：每次連線跑一次 chall.py，印出新的 n,c（讀 flag.txt）。
FROM python:3.12-slim
RUN pip install --no-cache-dir pycryptodome \
 && apt-get update && apt-get install -y --no-install-recommends socat \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY chall.py flag.txt /app/
EXPOSE 1337
CMD ["socat","-T120","TCP-LISTEN:1337,reuseaddr,fork","EXEC:python3 /app/chall.py"]
