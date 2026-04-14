# Air Control macOS Release

This project can now be signed and notarized with Apple's current `notarytool`
workflow.

## Prerequisites

- Apple Developer membership
- A valid `Developer ID Application` certificate installed in Keychain
- Xcode command line tools installed
- App-specific keychain profile stored for `notarytool`

## One-time notarytool setup

Create a keychain profile once:

```bash
xcrun notarytool store-credentials "AirControlNotary" \
  --apple-id "you@example.com" \
  --team-id "YOURTEAMID" \
  --password "app-specific-password"
```

You can list signing identities with:

```bash
security find-identity -v -p codesigning
```

## Build, sign, notarize

Run:

```bash
DEVELOPER_ID_APP="Developer ID Application: Your Name (TEAMID)" \
NOTARY_PROFILE="AirControlNotary" \
AIR_CONTROL_VERSION="1.0.0" \
AIR_CONTROL_BUILD="1.0.0" \
./release_macos.sh
```

Outputs:

- `dist/Air Control.app`
- `Air Control.dmg`

The script:

- builds the app with PyInstaller
- signs nested libraries and the app bundle with hardened runtime
- verifies the signature
- creates the DMG
- submits the DMG with `notarytool`
- staples the notarization ticket to the app and DMG

## Notes

- Other Macs may still show first-run permission prompts for Camera and
  Accessibility. That is expected.
- The bundle identifier is `com.aircontrol.app`.
- Version metadata is driven by `AIR_CONTROL_VERSION` and `AIR_CONTROL_BUILD`.
