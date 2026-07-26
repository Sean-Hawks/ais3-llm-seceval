# 找出通過所有檢查的輸入——它就是 flag。（非線性約束，暴力不可行，考慮 SMT 求解器 z3）
v1=[8, 26, 96, 72, 1, 73, 108, 44, 67, 92, 26, 69, 64, 44, 60, 83, 94, 29, 7, 6, 70, 5, 95, 26, 7, 14, 60]
v2=[138, 196, 178, 159, 238, 170, 167, 144, 230, 121, 231, 213, 159, 230, 143, 215, 97, 225, 188, 239, 209, 160, 164, 158, 232, 164, 240]
anchors={0: 65, 26: 125}
n=27
pw=input('flag: ').encode()
ok=len(pw)==n
for i in range(n):
    ok&=(pw[i]^pw[(i+1)%n])==v1[i]
    ok&=((pw[i]+pw[(i*3+1)%n])&0xff)==v2[i]
for k,val in anchors.items(): ok&=pw[k]==val
print('correct! '+pw.decode() if ok else 'nope')
