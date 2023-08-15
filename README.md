# PlatformIO for the Parallax Propeller
PlatformIO platform to add support for the parallax propeller 1 and 2. Using the flexprop toolchain we can compile binaries and upload them using load-p2.

## Installation (GUI)
Must have GIT installed for platformio to properly download this platforms repository: https://git-scm.com/downloads
Navigate to PIO Home -> Platforms -> Advanced Installation

Enter the github url https://github.com/RileyMcCarthy/platform-propeller.git

![Screenshot](docs/PlatformIOInstallation.png)

## Installation (CLI)

```
pio pkg install --platform https://github.com/RileyMcCarthy/platform-propeller.git
```

## Packages

https://github.com/RileyMcCarthy/toolchain-flexprop

https://github.com/RileyMcCarthy/tool-loadp2
