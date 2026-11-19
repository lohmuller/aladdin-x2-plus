"""Capture the ARM VM without compressing PNG on its emulated CPU."""
from pathlib import Path
import os
import struct
import subprocess
import sys
import zlib

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from vm_adb_sync import AdbSync

tools = Path(os.environ.get('ALADDIN_ANDROID_TOOLS',
    str(Path.home() / 'AppData/Local/Temp/Aladdin-Android-9')))
adb = tools / 'sdk/platform-tools/adb.exe'
remote = '/data/local/tmp/vm-layer-screen.raw'
subprocess.run([str(adb), '-P', '5039', '-s', 'emulator-5582', 'shell',
    '/data/local/tmp/busybox timeout 45 screencap ' + remote],
    check=True, timeout=55)
a = AdbSync()
try:
    data = a.get(remote)
finally:
    a.close()
w, h, fmt = struct.unpack_from('<III', data)
if not (0 < w <= 4096 and 0 < h <= 4096 and fmt in (1, 2, 3)):
    raise ValueError(f'Unsupported screencap header: {w}, {h}, {fmt}')
bpp = 3 if fmt == 3 else 4
header_size = 16 if len(data) == 16 + w * h * bpp else 12
pixels = data[header_size:]
if len(pixels) != w * h * bpp:
    raise ValueError(f'Incomplete capture: {len(pixels)} bytes')
def chunk(tag, payload):
    return (struct.pack('>I', len(payload)) + tag + payload +
            struct.pack('>I', zlib.crc32(tag + payload)))
rows = b''.join(b'\0' + pixels[y*w*bpp:(y+1)*w*bpp] for y in range(h))
png = (b'\x89PNG\r\n\x1a\n' +
       chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2 if bpp == 3 else 6, 0, 0, 0)) +
       chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))
out = Path(sys.argv[1]) if len(sys.argv) > 1 else root / 'raw-capture.png'
out.write_bytes(png)
print(f'{w}x{h}, format={fmt}, saved {out}')
