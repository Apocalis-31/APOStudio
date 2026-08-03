# APO Studio — Agent Instructions

## Release Process

Before creating a release tag, ensure these steps are done in order:

### 1. Bump version in all files
- `src/app_info.py` → `VERSION = "X.Y.Z"`
- `installer/version.txt` → same version string
- `installer/changelog.txt` → **add new section at top** with vX.Y.Z changes (this is the release notes body shown on GitHub)

⚠️ Ne pas oublier de mettre à jour `installer/changelog.txt` — c'est le corps de la release GitHub.

### 2. Regenerate version info
```bash
.venv\Scripts\python.exe tools/generate_version_info.py
```
This updates `version_info.txt` and the `.iss` installer scripts.

### 3. Commit and push
```bash
git add -A
git commit -m "chore: version X.Y.Z"
git push origin main
```

### 4. Create and push tag
```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```
The GitHub Actions workflow `Build & Release` runs automatically on tag push.

### 5. Patch zip
The workflow automatically creates `APOStudio_Patch_vX.Y.Z.zip` **only if** the previous release has a `manifest_v*.json` asset. If the previous release was published before the manifest system, the patch zip will be skipped (this is expected).

**Important:** The patch zip can only be created by the CI workflow (it needs the `dist/Apo Studio CPU/` build artifacts). It cannot be created manually from a dev machine because the CPU build requires Windows + PyInstaller. Do NOT try to create a patch zip locally using the GPU build — it will produce a full-size zip (~800+ MB) instead of a proper diff patch.

If a patch zip is missing for a release, the next release (N+1) will automatically create it since the manifest for release N will then be available in the release assets.

### Key files
- `src/app_info.py` — source of truth for VERSION
- `tools/generate_version_info.py` — regenerates `version_info.txt` and updates `.iss` files
- `tools/patch_builder.py` — computes file diff between manifests
- `tools/patch_packager.py` — creates the patch `.zip`
- `installer/changelog.txt` — release notes body
- `installer/version.txt` — installer version string

## Workflow Notes
- The CI workflow is in `.github/workflows/build.yml`
- It triggers on any `v*` tag push or manual workflow dispatch
- Build variants: GPU and CPU
- Release assets: `APOStudio_Setup_*.exe`, `APOStudio_Patch_*.zip`, `manifest_v*.json`