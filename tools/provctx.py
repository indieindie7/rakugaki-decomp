# provctx.py: review contexts for every provisional hand name (ckprovctx format, no image/literal pool).
# usage: py -3.13 -I provctx.py <decomp.c> <funcinfo.tsv> <hand.txt> <PROG> <N files> <out prefix>
import sys, re
dc, fi, hand, prog, n, pre = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), sys.argv[6]
b = {}; cur = None; buf = []
for l in open(dc, encoding='utf-8', errors='replace'):
    m = re.match(r'// ==== (\S+) @ ([0-9a-fA-F]+)', l)
    if m:
        if cur: b[cur] = ''.join(buf)
        cur = m.group(2).lower().zfill(8); buf = []
    buf.append(l)
if cur: b[cur] = ''.join(buf)
nm = {}
for l in open(hand, encoding='utf-8', errors='replace'):
    f = l.split(None, 4)
    if len(f) > 2: nm[f[0][2:].lower().zfill(8)] = (f[2], f[4].strip() if len(f) > 4 else '')
cl = {}; cur = None
for l in open(fi, encoding='utf-8', errors='replace'):
    f = l.split()
    if not f: continue
    if f[0] == 'F': cur = f[1].lower().zfill(8)
    elif f[0] == 'C' and cur: cl.setdefault(f[1].lower().zfill(8), []).append(cur)
def sub(t): return re.sub(r'(?:FUN_|func_0x)([0-9a-fA-F]{8})', lambda m: nm.get(m.group(1).lower(), (m.group(0),))[0], t)
items = []
for a in sorted(nm):
    name, cmt = nm[a]
    if 'provisional' not in cmt: continue
    txt = '#### %s 0x%s %s | %s\n' % (prog, a, name, cmt)
    ob = sub(b.get(a, '(no body)\n')).splitlines()
    if len(ob) > 300: ob = ob[:300] + ['  ... (body truncated, %d lines)' % len(ob)]
    txt += '\n'.join(ob) + '\n'
    cs = sorted(set(cl.get(a, [])))
    txt += '---- callers: %d (%s)\n' % (len(cs), ' '.join(nm.get(c, (c,))[0] for c in cs[:12]))
    for c in cs[:3]:
        cb = sub(b.get(c, '')).splitlines()
        if len(cb) > 80: cb = cb[:80] + ['  ... (caller truncated)']
        txt += '---- caller %s\n%s\n' % (nm.get(c, (c,))[0], '\n'.join(cb))
    items.append(txt)
print(prog, 'items', len(items))
per = (len(items) + n - 1) // n
for k in range(n):
    open('%s%d.txt' % (pre, k + 1), 'w', encoding='utf-8', newline='\n').write('\n'.join(items[k * per:(k + 1) * per]))
