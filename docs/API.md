# Aladdin APIs

HTTP requests identified in Aladdin X2 Plus V2.6.72, Home `2.6.21.20240118`, and Aladdin Store `2.2.2.221215`. All requests below use **GET**. Parameters describe what the examined clients send; the server may not require every field.

## System Update

| URL | Parameters | Purpose / response | Called by |
| --- | --- | --- | --- |
| `https://aladdin-api.xgimi.com/api/update` | `type=rom`, `gimiPid`, `systemVersion`, `androidVersion`, `model`, `modelName` | Firmware offer: version, release notes, ZIP URL and MD5. | Firmware update workflow; reproduced by the OTA diagnostic tool. The exact OEM caller has not been traced. |

See [firmware update parameters and examples](UPDATES.md).

## Aladdin Store

**Store metadata:** `osvn`, `brand`, `model`, `os`, `lang`, `platform`, `vcode`, `m`, `pkg`, `lvcode`, `gvcode`. `pkg` normally identifies the Store; app-specific requests replace it with the target package.

| URL | Parameters | Purpose / response | Called by |
| --- | --- | --- | --- |
| `https://aladdin-api.xgimi.com/api/tvstore` | Store metadata | App catalogue, including package names, versions, `apk_url` and `md5`. | Store → App Selection (`StoreFragment`). |
| `https://aladdin-api.xgimi.com/api/update` | Store metadata + `type=app`, `uid` | App updates, including Home. Entries contain `pkg`, `vname`, `vcode`, `url`, `md5` and `filesize`. | Store → My Apps / updates (`ManagerFragment` → `HttpHelper.i`). |
| `https://aladdin-api.xgimi.com/api/store/getappinfo` | Store metadata with target `pkg` | Details for an app's Store page. A successful response can still have empty app fields. | Store app-details screen (`AppDetailActivity`). |
| `https://aladdin-api.xgimi.com/api/store/checkversion` | Store metadata with target `pkg` + `version`, `versionName` | Version/availability check for the selected app; not a substitute for the APK update feed. | Store app-details screen (`AppDetailActivity`). |

