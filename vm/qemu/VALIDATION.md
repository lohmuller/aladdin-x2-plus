# Validation record

## Historical VM evidence

The local prototype's recorded SystemUI regression report passed eight observations in 302.4 seconds, alternating Home and System Update with frame capture active and a constant SystemUI PID. Original Home navigation and rendering of System Update were visually observed in that study. Raw logs, screenshots, and device identifiers are not part of this source package.

This validates a particular configured session, not reproducible cold boot, complete hardware behavior, or current physical-device state.

## Packaging changes

The source inventory records SHA-256 hashes of each original local source and its packaged version. The package contains original study wrappers/generators, not QEMU source, extracted firmware source, or third-party executables.

Minimal packaging changes make the external input directory configurable with `ALADDIN_VM_INPUTS`, make the D8 JAR configurable with `ALADDIN_R8_JAR`, allow the existing tools setting in the regression script, ensure report directories exist, reject non-emulator serials in the sync helper, and correct the aggregate native-adapter count from two to four. The Binder generator rejects a missing/incomplete interface set early.

The SHA checks and native patch bytes were preserved. No VM bootstrap, physical-device operation, or application interface was changed during packaging. Results of host-side packaging checks are recorded separately in `packaging-checks.json` when completed.
