"""Read-only checkpoint. Deliberately accepts emulator serials only."""
from pathlib import Path
import argparse
import json
import os
import re
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--serial', default='emulator-5582')
parser.add_argument('--adb-port', type=int, default=5039)
args = parser.parse_args()
if not re.fullmatch(r'emulator-\d+', args.serial):
    parser.error('VM-only: use an emulator-NNNN serial')
tools = Path(os.environ.get('ALADDIN_ANDROID_TOOLS',
             str(Path.home() / 'AppData/Local/Temp/Aladdin-Android-9')))
base = [str(tools / 'sdk/platform-tools/adb.exe'), '-P', str(args.adb_port), '-s', args.serial]


def shell(command):
    result = subprocess.run(base + ['shell', command], capture_output=True, timeout=25)
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors='replace'))
    return result.stdout.decode(errors='replace')


names = ['ro.build.version.incremental', 'ro.build.version.sdk',
         'ro.product.cpu.abilist', 'sys.boot_completed', 'init.svc.zygote']
values = shell('; '.join('getprop ' + name for name in names)).splitlines()
properties = dict(zip(names, (v.strip() for v in values)))
windows = shell('dumpsys window windows')
activity = shell('dumpsys activity activities')
focus = re.search(r'^\s*mCurrentFocus=(.*)$', windows, re.M)
resumed = re.findall(r'^\s*(?:mResumedActivity|ResumedActivity):?\s*[=:]?\s*(.*)$', activity, re.M)
report = {'serial': args.serial, 'properties': properties,
          'window_manager_booted': 'mSystemBooted=true' in windows,
          'display_enabled': 'mDisplayEnabled=true' in windows,
          'focused_window': focus.group(1).strip() if focus else None,
          'resumed_activity': resumed[-1].strip() if resumed else None,
          'visual_interaction_verified_by_this_script': False}
print(json.dumps(report, indent=2, ensure_ascii=False))
