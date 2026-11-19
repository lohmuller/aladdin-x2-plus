# Aladdin X2 Plus — Firmware V2.6.72

**[Download firmware V2.6.72](https://aladdin.static.xgimi.com/packages/rom/XGIMI_ALADD_II_PLUS_PA20U01DJ_FULL_V2_20240605115224.6.72.zip)** · [Checksum and download instructions](../../downloads/README.md)

Software fields and runtime diagnostics from an Aladdin X2 Plus running **V2.6.72**, captured on 19 November 2026. Other firmware versions can report different values.

## System

| Field | Value |
| --- | --- |
| Android model / `ro.product.model` | `popIn Aladdin 2 Plus` |
| Brand / `ro.product.brand` | `XGIMI` |
| Firmware / `ro.build.version.incremental` | `V2.6.72` |
| Android release | `9` |
| Android SDK / API level | `28` |
| Build / `ro.build.display.id` | `PPR1.180610.011.V2.6.72 release-keys` |
| System build date / `ro.build.date` | `Tue Jun 4 18:14:31 CST 2024` |
| Declared security patch | `2018-08-05` |
| Vendor security patch | Not declared |
| Primary ABI / `ro.product.cpu.abi` | `armeabi-v7a` |
| Supported ABIs / `ro.product.cpu.abilist` | `armeabi-v7a,armeabi` |
| Hardware / `ro.hardware` | `amlogic` |
| Board / `ro.board.platform` | `tl1` |

## Kernel

Kernel identification from `/proc/version`, split across lines for readability:

```text
Linux version 4.9.113 (xgimi@xgimi)
gcc version 6.3.1 20170109 (Linaro GCC 6.3-2017.02)
#1 SMP PREEMPT Tue Jun 4 18:26:33 CST 2024
```

| Field | Value |
| --- | --- |
| Kernel release | `4.9.113` |
| Build user / host | `xgimi@xgimi` |
| Compiler | `GCC 6.3.1 20170109` |
| Toolchain | `Linaro GCC 6.3-2017.02` |
| Build number | `#1` |
| Build flags | `SMP PREEMPT` |
| Kernel build date | `Tue Jun 4 18:26:33 CST 2024` |

The system build date and kernel build date are separate fields.

## Runtime diagnostic fields

| Field | Path | Value |
| --- | --- | --- |
| SELinux enforce | `/sys/fs/selinux/enforce` | `0` — Permissive |
| Binder | `/dev/binder` | `exists=true, readable=true, directory=false` |
| Kernel configuration | `/proc/config.gz` | `exists=true, readable=true, directory=false` |

`readable=true` is the file-readability flag returned to the reporting app; it does not describe access to every internal file.


SELinux and file-access flags describe the captured runtime state and can change with configuration or permissions.

## XGIMI command reference

These are the **18 named commands and two named queries recognized by the examined `XgimiOpenAidl` dispatcher** in `com.xgimi.xgimicustomservice/.XgimiNewApiService`. They are Android Binder calls, not ADB shell commands or HTTP endpoints. Other XGIMI/GMPF interfaces are separate APIs.

Each entry point receives a method name and four string slots:

```text
command(methodName, arg0, arg1, arg2, arg3) → void
get(methodName, arg0, arg1, arg2, arg3) → String
getMemoryFile(methodName, arg0, arg1, arg2, arg3) → ParcelFileDescriptor
set(methodName, arg0, arg1, arg2, arg3) → int
```

Only the arguments listed below are consumed by each command. `arg3` is unused by these command branches. Calling an operation requires a bound client and the access available to that client/service; names alone do not establish permission or a successful result.

### Commands

| Command | Parameters used | Behavior |
| --- | --- | --- |
| `installPkg` | `arg0`: APK path | Request installation through the package installer. |
| `uninstallPkg` | `arg0`: package name | Request uninstallation of that package. |
| `silentInstallAndAutoRun` | `arg0`: APK path; `arg1`: `service` or `activity`; `arg2`: `package/class` | Install the APK, then start the specified component. Installation/start ordering does not itself confirm success. |
| `setBootUpgradePackagePath` | `arg0`: source file path | Prepare the boot-install folder and attempt to copy the file to `data/xgimi_updateapps/bootInstallApp.apk`. Does not directly replace the factory launcher. |
| `setBootUninstallPackageName` | `arg0`: package name | Request package removal and then reboot. |
| `reboot` | None | Request a device reboot. |
| `shutdown` | None | Request device shutdown. |
| `setProvisionalShutdownTime` | `arg0`: duration in milliseconds, as a decimal string | Start a shutdown countdown and broadcast its duration. |
| `setBootSignalSource` | `arg0`: integer source index as text; `arg1`: source name | Set the saved boot-source selection. The implementation stores the supplied index plus one; valid source choices are not fully mapped. |
| `changeBootAnimation` | `arg0`: source file path | Copy a boot-animation asset into the local boot customization area. |
| `addBootVideo` | `arg0`: source file path | Add a file to the local boot-video directory. Android API 26+ branch. |
| `removeBootVideo` | None | Remove the stored boot-video content. |
| `setBootVideoModeAndVolume` | `arg0`: raw property value | Write `persist.vendor.media.bootvideo`. Its combined mode/volume encoding is not yet documented. |
| `lockProjectorButton` | `arg0`: raw property value | Write `persist.sys.cstm.lockprojector`. Accepted consumer values are not yet verified. |
| `lockRemoteButton` | `arg0`: raw property value | Write `persist.sys.cstm.lockremote`. Accepted consumer values are not yet verified. |
| `setUpdateDalenMcuBin` | `arg0`: source binary path | Stage a file in the LED/MCU update area. Android API 26+ branch; this is not the Android OTA endpoint. |
| `deleteUpdateDalenMcuBin` | None | Remove the staged LED/MCU update files. |
| `screenshot` | None | Invoke screen capture at display size. This `command` call returns no image. |

### Queries

| Query passed to `get` | Parameters used | Result |
| --- | --- | --- |
| `getBootSource` | None | Saved boot-source information as a string |
| `getBootVideoModeAndVolume` | None | Raw value of `persist.vendor.media.bootvideo` |

Unknown `get` names return an empty string in this implementation. A read-only Binder call has this form, once a client is bound:

```java
String value = api.get("getBootSource", "", "", "", "");
```

### Other entry points

| Entry point | Parameters used | Behavior |
| --- | --- | --- |
| `getMemoryFile` | `arg0`: width as integer text; `arg1`: height as integer text | Capture a bitmap, encode it, and return a memory-file descriptor. The examined method does not select behavior by `methodName`; `arg2` and `arg3` are unused. |
| `set` | None | Stub: returns `0` without implementing a setter. This return value does not indicate that a setting changed. |

### Functional status

The table lists implementation behavior; most modifying operations have not been validated on the physical projector. VM checks confirmed binding and some queries. The boot-install path created its target folder, but the requested file copy was not confirmed. Package installation, reboot, button locks, and firmware/MCU changes must not be inferred from a successful Binder return alone.
