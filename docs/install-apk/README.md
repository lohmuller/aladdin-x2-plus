# How to install an APK on Aladdin X2 Plus

Install a separate app through the projector's **network remote-control service (VControl)**. This protocol was tested with a diagnostic APK on firmware V2.6.72; a reusable installer client is not yet provided.

## What you need

- The PC and projector on the same reachable local network; use their current IP addresses.
- An APK suitable for the projector's Android 9 / API 28 environment and reported app ABI where native code is involved.
- An HTTP URL from which the projector can download that APK. The PC must keep the file available until the projector finishes downloading it.
- A client capable of sending the JSON request below and listening for its responses.

Keep the official **Aladdin X phone app connected to the projector** for this workflow. Whether it is required for pairing remains unverified. The PC sends the installation request directly to the projector.

## Installation steps

1. Connect the projector and PC to the same LAN. Open Aladdin X on the phone, select the projector, and confirm the normal remote buttons work.
2. Serve the intended APK at an HTTP URL reachable by the projector. Keep the file server available for the download, then stop it after the operation.
3. Bind the PC's UDP response listener to **16751** before sending. Responses return to this fixed port.
4. Send the request as UTF-8 JSON to **UDP 16750 on the projector**.
5. Observe the download and installation messages, then confirm the installed app and actual launch separately.

## Installation request

Example for the diagnostic package. Replace the URL, package name, and version fields to match your APK:

```json
{
  "action": 30200,
  "msgid": "diagnostic-install-example",
  "packageName": "org.aladdinstudy.systeminfo",
  "version": "1.1",
  "customPlay": {
    "mediatype": 3,
    "pos": 0,
    "playlist": [{
      "url": "http://YOUR_PC_IP:PORT/AladdinSystemInfo.apk",
      "title": "AladdinSystemInfo",
      "packagename": "org.aladdinstudy.systeminfo",
      "versioncode": "2",
      "mimetype": ".apk",
      "iconurl": ""
    }]
  }
}
```

Set the protocol's `mimetype` to **`.apk`**. The HTTP Content-Type is separate and can be `application/vnd.android.package-archive`.


## Responses and opening the app

| Response | Meaning |
| --- | --- |
| `30234`, download progress `100` | APK download reached 100% |
| `30231`, installation notification with `stat: 1` | The service reported installation success |
| `30232`, opening notification with `stat: 1` | The service reported that the open-app request succeeded |

Open the app with a separate request:

```json
{
  "action": 20000,
  "msgid": "diagnostic-open-example",
  "controlCmd": {
    "mode": 7,
    "type": 1,
    "data": "org.aladdinstudy.systeminfo"
  }
}
```

Check that the expected app version is installed and its screen opens. The service's `installInfo` label can appear in an open-app response; use the action code and operation context to distinguish them.

## Limits and other routes

- VControl is distinct from ADB, SFTP, local Binder APIs, and the [firmware update API](../UPDATES.md).
- An app installed through this service does not inherit the installer's privileges or bypass signature compatibility for factory apps.
- SFTP transfers files; it does not by itself install an APK or grant access to Home's private files.
- The phone's pairing/authorization role and a complete reusable installation client remain open work.
