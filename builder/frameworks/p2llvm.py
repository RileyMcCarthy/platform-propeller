"""
P2LLVM Framework for Propeller platforms.
Uses the LLVM-based P2LLVM compiler toolchain with precompiled static libraries.
"""

import os
import sys
from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform_instance = env.PioPlatform()
board = env.BoardConfig()

def _system():
    if os.name == 'nt' or sys.platform.startswith('win'):
        return 'Windows'
    elif sys.platform == 'darwin':
        return 'Darwin'
    else:
        return 'Linux'

def _machine():
    try:
        return os.uname().machine
    except AttributeError:
        return os.environ.get('PROCESSOR_ARCHITECTURE', '')

def get_platform_subdir():
    """Get the platform-specific subdirectory name based on current platform."""
    system = _system()
    arch = _machine()
    if system == "Windows":
        return "windows-amd64"
    elif system == "Darwin":  # macOS
        if arch == "arm64":
            return "macos-arm64"
        else:
            return "macos-amd64"
    else:  # Linux
        return "linux-amd64"

def get_executable_name(name):
    """Get executable name with platform-specific extension."""
    if _system() == "Windows":
        return f"{name}.exe"
    return name

# Get P2LLVM toolchain path
toolchain_path = platform_instance.get_package_dir("toolchain-p2llvm")
platform_subdir = get_platform_subdir()

print("P2LLVM: P2LLVM framework initializing (precompiled static libraries)")

# P2LLVM executable paths
clang = os.path.join(toolchain_path, "bin", platform_subdir, get_executable_name("clang"))
clang_cpp = os.path.join(toolchain_path, "bin", platform_subdir, get_executable_name("clang++"))
linker = os.path.join(toolchain_path, "bin", platform_subdir, get_executable_name("ld.lld"))

# Library paths - check if toolchain has precompiled libraries
lib_path = os.path.join(toolchain_path, "lib", platform_subdir)
libc_lib = os.path.join(lib_path, "libc.a")
libp2_lib = os.path.join(lib_path, "libp2.a")

# Include paths - new toolchain ships headers under include/libc and include/libp2
libc_include_path = os.path.join(toolchain_path, "include", "libc")
libp2_include_path = os.path.join(toolchain_path, "include", "libp2")

if not (os.path.exists(libc_include_path) and os.path.exists(libp2_include_path)):
    print("P2LLVM: Error - Header files not found in expected locations")
    print(f"P2LLVM: Checked: {os.path.join(toolchain_path, 'include', 'libc')} and {os.path.join(toolchain_path, 'include', 'libp2')}")
    env.Exit(1)

# Use clang for compilation, but link with ld.lld directly so we can control the linker script path
env.Replace(AS=clang, CC=clang, CXX=clang_cpp, LINK=linker)

# Standard compile/link flags - rely on toolchain to add -lc/-lp2 implicitly
# Determine the toolchain linker script and ensure it exists
linker_script = os.path.join(toolchain_path, "linker", "p2.ld")
if not os.path.exists(linker_script):
    print("P2LLVM: Error - Toolchain linker script not found:", linker_script)
    env.Exit(1)

env.Append(
    CCFLAGS=[
        "--target=p2",
        "-Os",
        "-ffunction-sections",
        "-fdata-sections",
        "-fno-jump-tables",
        f"-I{libc_include_path}",
        f"-I{libp2_include_path}",
    ],
    CXXFLAGS=["-std=c++14"],
    LINKFLAGS=[
        "-T",
        linker_script,
        "--gc-sections",
    ],
    LIBPATH=[lib_path],
    LIBS=["c", "p2"],
)

print("P2LLVM: Framework initialization complete - using ld.lld with toolchain linker script and precompiled libraries")