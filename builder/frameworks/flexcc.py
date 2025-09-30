"""
FlexCC Framework for Propeller platforms.
Uses the FlexC compiler toolchain for C/C++ development on Propeller chips.
"""

import os
import platform
from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform_instance = env.PioPlatform()
board = env.BoardConfig()

def get_platform_subdir():
    """Get the platform-specific subdirectory name based on current platform."""
    system = platform.system()
    arch = platform.machine()
    
    if system == "Windows":
        return "windows-amd64"
    elif system == "Darwin":  # macOS
        return "macos-amd64"
    elif system == "Linux":
        if arch in ["armv7l", "armv6l"]:  # Raspberry Pi
            return "raspberry-pi"
        else:
            return "linux-amd64"
    else:
        # Default to linux-amd64 for unknown platforms
        return "linux-amd64"

def get_loadp2_platform_subdir():
    """Get the platform-specific subdirectory name for LoadP2 tools."""
    system = platform.system()
    
    if system == "Windows":
        return "windows"
    elif system == "Darwin":  # macOS
        return "macos"
    elif system == "Linux":
        return "linux"
    else:
        # Default to linux for unknown platforms
        return "linux"

def get_executable_name(base_name):
    """Get the executable name based on the current platform."""
    system = platform.system()
    
    if system == "Windows":
        return f"{base_name}.exe"
    else:
        return base_name

def ensure_executable_permissions(executable_path):
    """Ensure the executable has execute permissions."""
    if os.path.exists(executable_path) and not os.access(executable_path, os.X_OK):
        try:
            import stat
            current_permissions = os.stat(executable_path).st_mode
            os.chmod(executable_path, current_permissions | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
            print(f"Added execute permissions to {executable_path}")
        except Exception as e:
            print(f"Warning: Could not add execute permissions to {executable_path}: {e}")

# Configure FlexCC toolchain
toolchain_path = platform_instance.get_package_dir("toolchain-flexcc")
platform_subdir = get_platform_subdir()
executable_name = get_executable_name("flexcc")

# Build paths using the new structure: bin/{platform}/{executable}
flexcc = os.path.join(toolchain_path, "bin", platform_subdir, executable_name)
flexprop_include_path = os.path.join(toolchain_path, "include")

# Ensure executables have proper permissions
ensure_executable_permissions(flexcc)
ensure_executable_permissions(os.path.join(toolchain_path, "bin", platform_subdir, get_executable_name("flexspin")))
ensure_executable_permissions(os.path.join(toolchain_path, "bin", platform_subdir, get_executable_name("spin2cpp")))

# Set up compilation environment
env.Replace(
    AS=flexcc,      # assembler
    CC=flexcc,      # C compiler
    CXX=flexcc,     # C++ compiler
)

# Add build flags
env.Append(
    CCFLAGS=["-2", "-Wall", "-O1", "--nostdlib", f"-I{flexprop_include_path}"],
    LINKFLAGS=["-2", "-Wall", "-O1", "--nostdlib", f"-I{flexprop_include_path}"],
)

# Configure LoadP2 uploader
loadp2_platform_subdir = get_loadp2_platform_subdir()
loadp2_executable = get_executable_name("loadp2")
uploader_path = platform_instance.get_package_dir("tool-loadp2")

# Configure uploader paths
uploader = os.path.join(uploader_path, "bin", loadp2_platform_subdir, loadp2_executable)
sdcard = os.path.join(uploader_path, "bin", "P2ES_sdcard.bin")
flash = os.path.join(uploader_path, "bin", "P2ES_flashloader.bin")

# Ensure LoadP2 executable has execute permissions
ensure_executable_permissions(uploader)

env.Replace(
    UPLOADER=uploader,
    SDCARD=sdcard,
    FLASH=flash,
    UPLOADERFLAGS=["-b230400"],
    UPLOADCMD="$UPLOADER $UPLOADERFLAGS $SOURCES",
)

# Configure upload protocols
upload_protocol = env.subst("$UPLOAD_PROTOCOL")

if upload_protocol.startswith("flash"):
    env.Replace(
        UPLOADERFLAGS=[
            "-t", "-v", "-b230400",
            '"@0=$FLASH,@8000+$SOURCES"',
        ],
        UPLOADCMD="$UPLOADER $UPLOADERFLAGS",
    )
elif upload_protocol.startswith("sdcard"):
    env.Replace(
        UPLOADERFLAGS=[
            "-t", "-v", "-b230400",
            '"@0=$SDCARD,@8000+$SOURCES"',
        ],
        UPLOADCMD="$UPLOADER $UPLOADERFLAGS",
    )
elif upload_protocol.startswith("serial"):
    env.Replace(
        UPLOADERFLAGS=["-t", "-v", "-b230400"],
        UPLOADCMD="$UPLOADER $UPLOADERFLAGS $SOURCES",
    )