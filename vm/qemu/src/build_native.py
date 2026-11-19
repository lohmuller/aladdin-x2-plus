import os
"""Rebuild the evidenced VM-only native adapters, checking exact inputs."""
from pathlib import Path
from io import BytesIO
import hashlib
import json
import sys

LAYER = Path(__file__).resolve().parents[1]
WORK = Path(os.environ.get('ALADDIN_VM_INPUTS', str(LAYER / 'inputs')))
sys.path.insert(0, str(WORK / 'tools/elfdeps'))
from elftools.elf.elffile import ELFFile
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

ADAPTERS = [
    dict(name='config', source='gmpfconfig-hidl-original.so', output='libgmpfconfigmanager_hidl.so',
         symbol='_ZN20ConfigManagerWrapper11HIDLconnectEv', address=0x1244, prologue='2de9f041',
         original='78bb760729fac55700c8fb8ce54cc5d7ac3d8e96cb3152e9c75df3d5f6d2fac4',
         adapted='10dd971c4528eaec044ca5e34e110a63ff942805867e1ad94518bba488bf621b'),
    dict(name='music', source='gmpfmusic-hidl-original.so', output='libgmpfmusicplayermanager_hidl.so',
         symbol='_ZN25MusicPlayerManagerWrapper11HIDLconnectEv', address=0x2390,
         original='0e1e1e02b7c9ca6355b56d1d474e9791eaa539f5c99c66504cca0445d8f04230',
         adapted='6685582ccc28c96597effc65d2a83a6d87fa539a6c0564d77cead359e038f0be'),
    dict(name='factory', source='gmfactory-hidl-original.so', output='libgmfactorymanager_hidl.so',
         symbol='_ZN21FactoryManagerWrapper11HIDLconnectEv', address=0x38bc,
         original='0662105e130e67ffa72120c818e352bf48fa5c8cc0fb514687fab35c87f60059',
         adapted='60f31cc2f9a4e206bda2a46ae0ac5a2a58df73847ab55316c9d7e26b58ff268a'),
    dict(name='system', source='gmpfsystem-hidl-original.so', output='libgmpfsystemmanager_hidl.so',
         symbol='_ZN20SystemManagerWrapper11HIDLconnectEv', address=0x2648,
         original='252524f92615e7950a9e446f53054a272e7f8efa1dc9b46e76d24aaa6fcd154f',
         adapted='ec4652bbdc4d2ddbff3f81c1322f0fbe47c439d2706d9b0a24d2f20a9bdfdb91'),
]


def build():
    target = LAYER / 'build/native'
    target.mkdir(parents=True, exist_ok=True)
    reports = []
    for adapter in ADAPTERS:
        original = (WORK / adapter['source']).read_bytes()
        assert hashlib.sha256(original).hexdigest() == adapter['original'], adapter['source']
        elf = ELFFile(BytesIO(original))
        symbol = next(s for s in elf.get_section_by_name('.dynsym').iter_symbols()
                      if s.name == adapter['symbol'])
        address = symbol['st_value'] & ~1
        assert address == adapter['address']
        segment = next(s for s in elf.iter_segments() if s['p_type'] == 'PT_LOAD' and
                       s['p_vaddr'] <= address < s['p_vaddr'] + s['p_filesz'])
        offset = segment['p_offset'] + address - segment['p_vaddr']
        assert original[offset:offset + 4] == bytes.fromhex(adapter.get('prologue', 'f0b589b0'))
        result = bytearray(original)
        result[offset:offset + 4] = bytes.fromhex('00207047')
        instructions = [(i.mnemonic, i.op_str) for i in Cs(CS_ARCH_ARM, CS_MODE_THUMB)
                        .disasm(result[offset:offset + 4], address)]
        assert instructions == [('movs', 'r0, #0'), ('bx', 'lr')]
        assert sum(a != b for a, b in zip(original, result)) == 4
        assert hashlib.sha256(result).hexdigest() == adapter['adapted']
        (target / adapter['output']).write_bytes(result)
        reports.append({**adapter, 'scope': 'VM only', 'changed_bytes': 4,
                        'effect': 'Keep hardware disconnected; existing getter defaults remain intact'})
    (target / 'build-report.json').write_text(json.dumps(reports, indent=2), encoding='utf-8')
    print('Verified native adapters:', len(reports))


if __name__ == '__main__':
    build()
