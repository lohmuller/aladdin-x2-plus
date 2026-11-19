# Publishing this source package

The repository-ready package contains only the reviewed source and documentation. It does not include the original study directory, firmware, generated binaries, or private inputs.

## Upload through GitHub

If the repository has no initial commit, use its **uploading an existing file** link. Otherwise choose **Add file → Upload files**. Extract the source ZIP locally and upload its contents, preserving `docs/`, `vm/`, `apps/`, and `patchs/`.

Upload the package contents with `README.md` at the root. The license is in `docs/LICENSE`; folder-specific `.gitignore` files should be preserved. GitHub's file upload interface does not apply local `.gitignore` rules, so use only the reviewed package rather than selecting the original research folder.

Review the final file list before committing. No APK, firmware archive, disk image, compiled library, key, personal log, or generated OEM code should appear. Suggested commit message: `Publish Aladdin X2 Plus VM research tools and documentation`.

## Publish with Git

Alternatively, clone the repository using a credential with permission to write repository contents, then copy the package contents into that clone. Inspect any existing files and changes before replacing them.

Before staging, inspect `git status --short --branch`, `git diff`, and `git diff --cached`. Stage only the reviewed files:

```text
git add README.md docs vm apps patchs
git diff --cached --stat
git diff --cached
git commit -m "Publish Aladdin X2 Plus VM research tools and documentation"
git push origin main
```

These commands assume a clean clone on `main`, no unrelated staged changes, and configured Git author information. Do not force-push an existing repository.

## Publication boundary

The `.gitignore` reduces accidental staging; it does not remove files already tracked and does not make any third-party material publishable. Build outputs and extracted firmware remain private. The MIT license applies to original material in this source package, with third-party licenses remaining separate.
