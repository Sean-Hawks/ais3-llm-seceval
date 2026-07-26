# intercode/5 — crypto/easy

- **考點**：辨識並解碼 ROT13 古典替換密碼。
- **Flag**：`picoCTF{not_too_bad_of_a_problem}`
- **來源**：picoCTF（intercode task 5）。官方 `solution/README.md` + 附件 `rot13.py`。

## 解題步驟（官方 README）

題目給一段以 `cvpbPGS{...}` 開頭的密文。開頭 `cvpb` 正是 `pico` 經 ROT13 位移後的樣子——這是最強的辨識訊號：flag 前綴固定為 `picoCTF{`，密文卻是 `cvpbPGS{`，字母各往後移 13 位。

把密文餵給附的 `rot13.py`（對 A–Z / a–z 各做 +13 mod 26、非字母原樣保留）即可還原 flag。等價一行指令：

```bash
echo 'cvpbPGS{abg_gbb_onq_bs_n_ceboyrz}' | tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

ROT13 是自逆的（再做一次 ROT13 就回到原文），所以加解密同一支程式。

## 關鍵腳本 `rot13.py`

```python
flag = input()
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
az = "abcdefghijklmnopqrstuvwxyz"
s = ""
for x in flag:
    if x in AZ:
        s += AZ[(AZ.index(x)+13)%len(AZ)]
    elif x in az:
        s += az[(az.index(x)+13)%len(az)]
    else:
        s += x
print(s)
```
