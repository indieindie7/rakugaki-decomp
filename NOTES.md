# Rakugaki Showtime (PlayStation, Treasure / Enix 1999) decomp notes (names + notes only; no game data)

## Disc (2026-10-17)
- Japanese release SLPM-86272, own copy, one MODE2/2352 track (591,880,800 bytes). SYSTEM.CNF: BOOT = cdrom:\SLPM_862.72;1, STACK 801fff00.
- Files: SLPM_862.72 = 81,920-byte PS-X EXE loader (pc 0x801a0c1c, load address 0x80190000, text size 0x13800); HAGECHO.BIN 13,039,616 bytes = the game (header starts with a table of RAM addresses, a VABp sound bank at +0x24); ARA.BIN 888,832; DO.BIN 652 (table); CDXA\RAKU_XA1..6.XA (XA audio); MOVIE\BAD.STR.
- The game is not a plain PS-X EXE, so the code was taken from RAM instead of from the file.

## RAM dump (PCSX-Redux)
- `tools/dump.lua` dumps RAM + a screenshot every 900 vsyncs (attract mode: title, then intro cutscenes). `tools/play2.lua` presses Circle every 60 vsyncs (Start every 4th) from vsync 300 and reaches a match by about vsync 4500 (health bars, three character icons; pause menu around 6300). The in-match dump at vsync 9000 is the Ghidra program (`rkram.bin`). `tools/raw2png.py` converts the raw screenshots.
- Function prologues start at 0x80033ca0; the main code is stable up to about 0x8012d374, the title mode adds code up to about 0x801a192c.

## Ghidra (12.1.4)
- BinaryLoader, base 0x80000000, MIPS:LE:32:default, `SeedMipsFunctions.java` as pre-script: 1,768 functions, 335 strings.
- `psxrules.py` (RAM dump + funcinfo): 53 rule names (BIOS A0/B0/C0 call stubs, trivial returns) and 224 hint lines (hardware register / GTE / COP0 / string hints per function), applied first.

## Naming round 1 (2026-10-18)
- CsDumpAll dump (1,767 functions, 2.2 MB) -> `injecthints.py` -> `trimdump.py` -> `slice.py 4` (326-468 functions per slice) -> one naming agent per slice with `ghidra/naming/prompt_r1.txt` (rule at the end: every name comes from reading the code, never from a script; per-slice check: line count = function count, every line `0x<8 hex> func <name> hand <comment>`).
- `dedupnames.py`: names unique across slices, 0 functions missing.
- ApplyNames (hand mode): 1,767 named; export `ghidra/funcinfo_rkram.tsv`: 1,767 functions, 0 FUN_, 227 provisional.
- Two slices used different prefixes for the character state machine (`char_` and `chr_`): merged into `char_` in round 2.

## Review round 1 (2026-10-18)
- The 227 provisional names were re-read with their callers (`tools/provctx.py` contexts, prompt `ghidra/review/prompt_r1_rk.txt`) by a local model; verdict lines in `review/RK1_verdicts.txt`: confirmed 196, renamed 26, unsure 5. Applied with `tools/srprovapply.py`, `chr_` merged into `char_`, re-applied and re-exported: 1767 functions, 0 FUN_, 5 provisional.

## Next
- Struct typing for the character record (state machine offsets), the move table, and the bitmap/drawing canvas format.
- Title / menu code only present in the attract-mode dumps (above 0x8012d374) is not covered.