**Home APK updates come from `api/update?type=app`, not necessarily the Store catalogue.** See [download Home and check for newer versions](../vm/home/README.md#find-a-newer-home-version).

## Home

**Home metadata:** `uid`, `lang`, `os`, `osvn`, `brand`, `model`, `m`, `lvcode`. This helper uses language-country, such as `ja-JP` or `en-US`.

| URL | Parameters | Purpose / response | Called by |
| --- | --- | --- | --- |
| `https://aladdin-api.xgimi.com/api/launcher/tablist` | Home metadata + cached `md5` when available | App categories, names, package lists and deeplinks. Can refresh the private `.AppDetailInfo` cache. | Home catalogue loader → `RequestApi.f`. |
| `https://aladdin-api-jp.xgimi.com/aladdin/api/home/tab_recommend` | Home metadata | Recommended content and tabs (`TabRecommend`). | Home recommendations → `RequestApi.k`. |
| `https://aladdin-api.xgimi.com/api/launcherad` | Home metadata | Splash advertising data (`SplashAdInfo`). This is an explicit advertising endpoint. | Home advertising components: `SplashAdView` and `SplashDownloader` → `RequestApi.i`. |
| `https://aladdin-api-jp.xgimi.com/api/rec/aladdin_today/list` | `postcode` query + Home HTTP headers below | Aladdin Today news/content (`NewsListBean` list). | Home → `HomeRequestApi.c`. |
| `http://aladdin-api.xgimi.com/api/launcher/hotvideos` | `t`, `limit=20` + Home HTTP headers below | Hot/recommended video list. The meaning of `t` depends on the calling video provider. | Home video/deeplink providers, including `YouTubeDpLink` → `HomeRequestApi.a`. |
| `https://aladdin-api.xgimi.com/api/launcher/checkwidevine` | Home metadata | Widevine-related check (`WidevineResponse`). | Home's `WidevineFix` → `RequestApi.l`. |

**Home HTTP headers:** `HTTP_X_API_VERSION=5`, `HTTP_X_CLIENT_PLATFORM`, `osvn`, `brand`, `os`, `lang`, `platform=android`, `uid`, `model`. Here `lang` is a language code such as `ja`, rather than `ja-JP`. The `hotvideos` HTTP URL is reproduced as declared in the app.

Home downloads categories, advertising and other recommendations separately. These are not all the same request, and not every banner is an advertisement. The exact mapping of visible banners and network-reconnection triggers is not fully traced.

## Example client values

| Field | X2 Plus example |
| --- | --- |
| `osvn` / firmware `systemVersion` | `V2.6.72` |
| `brand` | `XGIMI` |
| `model` | `popIn Aladdin 2 Plus` |
| `os` / firmware `androidVersion` | `28` / `Android9` |
| Store `vcode` / Home `lvcode` | `1003` / `1021` |
| Store `gvcode` | `0` in the tested app-update query |

`uid`, `m` and `gimiPid` are different identifiers; do not substitute one for another. The Store can generate a UUID for its `uid`. Firmware `gimiPid` comes from the projector's factory identifier.

These are vendor services and can change independently of the firmware. This is an index of identified requests, not a complete inventory of account, telemetry, media, or device-control APIs. Local Binder commands are documented separately in the [V2.6.72 reference](firmware/v2.6.72/README.md).

<details>
<summary>Home request examples, headers and response fields</summary>

## Tab catalogue: `api/launcher/tablist`

The client uses a GET request with a query map. The common fields are assembled by the original `RequestApi` class:

| Query field | Client value/source | Example or interpretation |
| --- | --- | --- |
| `uid` | Identifier returned by the application's device helper | Private device value; omitted here |
| `lang` | Locale language and country joined by a hyphen | `ja-JP` or `en-US` |
| `os` | Android SDK integer converted to text | `28` |
| `osvn` | `Build.VERSION.INCREMENTAL` | `V2.6.72` |
| `brand` | `Build.BRAND` | `XGIMI` in the firmware properties |
| `model` | `Build.MODEL` | `popIn Aladdin 2 Plus` |
| `m` | Network hardware-address value passed through the client's MD5 helper, or empty | Device-derived; omitted here |
| `lvcode` | Client constant `0x3fd` | `1021` for the examined Home |
| `md5` | Added when a cached-catalogue hash argument is available | Optional in this client path |

Illustrative X2 Plus request with private identifiers replaced:

```http
GET /api/launcher/tablist?uid=DEVICE_UID&lang=ja-JP&os=28&osvn=V2.6.72&brand=XGIMI&model=popIn%20Aladdin%202%20Plus&m=DEVICE_DERIVED_VALUE&lvcode=1021 HTTP/1.1
Host: aladdin-api.xgimi.com
```

The response is deserialized as an application response containing `AppDetailInfo`. The client model includes `md5`, `tabInfos`, `deeplinkInfos`, and `updateInfos`; each tab has `tabId`, `tabName`, and `pkgNames`.

This **illustrative subset** shows the structure, not a captured current server response:

```json
{
  "code": 200,
  "data": {
    "md5": "CATALOGUE_HASH",
    "tabInfos": [
      {
        "tabId": "5",
        "tabName": "キッズ",
        "pkgNames": []
      }
    ],
    "deeplinkInfos": [],
    "updateInfos": []
  },
  "message": "ok"
}
```

The launcher can save the catalogue as `.AppDetailInfo` in its private files directory, normally `/data/user/0/cc.popin.aladdin.home/files/`. The source names `.ConfigInfo` and `.NewConfigInfo` also occur in its configuration helper; their names do not imply identical formats or permissions.

**Localization consequence:** a downloaded catalogue can restore Japanese names after a local edit. Tab visibility also depends on installed or internally supplied applications. The cache's existence in a VM does not establish that an ordinary app or SFTP server can edit it on the physical projector.

## Recommendations: `aladdin/api/home/tab_recommend`

The original `NetworkConfig` constructs this URL from `https://aladdin-api-jp.xgimi.com/`. `RequestApi.k()` builds the same common query metadata listed above and calls the request method that deserializes `Response<TabRecommend>`. The catalogue-specific `md5` argument is not added in this method.

`TabRecommend` contains `contents` and `tabs`, with nested recommendation/media models. These supply dynamic Home content and are separate from the list of installed-app categories. Earlier local analysis identified a five-minute refresh guard on the recommendation path; it must not be treated as a universal polling interval for `tablist` or all Home networking.

The complete response schema and mapping from recommendation items to individual banners are not yet documented.

## Aladdin Today and HTTP headers

`HomeRequestService` identifies a GET endpoint at:

```text
https://aladdin-api-jp.xgimi.com/api/rec/aladdin_today/list
```

Its query map contains `postcode`, taken from the client's saved postal-code setting. The request uses `HeadersInterceptor` with the following fields assembled by `HomeRequestApi`:

| HTTP header | Client value/source |
| --- | --- |
| `HTTP_X_API_VERSION` | `5` |
| `HTTP_X_CLIENT_PLATFORM` | `Build.MODEL` |
| `osvn` | Incremental firmware version |
| `brand` | Android brand |
| `os` | Android SDK number as text |
| `lang` | `Locale.getDefault().getLanguage()`, e.g. `ja` |
| `platform` | `android` |
| `uid` | Private application/device identifier |
| `model` | `Build.MODEL` |

These header names are copied exactly as identified in the client. Notice that `lang` here is a language code, while the tablist helper constructs language-country. Do not interchange those formats or assume these headers are attached to every endpoint.

Illustrative request, with location and device identifiers replaced:

```http
GET /api/rec/aladdin_today/list?postcode=YOUR_POSTAL_CODE HTTP/1.1
Host: aladdin-api-jp.xgimi.com
HTTP_X_API_VERSION: 5
HTTP_X_CLIENT_PLATFORM: popIn Aladdin 2 Plus
osvn: V2.6.72
brand: XGIMI
os: 28
lang: ja
platform: android
uid: DEVICE_UID
model: popIn Aladdin 2 Plus
```

The response model is a response containing a list of `NewsListBean` items. We have not independently established the server's minimum required header set or published a validated response schema for this endpoint.

</details>
