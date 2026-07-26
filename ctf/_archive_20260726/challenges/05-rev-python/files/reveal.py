# 執行我就會印出 flag（或直接讀原始碼拼回來）
parts = [chr(c) for c in [65,73,83,51]]           # AIS3
body  = "{r3ad_th3_s0urc3}"
print("".join(parts) + body)
