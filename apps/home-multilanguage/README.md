# Home Launcher English

English text resources for the Aladdin X2 Plus Home launcher (`cc.popin.aladdin.home`).

## Files

| File | What it translates |
| --- | --- |
| [strings.xml](res/values-en/strings.xml) | 104 Android text resources: settings, keystone, postal code, audio, and other interface labels |
| [app_config_US.json](assets/app_config_US.json) | Card titles and descriptions for the US catalogue |

These are source files for an APK build. Copying them to the projector's storage does not change the launcher. A ready-to-install English Home APK is not provided here.

## How localization works

- **Interface text:** `res/values-en/strings.xml` is compiled into the APK's `resources.arsc`.
- **Card text:** the launcher selects `assets/app_config_<COUNTRY>.json`, falling back to `app_config.json`. The US file is selected for `en-US`; other English regions need their own handling.
- **Tab names:** a downloaded `.AppDetailInfo` catalogue can replace local names. See [runtime APIs](../../docs/API.md).

The files cover part of the launcher, not every screen or app. Native settings in `com.android.newsettings`, images, and online content need separate localization.

## Compatibility

The work targets Home `2.6.21.20240118` and firmware V2.6.72. English layouts were tested in generic Android VMs. The ARM firmware VM uses its original Home APK.

A VM test signature does not make an APK a valid update to the projector's factory launcher. Keep resource identifiers, format placeholders, escapes, and JSON structure intact when building a translated version.
