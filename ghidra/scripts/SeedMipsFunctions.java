// SeedMipsFunctions: seed function entries in a raw PSX RAM dump (base 0x80000000) before auto-analysis:
// every jal target inside RAM, plus every 'addiu sp,sp,-N' prologue that no jal reaches (called through pointers).
// Run as -preScript so the analyzers disassemble from the seeds.
//@category Analysis
import java.util.*;

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.Memory;

public class SeedMipsFunctions extends GhidraScript {
	@Override
	protected void run() throws Exception {
		Memory m = currentProgram.getMemory();
		Address base = toAddr(0x80000000L);
		long size = m.getBlock(base).getSize();
		TreeSet<Long> seeds = new TreeSet<>();
		int jal = 0, pro = 0;
		for (long o = 0x10000; o + 4 <= size; o += 4) {           // skip the BIOS / kernel area below 0x80010000
			int w = m.getInt(base.add(o));
			if ((w >>> 26) == 3) {                                 // jal target
				long t = 0x80000000L | ((w & 0x03ffffffL) << 2);
				if (t >= 0x80010000L && t < 0x80000000L + size) { seeds.add(t); jal++; }
			}
			if ((w & 0xffff8000) == 0x27bd8000) {                    // addiu sp,sp,-N
				seeds.add(0x80000000L + o); pro++;
			}
		}
		// a prologue is usually the first instruction; when a jal target sits just before it, keep only the jal target
		TreeSet<Long> keep = new TreeSet<>();
		for (long s : seeds) {
			Long lo = keep.isEmpty() ? null : keep.last();
			if (lo != null && s - lo <= 8 && (m.getInt(toAddr(s)) & 0xffff8000) == 0x27bd8000) continue;
			keep.add(s);
		}
		int made = 0;
		for (long s : keep) {
			if (monitor.isCancelled()) break;
			Address a = toAddr(s);
			if (getFunctionAt(a) != null) continue;
			new DisassembleCommand(a, null, true).applyTo(currentProgram, monitor);
			if (createFunction(a, null) != null) made++;
		}
		println("SeedMipsFunctions: jal refs " + jal + ", prologues " + pro + ", seeds " + keep.size() + ", functions " + made);
	}
}
