#!/usr/bin/env python3
"""Inspect the *historical* PE Settings source only; NOT an Android17 build."""
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ANDROID = "{http://schemas.android.com/apk/res/android}"


def check(predicate: bool, message: str) -> None:
    if not predicate:
        raise AssertionError(message)
    print("PASS INVENTORY:", message)


def main() -> None:
    bp = (ROOT / "Android.bp").read_text(encoding="utf-8")
    check(bool(re.search(r'android_library\s*\{\s*name:\s*"Settings-core"', bp)),
          "historical Settings-core library exists")
    check(bool(re.search(r'android_app\s*\{\s*name:\s*"Settings"', bp)),
          "historical privileged Settings APK exists")
    for module in ('"faceunlock_framework"', '"vendor.lineage.fastcharge-V1.0-java"',
                   '"custom-preference"', '"SettingsLibDefaults"'):
        check(module in bp, f"old dependency present but NOT approved: {module}")
    check('"TouchGestures/res"' in bp, "old Settings depends on external TouchGestures resources")
    link = ROOT / "TouchGestures"
    check(link.is_symlink() and link.readlink().as_posix() == "../TouchGestures",
          "TouchGestures symlink resolves outside this source tree")
    check('"SettingsLibMetadata-processor"' not in bp,
          "historical graph lacks modern AOSP17 Settings metadata processor")
    check((ROOT / "src/com/android/settings/custom/touch/HighTouchPollingRateSettingsPreferenceController.java").is_file(),
          "legacy high-touch HAL controller available for *review*")
    fast = (ROOT / "src/com/android/settings/fuelgauge/FastChargingPreferenceController.java").read_text()
    check("vendor.lineage.fastcharge.V1_0.IFastCharge" in fast,
          "old charge toggle binds obsolete, unverified HIDL fastcharge API")
    wifi = (ROOT / "src/com/android/settings/wifi/tether/WifiTetherApBandPreferenceController.java").read_text()
    check("mWifiManager.is5GHzBandSupported()" in wifi,
          "old WiFi country-code guard removal needs review; do NOT port")
    manifest = ET.parse(ROOT / "AndroidManifest.xml").getroot()
    check(manifest.get("package") == "com.android.settings", "Settings package")
    check(any(x.get(ANDROID + "name") == "com.android.settings.FACE_UNLOCK" for x in manifest.findall("permission")),
          "old app-defined face permission exists; not approved for AOSP17")
    print("PASS: historical Settings source inventory only. AOSP17 Soong and mondrian NOT TESTED.")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, ET.ParseError) as exc:
        print("FAIL:", exc, file=sys.stderr)
        sys.exit(1)
