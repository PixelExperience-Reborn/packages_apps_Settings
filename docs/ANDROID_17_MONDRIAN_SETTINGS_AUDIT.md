# P1 — packages/apps/Settings Android 17 / mondrian migration audit

Date: 2026-11-04. Status: **AUDIT ONLY; historical Android14 Settings NOT PORTED OR SELECTED IN AOSP17 MANIFEST**.

## Source provenance

- Historical PixelExperience-Reborn branch `seventeen`: commit `6d846522332a0e61a445151d5048d1d71c204376`; the source history includes the Android14 r21 merge `513270533eb2c9` (2024-01-30) and older PixelExperience/LineageOS patches.
- **AOSP17 r1** `platform/packages/apps/Settings`: official commit `213829fb67f5e070029e0513a088f31bc8f5c1ed`, tree `f41bf360ab496bb4c018a33f93b74858b8ed223c`. Source: https://android.googlesource.com/platform/packages/apps/Settings/+/refs/tags/android-17.0.0_r1
- Active staged manifest already selects `platform/packages/apps/Settings` at `packages/apps/Settings`. Replacing it with the historical `seventeen` repo is NOT approved.

## Actual architectural changes

Official AOSP17 `Android.bp` builds the privileged `Settings` APK from `Settings-core`, but introduces/depends on major new architecture: `SettingsLibMetadata-processor`, `androidx.room_room-compiler-plugin`, AConfig flag modules, `Spa-search`, `SettingsInterfaceLib`, `settings-api-registry`, Java/Kotlin source processors, modern `SettingsLib` and multiple new platform APIs. Its `Settings-core` uses `SettingsLib-search-defaults`, `SettingsLintDefaults`, `SpaPrivilegedLib-defaults` and updated static libraries. It also adds `RELEASE_SETTINGS_ENABLE_OPTIMIZE` and NullAway/ErrorProne configuration.

The historical PE `Android.bp` instead declares older `SettingsLibDefaults`, a `TouchGestures/res` resource directory, `custom-preference`, `faceunlock_framework`, and `vendor.lineage.fastcharge-V1.0-java` static libraries. Its `TouchGestures` symlink points at `../TouchGestures`, the separate historical `packages/apps/TouchGestures` project. **These are source-graph dependencies, not standalone settings labels**. A `sdk_version` edit or wholesale source replacement cannot resolve them.

## Historical PE changes, evidence and disposition

| Old commit | Function | Disposition |
| --- | --- | --- |
| `507a4709f8bdcf160fe198d1edece528e43f0078` | PE Face Unlock settings; custom manifest permission and `faceunlock_framework` | **BLOCKED**: the historical FaceUnlockService is separately security-blocked. Do not restore old biometric intents, permissions or capability assertions in Android17 Settings. |
| `66dbf9ca602abef35127bf86af18189bdb7d9d16` | Fast charging toggle using HIDL `vendor.lineage.fastcharge@1.0` | **DEFER**: no compatible mondrian service has been verified. Cannot add an orphan toggle or unresolved Soong dependency. |
| `6ff2bbcb46603862ef96ba0fbf214c252a297e52` | Lineage-style charging control preferences | **REVIEW** against existing `vendor.lineage.health-service.default`, AIDL ownership, config and planned feature scope. Do not claim integrated health feature. |
| `7b18a5b21673c5ae6582dddd44dfe6795957df5d` | High touch polling switch via `LineageHardwareManager.FEATURE_HIGH_TOUCH_POLLING_RATE` | **REVIEW** hardware support and any existing device-side controls before implementing anything twice. |
| `aa4651b48f1856d2daf345e34343465528aff494` | Peak refresh rate logic constrained by `config_defaultPeakRefreshRate` | **REVIEW** Android17 DisplayManager/Settings controllers and existing mondrian display mode behavior. Never copy older controllers blind. |
| `6d846522332a0e61a445151d5048d1d71c204376` | Conditionally hide display color-inversion setting via overlay | **LOW RISK CANDIDATE ONLY** after confirming current AOSP17 controller and resource; do not change defaults without requirements. |
| `50c0bc1ed254cebae36c0abd3d23357d9db13459` | Removes Wi-Fi hotspot 5 GHz country-code guard | **REJECT**; potential regulatory and invalid-band behavior. Preserve official Android17 platform checks. |
| `2d6985bdbe979a2eecf18090adf2b3d1fd7c59dd` | Validate ringtone URI across users and profile groups | **SECURITY CRITICAL**: check upstream AOSP17 code/tests first; do not overwrite newer checks with Android14 patch. |
| `9e78b8c0843787260581fdb4d0b9cee5e1b22b25` | Block work-profile notification-listener privilege escalation | **SECURITY CRITICAL**: verify AOSP17 policies and behavior; preserve all modern protections. |

There are many further historical PE changes. These identified rows are a **prioritized sample, not a complete patch-by-patch audit**. Full source history/diff classification is still required before any claim that all PE Settings features have been ported.

## Source and device integration gates

- [x] Identify old PE revision and official AOSP17 tag/commit/tree.
- [x] Identify incompatible Soong graph and `TouchGestures` external resource path.
- [x] Identify high-impact old patches and the blocked biometric/regulatory changes.
- [x] Preserve official AOSP17 Settings in all staged manifest profiles, with a structural source guard.
- [x] Host-only regression tests of historical presence and blockers (inventory, **not** AOSP17 app test).
- [ ] Enumerate and classify **all** historical Settings non-upstream commits, conflicts and source dependencies; label AOSP17-already-fixed vs optional vs reject.
- [ ] Build and validate a genuine Android17 Settings baseline via `m Settings` with platform modules and AConfig processors.
- [ ] Design optional PE functions as separate minimal patches with real Android17 APIs and mondrian overlays; each change needs unit/Soong/UI regression tests and clear source ownership.
- [ ] Confirm face-auth/FBE/security, runtime permissions, Setup Wizard, Settings search indexing, keyboard/display/controller lifecycles, quick settings, fast charging and user/profile boundaries.
- [ ] Test rotation, locales (RU/EN/UK as appropriate), large fonts, TalkBack, landscape, reboot persistence and GMS/no-GMS product behavior on mondrian.
- [ ] Only then consider a separate immutable, opt-in PE Settings profile and eventually promote it after full product integration.

## Decision

**No new Settings override in AOSP17 manifest.** This is a conservative build-preserving decision, not a claim that historical PE Settings work is complete. The old `seventeen` repository remains unchanged. The audit branch alters only `docs/`, `tools/`, and `.github/workflows/`; runtime sources are untouched.
