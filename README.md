# PlatformIO for the Parallax Propeller

PlatformIO platform for the Parallax Propeller P2 microcontroller. Uses the FlexCC compiler toolchain for C/C++ development and LoadP2 for firmware upload.

## Installation

### GUI Method
1. Navigate to PIO Home → Platforms → Advanced Installation
2. Enter the repository URL:
   ```
   https://github.com/RileyMcCarthy/platform-propeller.git
   ```

### CLI Method
```bash
pio pkg install --platform https://github.com/RileyMcCarthy/platform-propeller.git#v6.2.3
```

## Usage

Create a `platformio.ini` file in your project:

```ini
[env:propeller2]
platform = platform-propeller
board = EdgeModule
framework = flexcc
upload_protocol = flash     ; Options: flash, serial, sdcard
monitor_speed = 230400
```

## Features

- **FlexCC v7.4.3**: C/C++ compiler for Propeller P2 with multi-platform support
- **Platform Detection**: Automatically selects correct executables for Windows, macOS, Linux, and Raspberry Pi
- **LoadP2 Uploader**: Supports flash, sdcard, and serial upload protocols
- **Cross-Platform**: Works seamlessly across all supported platforms
- **Framework Support**: Extensible framework system for future toolchain support

## Packages

- **toolchain-flexcc**: FlexCC compiler toolchain
- **tool-loadp2**: LoadP2 firmware uploader
