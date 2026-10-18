# Rakugaki Showtime (PlayStation, Treasure / Enix, 1999) reverse-engineering notes and symbols

Hand-named function map, review inputs and tools for **Rakugaki Showtime** (SLPM-86272), the main
program `HAGECHO.BIN` as it sits in RAM during a match (MIPS R3000 + GTE, PsyQ GCC). Round 1
(one naming pass over every function):

- 1,767 functions found by Ghidra 12.1.4 in a gameplay RAM dump (code about 0x80010000..0x8018ffff, loader at 0x80190000);
- 1,767 hand-named, 0 placeholders left, 227 still marked `provisional` (a second review round with callers is queued and will be pushed as round 2).

Game: a throwing arena brawler (pick up and throw items and other characters), 3D characters drawn as doodles.
Subsystems named so far: character state machines (`char_`/`chr_`), items and projectiles (`obj_`, `proj_`),
effects (`fx_`), match rules and AI (`match_`, `ai_`), camera (`cam_`), collision (`col_`), GTE drawing
(`gs_`, `gpu_`, `gfx_`), sound (`snd_`, `spu_`, `ssseq_`), CD / XA streaming (`cd_`), pad (`pad_`), menus (`ui_`),
memory card (`card_`, `save_`), BIOS calls (`biosA0_` / `biosB0_` / `biosC0_`).

Same method as [ducatiworld-decomp](https://github.com/indieindie7/ducatiworld-decomp) and
[killzone-decomp](https://github.com/indieindie7/killzone-decomp): `psxrules.py` names the BIOS stubs and
trivial returns from the RAM dump, a hinted and trimmed decompile is cut into four slices, each slice is named
from its code and strings (prompt in `ghidra/naming/prompt_r1.txt`), names are deduplicated across slices and
applied as USER_DEFINED labels, then every provisional name is re-read with up to three callers
(prompt in `ghidra/review/`). Non-commercial, done for study and preservation.

**No game data is included**: no disc image, no executables, no RAM dump, no decompiled C,
no game text, no Ghidra database. You need your own copy of the game to use any of this.

## What is here

| Path | Content |
|---|---|
| `NOTES.md` | disc layout, RAM dump capture, Ghidra setup, the naming round, what comes next |
| `ghidra/hand_rkram.txt` | hand names: `0x<addr> func <name> hand <comment>` (apply with ApplyNames.java from the Scorcher / AMOK repos, hand mode) |
| `ghidra/funcinfo_rkram.tsv` | per-function export: `F` address name source size, `C` callees (string rows removed) |
| `ghidra/naming/prompt_r1.txt`, `ghidra/review/` | the round-1 naming prompt and the provisional-review prompt |
| `ghidra/scripts/` | `CsDumpAll.java` (decompile dump with headers), `SeedMipsFunctions.java` (function seeding from MIPS prologues in a RAM dump) |
| `tools/` | `dump.lua` + `play2.lua` (PCSX-Redux: play into a match, dump RAM + screenshots), `raw2png.py`, `psxrules.py` (BIOS stub / trivial-return names), `injecthints.py`, `trimdump.py`, `slice.py`, `dedupnames.py`, `provctx.py` (review contexts with callers), `srprovapply.py` (apply review verdicts), `pubfuncinfo.py` |

## Licence

Notes, names and tools: MIT (see `LICENSE`). Rakugaki Showtime belongs to its rights holders; nothing from the
game is distributed here.
