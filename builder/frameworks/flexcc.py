"""
FlexCC Framework for Propeller platforms.
Uses the FlexC compiler toolchain for C/C++ development on Propeller chips.
"""

import os
import platform
from SCons.Script import DefaultEnvironment
from frameworks._loadp2 import setup_loadp2

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
            print(f"FlexCC: Added execute permissions to {executable_path}")
        except Exception as e:
            print(f"FlexCC: Warning - Could not add execute permissions to {executable_path}: {e}")

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
    CCFLAGS=[
        "-2",
        "-Wall",
        "-O1",
        "--nostdlib",
        f"-I{flexprop_include_path}"
    ],
    LINKFLAGS=[
        "-2",
        "-Wall",
        "-O1",
        "--nostdlib",
        f"-I{flexprop_include_path}"
    ],
)

# -----------------------------------------------------------------------------
# Add program size reporting
# -----------------------------------------------------------------------------
def print_program_info(source, target, env):
    """Display program size information after successful build."""
    program_path = str(target[0])  # Use target instead of source
    
    print("=" * 80)
    print("FlexCC: Program Build Information")
    print("=" * 80)
    
    # Get file size
    try:
        file_size = os.path.getsize(program_path)
        print(f"Program: {os.path.basename(program_path)}")
        print(f"Binary file size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
        
        # Calculate percentage of available memory from board config
        board_config = env.BoardConfig()
        ram_size = board_config.get("upload.maximum_ram_size", 524288)  # Default to 512KB if not specified
        percentage = (file_size / ram_size) * 100
        print(f"RAM usage: {percentage:.1f}% of {ram_size/1024:.0f} KB")
        
    except Exception as e:
        print(f"FlexCC: Warning - Could not get file size: {e}")
    
    print("=" * 80)

# Add the info display as a post-action to the program build
env.AddPostAction("$BUILD_DIR/${PROGNAME}$PROGSUFFIX", print_program_info)

# -----------------------------------------------------------------------------
# Configure LoadP2 uploader (using shared _loadp2.py module)
# -----------------------------------------------------------------------------
setup_loadp2(env, platform_instance)
