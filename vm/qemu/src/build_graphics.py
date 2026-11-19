import os
"""Rebuild the proven EGL library path adapter from the preserved SDK24 driver tar."""
from pathlib import Path
import io
import tarfile

LAYER = Path(__file__).resolve().parents[1]
WORK = Path(os.environ.get('ALADDIN_VM_INPUTS', str(LAYER / 'inputs')))


def build():
    source = WORK / 'graphics32-virtual.tar.gz'
    output = LAYER / 'build/graphics'
    output.mkdir(parents=True, exist_ok=True)
    with tarfile.open(source, 'r:gz') as archive:
        member = next(m for m in archive.getmembers() if m.name.endswith('/libEGL_emulation.so'))
        original = archive.extractfile(member).read()
    before, after = b'/system/lib/egl/', b'/vendor/lib/egl/'
    assert len(before) == len(after)
    assert original.count(before) == 2
    adapted = original.replace(before, after)
    assert len(original) == len(adapted)
    assert adapted == (WORK / 'libEGL_emulation-vendor.so').read_bytes()
    (output / 'libEGL_emulation.so').write_bytes(adapted)
    print('Verified EGL adapter: two equal-length library paths')


if __name__ == '__main__':
    build()
