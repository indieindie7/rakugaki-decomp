"""psxrules.py: decider step for a PSX RAM dump (MIPS LE, base 0x80000000).

    py -3.13 -I psxrules.py <ram.bin> <funcinfo.tsv> <names out> <hints out>

Names (hand-file lines): BIOS call stubs (li t2,0xA0/B0/C0; jr t2; li t1,N) named from the public psx-spx
function tables; stub_/ret<N>_ for empty or constant bodies.
Hints (one line per other function): hardware blocks touched (lui 0x1f80 + offset), GTE op count, cop0 use,
strings, BIOS stubs called.
"""
import collections, struct, sys

# psx-spx "BIOS Function Summary" (public docs), only the ones PsyQ libraries wrap
A0 = {0x00: 'FileOpen', 0x01: 'FileSeek', 0x02: 'FileRead', 0x03: 'FileWrite', 0x04: 'FileClose', 0x05: 'FileIoctl', 0x06: 'exit', 0x0a: 'todigit', 0x0e: 'abs', 0x0f: 'labs', 0x10: 'atoi', 0x11: 'atol',
      0x13: 'SaveState',
      0x14: 'RestoreState', 0x15: 'strcat', 0x16: 'strncat', 0x17: 'strcmp', 0x18: 'strncmp', 0x19: 'strcpy', 0x1a: 'strncpy',
      0x1b: 'strlen', 0x1c: 'index', 0x1d: 'rindex', 0x1e: 'strchr', 0x1f: 'strrchr', 0x24: 'strstr', 0x25: 'toupper',
      0x26: 'tolower', 0x27: 'bcopy', 0x28: 'bzero', 0x29: 'bcmp',
      0x2a: 'memcpy', 0x2b: 'memset', 0x2f: 'rand', 0x30: 'srand', 0x33: 'malloc', 0x34: 'free', 0x39: 'InitHeap',
      0x3f: 'printf', 0x44: 'FlushCache', 0x49: 'GPU_cw', 0x70: '_bu_init', 0x71: 'CdInit', 0x72: 'CdRemove',
      0x9f: 'SetMemSize', 0xa0: 'WarmBoot', 0xa1: 'SystemErrorBootOrDiskFailure', 0xa2: 'EnqueueCdIntr',
      0xa3: 'DequeueCdIntr', 0xab: '_card_info', 0xac: '_card_load'}
B0 = {0x00: 'alloc_kernel_memory', 0x07: 'DeliverEvent', 0x08: 'OpenEvent', 0x09: 'CloseEvent', 0x0a: 'WaitEvent',
      0x0b: 'TestEvent', 0x0c: 'EnableEvent', 0x0d: 'DisableEvent', 0x0e: 'OpenThread', 0x0f: 'CloseThread',
      0x10: 'ChangeThread', 0x12: 'InitPad', 0x13: 'StartPad', 0x14: 'StopPad', 0x15: 'OutdatedPadInitAndStart',
      0x16: 'OutdatedPadGetButtons', 0x17: 'ReturnFromException', 0x18: 'SetDefaultExitFromException',
      0x19: 'SetCustomExitFromException', 0x20: 'UnDeliverEvent', 0x32: 'FileOpen', 0x33: 'FileSeek',
      0x34: 'FileRead', 0x35: 'FileWrite', 0x36: 'FileClose', 0x37: 'FileIoctl', 0x38: 'exit', 0x3f: 'puts',
      0x40: 'chdir', 0x41: 'FormatDevice', 0x42: 'firstfile', 0x43: 'nextfile', 0x44: 'FileRename',
      0x45: 'FileDelete', 0x46: 'FileUndelete', 0x47: 'AddDevice', 0x48: 'RemoveDevice', 0x4a: 'InitCard',
      0x4b: 'StartCard', 0x4c: 'StopCard', 0x4e: 'write_card_sector', 0x4f: 'read_card_sector',
      0x50: 'allow_new_card', 0x56: 'GetC0Table', 0x57: 'GetB0Table', 0x58: 'get_bu_callback_port',
      0x5b: 'ChangeClearPad'}
C0 = {0x00: 'EnqueueTimerAndVblankIrqs', 0x01: 'EnqueueSyscallHandler', 0x02: 'SysEnqIntRP', 0x03: 'SysDeqIntRP',
      0x07: 'InstallExceptionHandlers', 0x08: 'SysInitMemory', 0x0a: 'ChangeClearRCnt', 0x0c: 'InitDefInt',
      0x12: 'InstallDevices', 0x1c: 'AdjustA0Table'}
TAB = {0xa0: ('A0', A0), 0xb0: ('B0', B0), 0xc0: ('C0', C0)}

