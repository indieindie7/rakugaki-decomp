# dedupnames.py <hand.txt> <decomp.c> : make names unique across slices (_2, _3 ...) and report addresses missing from the decomp's FUN_ list
import sys, re
hand, dec = sys.argv[1], sys.argv[2]
funs = set(re.findall(r'^// ==== FUN_([0-9a-f]{8})', open(dec, encoding='utf-8', errors='replace').read(), re.M))
seen = {}
out = []
addrs = set()
for l in open(hand, encoding='utf-8', errors='replace'):
    p = l.rstrip('\n').split(' ', 4)
    if len(p) < 5 or p[1] != 'func':
        continue
    a = p[0][2:]
    addrs.add(a)
    n = p[2]
    if n in seen:
        seen[n] += 1
        n = '%s_%d' % (n, seen[n])
        while n in seen:
            seen[p[2]] += 1
            n = '%s_%d' % (p[2], seen[p[2]])
        seen[n] = 1
    else:
        seen[n] = 1
    out.append('%s func %s %s %s' % (p[0], n, p[3], p[4]))
open(hand, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
missing = sorted(funs - addrs)
extra = sorted(addrs - funs)
print(len(out), 'lines;', len(missing), 'FUN_ missing from hand;', len(extra), 'hand addrs not FUN_')
if missing: open(hand + '.missing', 'w').write('\n'.join(missing) + '\n')
