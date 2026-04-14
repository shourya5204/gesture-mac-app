#!/bin/bash

set -euo pipefail

APP_NAME="Air Control"
APP_BUNDLE="dist/${APP_NAME}.app"
DMG_PATH="${APP_NAME}.dmg"
IDENTITY="${DEVELOPER_ID_APP:-}"
NOTARY_PROFILE="${NOTARY_PROFILE:-}"
VERSION="${AIR_CONTROL_VERSION:-1.0.0}"
BUILD="${AIR_CONTROL_BUILD:-$VERSION}"
ENTITLEMENTS="AirControl.entitlements"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

sign_binary() {
  local path="$1"
  codesign \
    --force \
    --sign "$IDENTITY" \
    --timestamp \
    --options runtime \
    "$path"
}

sign_app() {
  echo "Signing nested binaries"
  while IFS= read -r path; do
    sign_binary "$path"
  done < <(
    find "$APP_BUNDLE" \
      \( -name "*.so" -o -name "*.dylib" -o -perm -111 \) \
      -type f \
      | sort
  )

  echo "Signing app bundle"
  codesign \
    --force \
    --deep \
    --sign "$IDENTITY" \
    --timestamp \
    --options runtime \
    --entitlements "$ENTITLEMENTS" \
    "$APP_BUNDLE"
}

verify_signature() {
  echo "Verifying code signature"
  codesign --verify --deep --strict --verbose=2 "$APP_BUNDLE"
  spctl --assess --type execute --verbose=4 "$APP_BUNDLE"
}

notarize_dmg() {
  echo "Submitting DMG for notarization"
  xcrun notarytool submit "$DMG_PATH" --keychain-profile "$NOTARY_PROFILE" --wait

  echo "Stapling notarization ticket"
  xcrun stapler staple "$APP_BUNDLE"
  xcrun stapler staple "$DMG_PATH"
}

require_command "./venv/bin/pyinstaller"
require_command "codesign"
require_command "xcrun"
require_command "hdiutil"
require_command "spctl"

if [[ -z "$IDENTITY" ]]; then
  echo "Set DEVELOPER_ID_APP to your Developer ID Application certificate name." >&2
  exit 1
fi

if [[ -z "$NOTARY_PROFILE" ]]; then
  echo "Set NOTARY_PROFILE to your notarytool keychain profile name." >&2
  exit 1
fi

export AIR_CONTROL_VERSION="$VERSION"
export AIR_CONTROL_BUILD="$BUILD"

echo "Building app bundle"
./venv/bin/pyinstaller -y "Air Control.spec"

sign_app
verify_signature

echo "Creating DMG"
hdiutil create -volname "$APP_NAME" -srcfolder "$APP_BUNDLE" -ov -format UDZO "$DMG_PATH"

notarize_dmg

echo "Release complete"
echo "App: $APP_BUNDLE"
echo "DMG: $DMG_PATH"
