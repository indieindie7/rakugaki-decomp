# trimdump.py <decomp.c> <out.c> [head=45] [tail=8]: shorten every function body of a CsDumpAll dump
# (keeps the "// ==== name @ addr" header, hint lines and the first/last lines; marks the cut).
import sys, re
src, dst = sys.argv[1], sys.argv[2]
H = int(sys.argv[3]) if len(sys.argv) > 3 else 45
T = int(sys.argv[4]) if len(sys.argv) > 4 else 8
funcs, cur = [], None
for l in open(src, encoding='utf-8', errors='replace'):
    if l.startswith('// ==== '):
        cur = [l]; funcs.append(cur)
    elif cur is not None: cur.append(l)
n = 0
with open(dst, 'w', encoding='utf-8') as w:
    for f in funcs:
        if len(f) > H + T + 4:
            f = f[:H] + ['/* ... %d lines cut ... */\n' % (len(f) - H - T)] + f[-T:]; n += 1
        w.writelines(f)
print(len(funcs), 'functions,', n, 'trimmed')
