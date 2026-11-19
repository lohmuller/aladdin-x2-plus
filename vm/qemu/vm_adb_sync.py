import socket,struct,json,sys,re
from pathlib import Path
class AdbSync:
 def __init__(self,serial='emulator-5582',port=5039):
  if not re.fullmatch(r'emulator-\d+',serial):raise ValueError('VM-only: use an emulator-NNNN serial')
  self.s=socket.create_connection(('127.0.0.1',port),timeout=10)
  for cmd in ['host:transport:'+serial,'sync:']:
   b=cmd.encode();self.s.sendall(f'{len(b):04x}'.encode()+b)
   if self.read(4)!=b'OKAY':raise RuntimeError('ADB connection failed')
 def read(self,n):
  a=bytearray()
  while len(a)<n:
   d=self.s.recv(n-len(a))
   if not d:raise EOFError()
   a.extend(d)
  return bytes(a)
 def close(self):self.s.close()
 def send(self,cmd,p):
  b=p.encode();self.s.sendall(cmd+struct.pack('<I',len(b))+b)
 def ls(self,p):
  self.send(b'LIST',p);rows=[]
  while True:
   tag=self.read(4)
   if tag==b'DONE':self.read(16);return rows
   if tag==b'FAIL':n=struct.unpack('<I',self.read(4))[0];raise RuntimeError(self.read(n).decode())
   if tag!=b'DENT':raise RuntimeError(tag)
   mode,size,mtime,n=struct.unpack('<IIII',self.read(16));rows.append({'name':self.read(n).decode(),'mode':mode,'size':size,'mtime':mtime})
 def get(self,p):
  self.send(b'RECV',p);data=bytearray()
  while True:
   tag,n=struct.unpack('<4sI',self.read(8))
   if tag==b'DONE':return bytes(data)
   b=self.read(n)
   if tag==b'FAIL':raise RuntimeError(b.decode())
   if tag!=b'DATA':raise RuntimeError(tag)
   data.extend(b)
 def put(self,p,data,mode=0o100755):
  import time
  self.send(b'SEND',p+','+str(mode))
  for off in range(0,len(data),65536):
   c=data[off:off+65536];self.s.sendall(b'DATA'+struct.pack('<I',len(c))+c)
  self.s.sendall(b'DONE'+struct.pack('<I',int(time.time())))
  tag,n=struct.unpack('<4sI',self.read(8))
  if tag==b'FAIL':raise RuntimeError(self.read(n).decode())
  if tag!=b'OKAY':raise RuntimeError(tag)
if __name__=='__main__':
 a=AdbSync()
 try:
  if sys.argv[1]=='list':print(json.dumps(a.ls(sys.argv[2]),indent=2))
  elif sys.argv[1]=='get':
   data=a.get(sys.argv[2])
   if len(sys.argv)>3:Path(sys.argv[3]).write_bytes(data);print('Saved',len(data))
   else:print(data.decode(errors='replace'))
 finally:a.close()
