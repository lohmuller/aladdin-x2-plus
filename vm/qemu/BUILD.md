# Source and build guide

This is a research source package, not a complete VM installer. The tools were developed on Windows and target the Aladdin X2 Plus H0002 firmware V2.6.72. Builds below run on the host and do not contact Android devices.

## Layout

```text
README.md
docs/
vm/
  qemu/
    BUILD.md
    src/
    scripts/
    vm_adb_sync.py
  home/
apps/
  home-multilanguage/
patchs/
```

`build/` directories, inputs, and generated outputs are ignored by Git. The project does not include a QEMU binary, Android SDK, JDK, firmware, or generated OEM interface source.

## Dependencies

- Python 3.10 or newer with Tk support for the viewer. Packaging checks used Python 3.13.
- Java 17 for the Java helpers.
- An externally installed Android SDK/platform-tools and emulator appropriate for the prototype.
- Apktool 2.12.1 for the DexTool wrapper.
- Android R8/D8 for compiling ScreenStream into DEX.
- Python dependencies listed in `vm/qemu/requirements.txt`.

Install Python dependencies in your own environment:

```powershell
python -m pip install -r .\vm\qemu\requirements.txt
```

Tools are not downloaded or installed automatically. Obtain dependencies from their upstream distributions, retain their notices, and verify the versions you use. The research scripts currently expect Windows Java and ADB executable names.

## External inputs

Set `ALADDIN_VM_INPUTS` to a private directory containing the following locally prepared inputs. If unset, the generators look in `vm/qemu/inputs/`.

| Input relative to that directory | Used by |
| --- | --- |
| `gmfactory-hidl-original.so` | Native Factory adapter |
| `gmpfsystem-hidl-original.so` | Native System adapter |
| `gmpfmusic-hidl-original.so` | Native Music adapter |
| `gmpfconfig-hidl-original.so` | Native Config adapter |
| `graphics32-virtual.tar.gz` | Preserved virtual SDK24 graphics archive containing `libEGL_emulation.so` |
| `libEGL_emulation-vendor.so` | Previously verified EGL reference output for byte comparison |
| `original-sdk-smali/com/xgimi/aidl/` | Original ROM interface definitions and Stub files, prepared locally |

The four native input/output SHA-256 values, symbol addresses, and expected prologues are declared in `src/build_native.py`. Different firmware or library versions are rejected. The EGL generator requires both the source archive and the previously verified reference: its full extraction recipe remains to be documented.

The Binder generator consumes locally decoded interface declarations. Only the generator is distributed here; extracted and generated firmware-specific smali/DEX must remain outside commits. The expected input contains 17 interfaces, producing 174 methods in the verified prototype.

There is not yet an automated path from an arbitrary OTA download to this input layout. Renaming unrelated binaries to these filenames is insufficient; the native build checks the bytes.

## Host-only adapter build

Example environment, with paths replaced by your own installation locations:

```powershell
$env:ALADDIN_VM_INPUTS = 'D:\private\aladdin-inputs'
$env:ALADDIN_ANDROID_TOOLS = 'D:\tools\aladdin-android'
$env:JAVA_HOME = 'D:\tools\jdk-17'
python .\vm\qemu\scripts\build.py
```

`ALADDIN_ANDROID_TOOLS` must contain `apktool_2.12.1.jar` and, for VM tools, `sdk/platform-tools/adb.exe`. Set `JAVA_HOME` explicitly; the older fallback refers to a JDK under the input tree.

Outputs go to `vm/qemu/build/`: native libraries, the graphics adapter, generated Binder smali/DEX, and verification reports. The aggregate build checks the known Binder DEX SHA-256. Generated firmware-derived binaries are private build outputs, not publication artifacts.

Build the framebuffer server separately:

```powershell
$env:ALADDIN_R8_JAR = 'D:\tools\r8.jar'
python .\vm\qemu\scripts\build_screen.py
```

Without `ALADDIN_R8_JAR`, the script looks for `vm/qemu/tools/r8.jar`. Output is `vm/qemu/build/screen/classes.dex`. Compilation does not stage or execute it in a VM.

## Existing VM tools

The following commands require an already bootstrapped VM and an ADB server on port 5039. The prototype serial is `emulator-5582`. They do not create or boot the VM.

```powershell
python .\vm\qemu\scripts\status.py --serial emulator-5582 --adb-port 5039
```

Status is read-only and rejects physical-device serials. Most remaining research tools are fixed to `emulator-5582` and port 5039. The ADB sync helper also rejects non-emulator serials.

For an already staged and running framebuffer server, forward its loopback port and open the viewer:

```powershell
& "$env:ALADDIN_ANDROID_TOOLS\sdk\platform-tools\adb.exe" -P 5039 -s emulator-5582 forward tcp:38582 tcp:38582
python .\vm\qemu\scripts\viewer.py
```

Arrow keys navigate, Enter sends OK, and Escape sends Back. `probe_stream.py` measures eight actual frames; `capture.py` captures independently. Generated images and viewer state are ignored by Git. Do not run the probe concurrently with the viewer: the framebuffer server serves one active connection at a time.

`start-screen-budget.sh` expects a DEX already staged as `/data/local/tmp/vm-screen-stream-budget.dex` and BusyBox at `/data/local/tmp/busybox`. It starts a separate capture process at 640×360, limited to 3 FPS, with nice +10. `prioritize-systemui.sh` sets SystemUI nice -10 and can start its service if absent. These scripts change VM runtime state; they are not passive status tools. Do not start duplicate capture processes.

`test_systemui_stability.py` alternates Home and System Update, examines ANR reports and ImageWallpaper state, and requires the same SystemUI PID throughout. It takes several minutes and writes a report. It does not activate an update action. It was included for future validation and was not run against a device during source packaging.

## Deliberately not included

The old launcher and bootstrap are not presented as a working installer: they depend on intermediate images and manual runtime changes. Experimental gRPC and wallpaper helpers, firmware extracts, platform keys, APKs, screenshots, and raw device logs are also excluded. Before adding more tools, document dependencies and distinguish host-only generation from VM changes and physical-device operations.
