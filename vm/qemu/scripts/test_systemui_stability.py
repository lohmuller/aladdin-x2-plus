"""Directed VM regression check: original SystemUI and ImageWallpaper enabled.

Does not click any updater action. Keeps Android's ANR reporting enabled.
"""
from pathlib import Path
import gzip
import os
import json
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
root = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from vm_adb_sync import AdbSync
tools = Path(os.environ.get('ALADDIN_ANDROID_TOOLS', str(Path.home()/'AppData/Local/Temp/Aladdin-Android-9')))
adb = str(tools/'sdk/platform-tools/adb.exe')
(root/'build').mkdir(parents=True, exist_ok=True)
base = [adb,'-P','5039','-s','emulator-5582']
def shell(command):
    r = subprocess.run(base+['shell',command],capture_output=True,timeout=50)
    if r.returncode: raise RuntimeError(r.stderr.decode(errors='replace'))
    return r.stdout.decode(errors='replace')
def latest_anr():
    s = AdbSync()
    try:
        rows=sorted((r for r in s.ls('/data/system/dropbox') if 'anr@' in r['name']),
            key=lambda r:r['mtime'],reverse=True)
        for row in rows:
            b=s.get('/data/system/dropbox/'+row['name'])
            if row['name'].endswith('.gz'): b=gzip.decompress(b)
            if b.startswith(b'Process: com.android.systemui\n') or b.startswith(b'Process: com.android.systemui\r'):
                return row['name']
        return None
    finally: s.close()
def component_disabled():
    s=AdbSync()
    try: data=s.get('/data/system/users/0/package-restrictions.xml')
    finally:s.close()
    tree=ET.fromstring(data)
    pkg=tree.find("pkg[@name='com.android.systemui']")
    return pkg is not None and pkg.find("disabled-components/item[@name='com.android.systemui.ImageWallpaper']") is not None
baseline=latest_anr()
assert not component_disabled(), 'Original ImageWallpaper should remain enabled'
report={'baseline_systemui_anr':baseline,'started':time.time(),'stages':[]}
home='cc.popin.aladdin.home/cc.popin.aladdin.splash.ui.SplashActivity'
update='com.android.newsettings/.general.SystemUpdateActivity'
for index,activity in enumerate([home,update,home,update]):
    print('Opening',activity,flush=True)
    shell('am start -n '+activity)
    for turn in range(2):
        time.sleep(15)
        windows=shell('dumpsys window windows')
        focus=re.search(r'^\s*mCurrentFocus=(.*)$',windows,re.M)
        item={'stage':index,'check':turn,'focus':focus.group(1).strip() if focus else None,
            'system_ui_pid':shell('pidof com.android.systemui').strip(),
            'latest_systemui_anr':latest_anr()}
        report['stages'].append(item)
        (root/'build/systemui-stability.json').write_text(json.dumps(report,indent=2))
        print(json.dumps(item),flush=True)
        assert item['system_ui_pid'], 'Main SystemUI must remain running'
        assert item['latest_systemui_anr']==baseline, 'New SystemUI ANR detected'
        assert item['focus'] and 'Not Responding' not in item['focus'], 'ANR dialog detected'
        assert ('com.android.newsettings' if activity==update else 'cc.popin.aladdin.home') in item['focus']
report['elapsed_seconds']=time.time()-report['started']
assert len({item['system_ui_pid'] for item in report['stages']}) == 1, 'SystemUI restarted during the test'
report['passed']=True
(root/'build/systemui-stability.json').write_text(json.dumps(report,indent=2))
print('PASS: SystemUI stayed running without a new ANR',flush=True)
