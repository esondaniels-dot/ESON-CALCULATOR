# ESON CALCULATOR 🇿🇲

A polished, offline Android calculator built with Python and Kivy. The app includes a safe expression parser, calculation history, copy-to-clipboard, dark/light themes, button feedback, and Android vibration feedback. No network permission or connection is required.

## Features

- Addition, subtraction, multiplication, division, decimals, percent, brackets and order of operations.
- Unary signs, square, square root, and exponentiation (including negative exponents).
- Division-by-zero and malformed-expression validation; expressions are parsed without Python `eval`.
- Calculation preview and persistent history (up to 100 entries); tap an entry to reuse its result.
- Copy the last calculated result, switch between dark and light themes, and tactile button feedback.
- Responsive Kivy layout and offline-first operation.

## Run locally

Python 3.9+ is recommended. On a desktop:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest -v
python main.py
```

Kivy may require platform-specific system packages; consult the official Kivy installation guide for your OS. The standalone parser and tests have no third-party dependencies.

## Build an Android APK

Buildozer is best run on Linux (or WSL2). Install the Android SDK/NDK and Buildozer prerequisites following the official Buildozer installation guide. Then:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install buildozer Cython==0.29.36
python -m unittest -v
buildozer android debug
```

The debug APK is written under `bin/`. First builds download the Android toolchain and can take some time. The project configuration requests Android API 35, minimum API 23, and 32/64-bit ARM. To install on a connected device with USB debugging enabled:

```bash
buildozer android debug deploy run
```

## Generate a signed release APK

Create a private signing keystore and keep it out of source control:

```bash
keytool -genkeypair -v -keystore eson-release.keystore -alias eson-calculator \\
  -keyalg RSA -keysize 2048 -validity 10000
```

Build a release APK, then sign and align it using the `apksigner` and `zipalign` tools supplied by the Android SDK. Example (adjust SDK build-tools version and paths):

```bash
buildozer android release
$ANDROID_HOME/build-tools/<version>/zipalign -f -v 4 bin/*-release-unsigned.apk bin/eson-calculator-aligned.apk
$ANDROID_HOME/build-tools/<version>/apksigner sign --ks eson-release.keystore \\
  --ks-key-alias eson-calculator --out bin/eson-calculator-release.apk bin/eson-calculator-aligned.apk
$ANDROID_HOME/build-tools/<version>/apksigner verify --verbose bin/eson-calculator-release.apk
```

Enter the keystore passwords when prompted. Never commit or share the keystore or passwords. Verify the generated APK with `apksigner verify` before distribution. APK generation/signing requires a configured local Android toolchain; no APK artifact is included in this repository.

## Controls

`AC` clears, `DEL` deletes the last typed character, `( )` inserts a bracket (or opens a multiplication group), `%` is postfix percent, `x²` squares, `√` starts a square-root expression, and `^` is exponentiation. `+/−` toggles the sign of the current number. The top icons open history, switch the theme, and copy a completed result.

## Project files

- `main.py` — Kivy interface, interaction, history, themes, clipboard and haptics.
- `calculator.py` — safe tokenizer/parser and number formatting.
- `test_calculator.py` — arithmetic, precision, precedence and validation tests.
- `buildozer.spec` — Android packaging configuration.
