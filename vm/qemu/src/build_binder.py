"""Generate VM-only Binder stand-ins against the ORIGINAL ROM's boot-classpath AIDL.

No projector APK or partition is modified. All hardware setters are inert.
"""
from pathlib import Path
import re
import os

LAYER = Path(__file__).resolve().parents[1]
root = Path(os.environ.get('ALADDIN_VM_INPUTS', str(LAYER / 'inputs')))
source = root / "original-sdk-smali/com/xgimi/aidl"
output = LAYER / "build/binder/smali"
output.mkdir(parents=True, exist_ok=True)
interfaces = [p for p in source.glob("I*.smali") if "$" not in p.name and
              (source / (p.stem + "$Stub.smali")).exists()]
if len(interfaces) != 17:
    raise SystemExit('Expected 17 firmware AIDL interfaces; check ALADDIN_VM_INPUTS')
names = {p.stem for p in interfaces}
count = 0
for interface in interfaces:
    name = interface.stem
    clazz = "Lvm/" + name + ";"
    base = "Lcom/xgimi/aidl/" + name + "$Stub;"
    text = f".class public {clazz}\n.super {base}\n\n"
    text += f".method public constructor <init>()V\n .locals 0\n invoke-direct {{p0}}, {base}-><init>()V\n return-void\n.end method\n"
    for signature in re.findall(r"^\.method public abstract (\S+)", interface.read_text(), re.M):
        method, result = signature.split(")")
        method_name = method.split("(")[0]
        body = f" const-string v0, \"{name}.{method_name}\"\n invoke-static {{v0}}, Lvm/Main;->trace(Ljava/lang/String;)V\n"
        target = result.removeprefix("Lcom/xgimi/aidl/").removesuffix(";")
        if result.startswith("Lcom/xgimi/aidl/") and target in names:
            body += f" new-instance v0, Lvm/{target};\n invoke-direct {{v0}}, Lvm/{target};-><init>()V\n return-object v0\n"
        elif result in ("Ljava/util/List;", "Ljava/util/ArrayList;"):
            body += " new-instance v0, Ljava/util/ArrayList;\n invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V\n return-object v0\n"
        elif result == "V":
            body += " return-void\n"
        elif result in ("J", "D"):
            body += " const-wide/16 v0, 0\n return-wide v0\n"
        elif result.startswith(("L", "[")):
            body += " const/4 v0, 0\n return-object v0\n"
        else:
            body += " const/4 v0, 0\n return v0\n"
        text += f"\n.method public {signature}\n .locals 2\n{body}.end method\n"
        count += 1
    (output / (name + ".smali")).write_text(text, encoding="utf-8")

(output / "Main.smali").write_text('''.class public Lvm/Main;
.super Ljava/lang/Object;

.method public static trace(Ljava/lang/String;)V
 .locals 1
 const-string v0, "ALADDIN_VM_BINDER"
 invoke-static {v0, p0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
 return-void
.end method

.method public static main([Ljava/lang/String;)V
 .locals 2
 invoke-static {}, Landroid/os/Looper;->prepareMainLooper()V
 new-instance v0, Lvm/IXgimiService;
 invoke-direct {v0}, Lvm/IXgimiService;-><init>()V
 const-string v1, "XGIMI"
 invoke-static {v1, v0}, Landroid/os/ServiceManager;->addService(Ljava/lang/String;Landroid/os/IBinder;)V
 const-string v0, "VM-only XGIMI Binder registered; hardware setters are inert"
 invoke-static {v0}, Lvm/Main;->trace(Ljava/lang/String;)V
 sget-object v0, Ljava/lang/System;->out:Ljava/io/PrintStream;
 const-string v1, "VM XGIMI Binder ready"
 invoke-virtual {v0, v1}, Ljava/io/PrintStream;->println(Ljava/lang/String;)V
 invoke-static {}, Landroid/os/Looper;->loop()V
 return-void
.end method
''', encoding="utf-8")
print(f"Generated {len(interfaces)} original-AIDL stand-ins, {count} methods")
