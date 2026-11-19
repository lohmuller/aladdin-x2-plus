# Downloads

## Aladdin X2 Plus V2.6.72 firmware

**[Download the firmware ZIP](https://aladdin.static.xgimi.com/packages/rom/XGIMI_ALADD_II_PLUS_PA20U01DJ_FULL_V2_20240605115224.6.72.zip)**

| Field | Recorded value |
| --- | --- |
| Target studied | Aladdin X2 Plus / H0002 |
| Firmware | V2.6.72 |
| Package type | Full OTA package |
| Filename | `XGIMI_ALADD_II_PLUS_PA20U01DJ_FULL_V2_20240605115224.6.72.zip` |
| Expected MD5 | `4b54fd4ce4a5802021aeae1cc68326e8` |

The link points to the vendor server. It was supplied in an X2 Plus update response; availability can change.

### Check the downloaded file

In PowerShell, from the folder containing the ZIP:

```powershell
$firmwareHash = (Get-FileHash -LiteralPath '.\XGIMI_ALADD_II_PLUS_PA20U01DJ_FULL_V2_20240605115224.6.72.zip' -Algorithm MD5).Hash.ToLowerInvariant()
if ($firmwareHash -ne '4b54fd4ce4a5802021aeae1cc68326e8') { throw 'Firmware checksum does not match the recorded package.' }
```

Keep the original archive unchanged as the input for VM preparation. The checksum checks the package bytes, not its signature or compatibility with another model.

### Continue

- [Prepare the VM tools and inputs](../../vm/qemu/README.md#2-prepare-the-windows-tools-and-inputs)
- [Update API: URL, parameters, and historical responses](../UPDATES.md)

The ZIP alone is not a bootable QEMU disk. Extracting/preparing the partitions, virtual boot files, and adapters is a separate step whose full cold-boot procedure is still being consolidated.

## Android 9 (API 28) AOSP x86

**[Download the Android 9 x86 image — revision 4](https://dl.google.com/android/repository/sys-img/android/x86-28_r04.zip)**

This is an Android Emulator system image, not a Windows installer. The Android SDK tools register and run it.

1. Download [Android Studio or the SDK command-line tools](https://developer.android.com/studio).
2. Install the emulator, platform tools, and **Android 9 / API 28 AOSP x86** system image through SDK Manager.
3. Continue with the [Home launcher VM setup](../../vm/home/README.md#create-the-android-vm).

With the legacy SDK tools on PATH:

```powershell
sdkmanager "platform-tools" "emulator" "system-images;android-28;default;x86"
```

SDK Manager handles image installation automatically. The direct ZIP above is the revision used by this project, provided for manual setup. See the [SDK Manager documentation](https://developer.android.com/tools/sdkmanager) for tool installation and package management.
