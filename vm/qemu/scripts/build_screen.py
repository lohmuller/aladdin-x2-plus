"""Host-only reproducible build of the VM resident framebuffer server."""
from pathlib import Path
import os
import subprocess
root = Path(__file__).resolve().parents[1]
java = Path(os.environ.get('JAVA_HOME',str(root/'tools/jdk-17.0.21+9'))) / 'bin'
out = root/'build/screen'
classes = out/'classes'
classes.mkdir(parents=True,exist_ok=True)
subprocess.run([str(java/'javac.exe'),'-source','8','-target','8','-d',str(classes),
    str(root/'src/ScreenStream.java')],check=True)
subprocess.run([str(java/'java.exe'),'-cp',str(Path(os.environ.get('ALADDIN_R8_JAR', str(root/'tools/r8.jar')))),
    'com.android.tools.r8.D8','--min-api','28','--output',str(out),
    str(classes/'vm/ScreenStream.class')],check=True)
print(out/'classes.dex')
