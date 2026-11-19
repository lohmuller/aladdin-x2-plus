# Custom applications and APKs

The project is intended to include independently developed applications, their source, and installable APK releases for Aladdin X2 Plus experiments and diagnostics.

## Planned applications

| Application | Status |
| --- | --- |
| Projection Diagnostics | Planned addition; current name is provisional and will be reconsidered before publication |

No application source or APK for Projection Diagnostics is included in this documentation update. Its features, permissions, supported firmware, build procedure, and validation results will be documented when the application is added.

## Distribution

For each published application, document its package name, version, requested permissions, compatibility, build steps, and whether it was tested on the physical device or only in a VM. Installable APKs can be distributed as project release assets with checksums; generated APKs remain ignored in the source tree.

Project applications are distinct from extracted OEM APKs or repackaged firmware. Private signing keys, passwords, device identifiers, and proprietary firmware components are not part of the public distribution. Installing a separate diagnostic app does not grant it system privileges or authorize replacement of factory applications.
