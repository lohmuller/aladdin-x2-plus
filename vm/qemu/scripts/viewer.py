"""VM-only resident raw-frame viewer; no per-frame ADB process or codec."""
from pathlib import Path
import base64
import os
import queue
import subprocess
import sys
import threading
import time
import tkinter as tk
import socket
import struct
from probe_stream import exact, png

here = Path(__file__).resolve().parent
root = here.parent
tools = Path(os.environ.get('ALADDIN_ANDROID_TOOLS',
    str(Path.home() / 'AppData/Local/Temp/Aladdin-Android-9')))
adb = tools / 'sdk/platform-tools/adb.exe'
base = [str(adb), '-P', '5039', '-s', 'emulator-5582']
frames = queue.Queue(maxsize=1)
keys = queue.Queue(maxsize=2)
closed = threading.Event()
output = root / 'viewer-frame.png'
state = root / 'viewer-state.txt'
frame_info = {'fps': 0.0, 'last': 0.0, 'key': '', 'error': ''}

def capture_loop():
    while not closed.is_set():
        try:
            with socket.create_connection(('127.0.0.1',38582),timeout=10) as stream:
                stream.settimeout(15)
                previous = 0.0
                saved = 0.0
                while not closed.is_set():
                    magic,w,h,n = struct.unpack('>IIII',exact(stream,16))
                    if magic != 0x414c5631 or not 0<w<=4096 or n != w*h*4:
                        raise ValueError('Invalid VM frame')
                    data = png(w,h,exact(stream,n))
                    now = time.monotonic()
                    if previous: frame_info['fps'] = 1/(now-previous)
                    previous = now
                    if frames.full(): frames.get_nowait()
                    frames.put((data, now))
                    if now-saved > 1:
                        output.write_bytes(data)
                        saved = now
                    frame_info['error'] = ''
        except Exception as exc:
            frame_info['error'] = str(exc)
        closed.wait(1)

def key_loop():
    while not closed.is_set():
        try:
            code = keys.get(timeout=.2)
        except queue.Empty:
            continue
        try:
            result = subprocess.run(base + ['emu', 'event', 'send',
                f'EV_KEY:{code}:1', f'EV_KEY:{code}:0'],
                capture_output=True, timeout=3, creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode: frame_info['error'] = 'Falha no envio da tecla'
        except Exception as exc:
            frame_info['error'] = str(exc)

window = tk.Tk()
window.title('Aladdin Original V2.6.72 - VM ARM32 - fluxo direto')
window.configure(bg='black')
canvas = tk.Label(window, bg='black', fg='white', text='Carregando imagem real da VM...')
canvas.pack(fill='both', expand=True)
status = tk.StringVar(value='Conectando ao fluxo de quadros da VM...')
tk.Label(window, textvariable=status, bg='#202020', fg='white').pack(fill='x')
window.geometry('1280x750')
mapping = {'Left':105, 'Right':106, 'Up':103, 'Down':108, 'Return':232, 'Escape':158}
last_press = {}
def press(event):
    code = mapping.get(event.keysym)
    if code is not None:
        now = time.monotonic()
        if now-last_press.get(code,0)<.15: return 'break'
        last_press[code] = now
        if keys.full(): keys.get_nowait()
        keys.put(code)
        frame_info['key'] = event.keysym
        return 'break'
def refresh():
    if closed.is_set():
        return
    try:
        data, timestamp = frames.get_nowait()
        if data:
            image = tk.PhotoImage(data=base64.b64encode(data))
            if image.width() == 640:
                image = image.zoom(2,2)
            elif image.width() == 960:
                image = image.zoom(4,4).subsample(3,3)
            canvas.configure(image=image, text='')
            canvas.image = image
            frame_info['last'] = timestamp
            state.write_text(f'frame_displayed={time.time()}\nresident_stream_fps={frame_info["fps"]:.2f}\n', encoding='utf-8')
    except queue.Empty:
        pass
    age = time.monotonic()-frame_info['last'] if frame_info['last'] else 0
    status.set(f'{frame_info["fps"]:.1f} FPS | quadro: {age:.1f}s | tecla: {frame_info["key"]} | Setas / Enter=OK / Esc=voltar '+frame_info['error'])
    window.after(20, refresh)
def close():
    closed.set()
    window.destroy()
window.bind('<KeyPress>', press)
canvas.bind('<Button-1>', lambda event: window.focus_set())
window.protocol('WM_DELETE_WINDOW', close)
threading.Thread(target=capture_loop, daemon=True).start()
threading.Thread(target=key_loop, daemon=True).start()
refresh()
window.mainloop()
