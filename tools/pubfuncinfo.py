# pubfuncinfo.py: sanitize a funcinfo TSV for publishing: drop S (string) rows, replace s_* names by fn_<addr>.
# usage: py -3.13 -I pubfuncinfo.py <in.tsv> <out.tsv>
import sys
n = 0
out = []
for l in open(sys.argv[1], encoding='utf-8', errors='replace'):
    f = l.split()
    if not f or f[0] == 'S': continue
    if f[0] == 'F' and f[2].startswith('s_'):
        f[2] = 'fn_' + f[1]; n += 1
        l = ' '.join(f) + '\n'
    out.append(l.rstrip('\r\n') + '\n')
open(sys.argv[2], 'w', encoding='utf-8', newline='\n').write(''.join(out))
print('rows', len(out), 's_ replaced', n)
