# intercode/44 — rev/easy

- **考點**：閱讀 Java 驗證程式碼，從 `checkPassword` 邏輯取回密碼。
- **Flag**：`picoCTF{w4rm1ng_Up_w1tH_jAv4_be8d9806f18}`
- **來源**：picoCTF（intercode task 44，"Vault Door Training"）。官方 `solution/README.md` + 附件 `VaultDoorTraining.java`。

## 解題步驟（官方 README）

`cat` 給定的 `.java` 檔即可——密碼直接硬編碼在 `checkPassword` 函式裡（`password.equals("...")`）。這題本身就是在示範「把密碼寫死在原始碼裡」的反面教材。

流程：
1. 讀 `main`：使用者輸入被 `substring("picoCTF{".length(), len-1)` 切掉外框 `picoCTF{ }`，剩下的字串丟進 `checkPassword`。
2. 讀 `checkPassword`：直接比對常數字串 `w4rm1ng_Up_w1tH_jAv4_be8d9806f18`。
3. 套回 flag 框：`picoCTF{w4rm1ng_Up_w1tH_jAv4_be8d9806f18}`。

不需要編譯或執行，純靜態閱讀。

## 關鍵原始碼片段

```java
String input = userInput.substring("picoCTF{".length(), userInput.length()-1);
...
public boolean checkPassword(String password) {
    return password.equals("w4rm1ng_Up_w1tH_jAv4_be8d9806f18");
}
```
