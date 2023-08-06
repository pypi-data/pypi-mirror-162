def mypow(root,exponent):
    # root to the exponent (Integer)
    res = 1
    for i in range(exponent):
        res *= root
    return res
def excel_ctn(col):
    # e.g. 'A' to column 0, 'Z' to column 25, 'AA' to column 26, 'CPU' to column 2464
    col = col.upper()
    tot = len(col)
    res = 0
    for i in range(tot):
        res += (ord(col[i])-ord('A')+1)*mypow(26,tot-i-1)
    return res-1 # Count from 0