HW = [(0x1000, 0x1040, 'memctl'), (0x1040, 0x1060, 'sio'), (0x1060, 0x1070, 'memctl'), (0x1070, 0x1080, 'irq'),
      (0x1080, 0x1100, 'dma'), (0x1100, 0x1130, 'timer'), (0x1800, 0x1804, 'cdrom'), (0x1810, 0x1818, 'gpu'),
      (0x1820, 0x1828, 'mdec'), (0x1c00, 0x2000, 'spu'), (0x2000, 0x2100, 'exp2')]


def main():
    ram, fi, out, hints = sys.argv[1:5]
    m = open(ram, 'rb').read()
    word = lambda a: struct.unpack_from('<I', m, a & 0x1fffff)[0]
    fs, strs, calls, cur = {}, collections.defaultdict(list), collections.defaultdict(list), None
    for l in open(fi, encoding='utf-8', errors='replace'):
        t = l.rstrip('\n').split(' ', 1)
        if t[0] == 'F':
            p = t[1].split(); cur = int(p[0], 16); fs[cur] = (p[1], int(p[3]))
        elif t[0] == 'S' and cur is not None and t[1] not in strs[cur]: strs[cur].append(t[1])
        elif t[0] == 'C' and cur is not None: calls[cur].append(int(t[1], 16))
    new, used = {}, collections.Counter()
    for a, (n, s) in fs.items():
        if not n.startswith('FUN_'): continue
        ws = [word(x) for x in range(a, a + min(s, 64), 4)]
        if len(ws) >= 3 and ws[0] >> 16 == 0x240a and (ws[0] & 0xffff) in TAB and ws[1] == 0x01400008 \
                and ws[2] >> 16 == 0x2409:                       # li t2,X ; jr t2 ; li t1,N
            k, tb = TAB[ws[0] & 0xffff]; fn = ws[2] & 0xffff
            nm = 'bios%s_%s' % (k, tb.get(fn, '%02x' % fn)); used[nm] += 1
            if used[nm] > 1: nm += '_%d' % used[nm]
            new[a] = (nm, 'BIOS %s(%02x) call stub' % (k, fn))
        elif ws[:2] == [0x03e00008, 0]:
            new[a] = ('stub_%08x' % a, 'empty: jr ra')
        elif len(ws) >= 2 and ws[0] == 0x03e00008 and ws[1] >> 16 == 0x2402:
            v = struct.unpack('<h', struct.pack('<H', ws[1] & 0xffff))[0]
            new[a] = ('ret%s_%08x' % (str(v).replace('-', 'M'), a), 'returns %d' % v)
    with open(out, 'w', encoding='utf-8') as w:
        for a in sorted(new):
            w.write('0x%08x func %s hand rules: %s\n' % (a, new[a][0], new[a][1]))
    names = {a: v[0] for a, v in new.items()}
    nh = 0
    with open(hints, 'w', encoding='utf-8') as w:
        for a, (n, s) in sorted(fs.items()):
            if a in names: continue
            hb, gte, c0, hi = set(), 0, 0, {}
            for x in range(a, a + s, 4):
                i = word(x); op = i >> 26
                if op == 0x0f: hi[(i >> 16) & 31] = (i & 0xffff) << 16          # lui
                elif op in (0x09, 0x23, 0x21, 0x25, 0x20, 0x24, 0x2b, 0x29, 0x28) and ((i >> 21) & 31) in hi:
                    v = (hi[(i >> 21) & 31] + struct.unpack('<h', struct.pack('<H', i & 0xffff))[0]) & 0xffffffff
                    if (v & 0x1fffffff) >> 16 == 0x1f80:
                        for lo, h2, nm in HW:
                            if lo <= (v & 0xffff) < h2: hb.add(nm)
                if op == 0x12 and (i >> 25) & 1: gte += 1                           # cop2 command
                elif op in (0x12, 0x32, 0x3a): gte += 1                             # mfc2/mtc2/lwc2/swc2
                if op == 0x10: c0 += 1
            parts = []
            if hb: parts.append('hw=' + ','.join(sorted(hb)))
            if gte: parts.append('gte=%d' % gte)
            if c0: parts.append('cop0=%d' % c0)
            if strs[a]: parts.append('str=' + ' | '.join(strs[a][:4]))
            cn = sorted({names[c] for c in calls[a] if c in names})
            if cn: parts.append('calls=' + ','.join(cn[:6]))
            if parts:
                w.write('0x%08x %s\n' % (a, '; '.join(parts))); nh += 1
    print('names', len(new), 'hints', nh)


main()
