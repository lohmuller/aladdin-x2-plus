# Aladdin Home Launcher in a VM

Run the Aladdin Home launcher in a generic **Android 9 x86 VM on 64-bit Windows**.

## Downloads

| Download | Source |
| --- | --- |
| Android Studio / SDK tools | [Official Android downloads](https://developer.android.com/studio) |
| Android 9 / API 28 AOSP x86, revision 4 | [Official Google ZIP](https://dl.google.com/android/repository/sys-img/android/x86-28_r04.zip) · [SDK installation](../../docs/downloads/README.md#android-9-api-28-aosp-x86) |
| Original Home 2.6.41.20261029 | [Download APK](https://aladdin.static.xgimi.com/packages/app/launcher_release_jp_aladdin_gen2_v2_20261029135127.6.41.20261029_202610291202.apk) |

| APK field | Value |
| --- | --- |
| Package | `cc.popin.aladdin.home` |
| Version / versionCode | `2.6.41.20261029` / `1041` |
| Size | 40,357,754 bytes |
| MD5 reported by the API | `3487ab953283cb8e79f1bbe8b65d9dd9` |

**This is the original APK, not a VM-adapted build.** Its compatibility with this x86 setup has not been verified. A compatible adapted Home build is still required and is not yet published here.

<details>
<summary>Home version bundled with the firmware</summary>

The [V2.6.72 firmware](../../docs/downloads/README.md#aladdin-x2-plus-v2672-firmware) contains the older Home `2.6.21.20240118`. Extract its vendor partition to find `/priv-app/Aladdin_Launcher/Aladdin_Launcher.apk`, mounted as `/vendor/priv-app/Aladdin_Launcher/Aladdin_Launcher.apk` on Android.

</details>

## Requirements

- Windows x86-64 and Android SDK tools compatible with the legacy API 28 image.
- Android 9 / API 28 **AOSP x86**, revision 4 for the original configuration.
- A supported hypervisor for x86 acceleration, if available.
- A compatible **VM-adapted Home APK**; English XML/JSON files alone are not an installable app.

## Create the Android VM

Use a separate AVD with a landscape display. With compatible legacy SDK tools on PATH:

```powershell
sdkmanager "platform-tools" "emulator" "system-images;android-28;default;x86"
avdmanager create avd -n Aladdin_Home_App9 -k "system-images;android-28;default;x86"
```

Choose an unused emulator port. This example uses 5570 and a separate ADB server on 5039:

```powershell
$env:ANDROID_ADB_SERVER_PORT = '5039'
adb -P 5039 start-server
emulator -avd Aladdin_Home_App9 -port 5570
```

Current Android tooling also offers a newer CLI; these commands use the legacy toolchain. See [AVD creation](https://developer.android.com/tools/avdmanager).

## Install and open Home

Once Android has booted, open a second terminal and check the guest:

```powershell
adb -P 5039 -s emulator-5570 shell getprop ro.build.version.sdk
adb -P 5039 -s emulator-5570 shell getprop ro.product.cpu.abi
```

For this setup, the values should be `28` and `x86`. Supply your compatible adapted APK in place of the placeholder:

```powershell
adb -P 5039 -s emulator-5570 install "YOUR_VM_ADAPTED_HOME.apk"
adb -P 5039 -s emulator-5570 shell am start -n cc.popin.aladdin.home/cc.popin.aladdin.splash.ui.SplashActivity
```

See the [Android Emulator command-line guide](https://developer.android.com/studio/run/emulator-commandline) for SDK options.

## What to expect

This approach supports UI and translation testing, including settings layouts and tab labels. It does not boot the projector's ARM32 firmware or reproduce its hardware services. Installing an unmodified projector APK into a generic image is not a substitute for the missing adaptation recipe.

Native settings, media, XGIMI services, and permissions can behave differently from the projector. Physical Wi-Fi, optics, calibration, and firmware installation are outside this VM's coverage.

## Find a newer Home version

The Store's **My Apps → Update** screen uses `api/update?type=app`. Unlike the public store catalogue, this feed can include Home updates. Its download field is **`url`**, not `apk_url`.

<details>
<summary>Check Home updates from PowerShell</summary>

This example uses X2 Plus/V2.6.72 client metadata and a fresh random UUID. It does not send a personal serial number, require a login, or download/install an APK.

```powershell
$params = @{
    type = 'app'
    uid = [guid]::NewGuid().ToString()
    pkg = 'cc.popin.aladdin.appstore'
    osvn = 'V2.6.72'
    brand = 'XGIMI'
    model = 'popIn Aladdin 2 Plus'
    os = '28'
    lang = 'ja'
    platform = 'android'
    vcode = '1003'
    lvcode = '1021'
    gvcode = '0'
}
$query = ($params.GetEnumerator() | ForEach-Object {
    '{0}={1}' -f $_.Key, [Uri]::EscapeDataString([string]$_.Value)
}) -join '&'
$result = Invoke-RestMethod -Uri ("https://aladdin-api.xgimi.com/api/update?" + $query) -TimeoutSec 20
$result.data | Where-Object pkg -eq 'cc.popin.aladdin.home' |
    Select-Object vname, vcode, url, md5, filesize
```

Use the returned `vname` to identify the offered version and `url` for its APK. The response can change by client configuration and over time; the linked version above was returned on 19 November 2026.

</details>
