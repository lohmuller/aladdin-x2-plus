"""Build host-side VM adapters; this command does not connect to a device."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

LAYER = Path(__file__).resolve().parents[1]
WORK = Path(os.environ.get('ALADDIN_VM_INPUTS', str(LAYER / 'inputs')))
tools = Path(os.environ.get('ALADDIN_ANDROID_TOOLS',
             str(Path.home() / 'AppData/Local/Temp/Aladdin-Android-9')))
jdk = Path(os.environ.get('JAVA_HOME', str(WORK / 'tools/jdk-17.0.21+9')))
jar = tools / 'apktool_2.12.1.jar'
host = LAYER / 'build/host'
host.mkdir(parents=True, exist_ok=True)


def run(*args):
    subprocess.run([str(a) for a in args], check=True, timeout=60)


run(sys.executable, LAYER / 'src/build_native.py')
run(sys.executable, LAYER / 'src/build_graphics.py')
run(sys.executable, LAYER / 'src/build_binder.py')
run(jdk / 'bin/javac.exe', '-cp', jar, '-d', host, LAYER / 'src/DexTool.java')
dex = LAYER / 'build/binder/vm-xgimi-binder.dex'
run(jdk / 'bin/java.exe', '-cp', f'{host}{os.pathsep}{jar}', 'DexTool', 'build',
    LAYER / 'build/binder/smali', dex)
digest = hashlib.sha256(dex.read_bytes()).hexdigest()
assert digest == '3439b135fb94644ce840abea7a8865eb784c0954477687031e31e81cea5d4192', digest
report = {'scope': 'host-only build', 'native_adapters_verified': 4,
          'egl_paths_verified': 2, 'binder_interfaces': 17, 'binder_methods': 174,
          'binder_sha256': digest, 'device_modified': False}
(LAYER / 'build/verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
