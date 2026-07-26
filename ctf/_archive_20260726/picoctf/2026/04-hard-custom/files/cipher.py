# 本程式把 flag 加密成 flag.enc；請逆向還原 flag。
key=b'A1S3_k3y'
def enc(pt):
    out=bytearray()
    for i,b in enumerate(pt):
        x=(b+i*7)%256
        x^=key[i%len(key)]
        x=((x<<3)|(x>>5))&0xff
        out.append(x)
    return bytes(out)
