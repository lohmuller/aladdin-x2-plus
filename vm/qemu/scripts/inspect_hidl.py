"""Read-only ELF disassembly for VM hardware adapters."""
from pathlib import Path
import re
import sys
from elftools.elf.elffile import ELFFile
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
with Path(sys.argv[1]).open('rb') as f:
    elf = ELFFile(f)
    for symbol in elf.get_section_by_name('.dynsym').iter_symbols():
        if not symbol['st_size'] or not re.search(sys.argv[2], symbol.name):
            continue
        start = symbol['st_value'] & ~1
        segment = next(s for s in elf.iter_segments() if s['p_type'] == 'PT_LOAD' and
            s['p_vaddr'] <= start < s['p_vaddr'] + s['p_filesz'])
        f.seek(segment['p_offset'] + start - segment['p_vaddr'])
        data = f.read(symbol['st_size'])
        print(symbol.name, hex(start), symbol['st_size'])
        for instruction in Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(data, start):
            print(hex(instruction.address), instruction.mnemonic, instruction.op_str)
