# VM architecture


The physical projector combines Android with hardware-specific services. QEMU provides a virtual machine, while a separate adaptation layer handles the differences between the projector and virtual hardware.

```mermaid
flowchart TB
    subgraph HOST["Host computer — Windows prototype"]
        TOOLS["Build and debugging tools"]
        VIEW["Desktop viewer and keyboard input"]
        subgraph VM["QEMU / Android Emulator — virtual ranchu board"]
            CPU["Virtual ARM64 CPU<br/>ARM32 compatibility"]
            BOOT["Virtual kernel and bootstrap"]
            ANDROID["Aladdin Android 9 ARM32<br/>System, product and ODM components"]
            HOME["Original Aladdin Home<br/>and selected system applications"]
            ADAPT["VM adaptation layer<br/>Virtual graphics and native adapters<br/>Minimal XGIMI Binder stand-ins"]
            CAPTURE["Resident frame capture<br/>and virtual input"]
            CPU --> BOOT
            BOOT --> ANDROID
            ANDROID --> HOME
            ADAPT --> ANDROID
            ANDROID --> CAPTURE
        end
        TOOLS -. "ADB: inspect and stage VM files" .-> ANDROID
        CAPTURE -->|"Frames over local ADB forwarding"| VIEW
        VIEW -->|"Directional keys, OK and Back"| CAPTURE
    end
    INPUT["User-supplied firmware files<br/>Kept outside this repository"] -. "Offline extraction" .-> ANDROID
```

This is an adaptation environment built around QEMU, rather than a new QEMU implementation. The Windows host runs the emulator; Android applications and native libraries execute as ARM code inside the VM.

### Original components and VM adaptations

| Layer | Approach in the local prototype |
| --- | --- |
| Firmware inputs | Original OTA archive retained separately; extracted components used as inputs |
| Home application | Original APK preserved in the ARM prototype |
| Boot | Virtual kernel and bootstrap replace the physical boot environment |
| Graphics | Virtual EGL/gralloc libraries with targeted compatibility adjustments |
| Native hardware integration | Small VM-only adapters avoid calls that require absent projector services |
| XGIMI Binder interfaces | Minimal stand-ins provide default responses; they do not reproduce the hardware |
| Audio, codecs and storage | A mixture of original components, virtual backends, and manual setup |
| Display and controls | Custom frame viewer and virtual keyboard events |

The native adapters cover FactoryManager, SystemManager, MusicPlayerManager, and ConfigManager. Their local build checks input/output hashes and the intended byte changes. These adaptations are specific to the studied binaries and are not general firmware patches.

