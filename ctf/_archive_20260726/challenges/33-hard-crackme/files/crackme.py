# 需要正確密碼（4 個小寫英文字母）才會印出 flag。
enc=bytes.fromhex("802ff467869131f49a55f2dfea28c9ad4525f1b41fc100af1999f2")
def keystream(pw,ln):
    s=0
    for c in pw: s=(s*131+ord(c))&0xffffffff
    ks=[]
    for _ in range(ln):
        s=(s*1103515245+12345)&0x7fffffff
        ks.append(s&0xff)
    return bytes(ks)
pw=input("pw: ")
flag=bytes(a^b for a,b in zip(enc,keystream(pw,len(enc))))
print(flag.decode() if flag.startswith(b"AIS3{") else "nope")
