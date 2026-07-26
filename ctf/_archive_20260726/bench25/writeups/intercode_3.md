# intercode/3 — forensics/medium

- **考點**：區分兩種 Unicode 空白並映射為位元流後還原 ASCII。
- **Flag**：`picoCTF{not_all_spaces_are_created_equal_c54f27cd05c2189f8147cc6f5deb2e56}`
- **來源**：picoCTF（intercode task 3，"whitepages"）。官方 `solution/README.md` + 附件 `whitepages_task_3.txt`。

## 解題步驟（官方 README）

用 hex editor 打開 `whitepages_task_3.txt` 會看到檔案由**兩種不同的空白字元**構成——普通空格 `0x20` 與 U+2003（EM SPACE，UTF-8 編碼 `0xE2 0x80 0x83`）。兩種空白對映到二進位的 0 與 1，即隱藏的位元流。

流程：
1. 讀原始位元組，辨識出只有兩種「空白」token。
2. 把其中一種當 `0`、另一種當 `1`，串成位元字串。
3. 每 8 bit 切一組轉成 ASCII，即得 flag。

關鍵在於察覺「看起來全是空白，但位元組不同」，而不是被純文字檢視器騙過（兩種空白在畫面上都長一樣）。

## 參考解法

```python
data = open("whitepages_task_3.txt", "rb").read()
# EM SPACE (U+2003) = 0xE2 0x80 0x83 → 位元 1；普通空格 0x20 → 位元 0
text = data.decode("utf-8")
bits = "".join('1' if ch == ' ' else '0' for ch in text)
flag = "".join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits)//8*8, 8))
print(flag)
```
