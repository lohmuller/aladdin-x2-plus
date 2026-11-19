"""Measure real frame intervals before replacing the viewer."""
from pathlib import Path
import json
import socket
import struct
import time
import zlib
root = Path(__file__).resolve().parents[1]
def exact(s, n):
    data = bytearray()
    while len(data) < n:
        b = s.recv(n-len(data))
        if not b: raise EOFError('VM frame stream closed')
        data.extend(b)
    return bytes(data)
def png(w, h, pixels):
    def chunk(tag, data):
        return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data))
    rows = b''.join(b'\0'+pixels[y*w*4:(y+1)*w*4] for y in range(h))
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+
        chunk(b'IDAT',zlib.compress(rows,1))+chunk(b'IEND',b''))
if __name__ == '__main__':
    (root/'build').mkdir(parents=True, exist_ok=True)
    times=[]
    with socket.create_connection(('127.0.0.1',38582),timeout=10) as s:
        s.settimeout(30)
        for i in range(8):
            magic,w,h,n=struct.unpack('>IIII',exact(s,16))
            if magic!=0x414c5631 or not 0<w<=4096 or n!=w*h*4:
                raise ValueError('Invalid frame header')
            pixels=exact(s,n)
            times.append(time.perf_counter())
            print('frame',i,w,h,flush=True)
        (root/'stream-probe.png').write_bytes(png(w,h,pixels))
    report={'frames':len(times),'seconds':times[-1]-times[0],
        'fps':(len(times)-1)/(times[-1]-times[0]),
        'interval_seconds':[b-a for a,b in zip(times,times[1:])],
        'width':w,'height':h}
    (root/'build/stream-probe.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
