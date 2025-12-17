"""
P2LLVM Framework for Propeller platforms.
Uses the LLVM-based P2LLVM compiler toolchain with precompiled static libraries.
"""

import os
import sys
from SCons.Script import DefaultEnvironment
from frameworks._loadp2 import setup_loadp2

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

def ensure_executable_permissions(executable_path):
    """Ensure the executable has execute permissions."""
    if os.path.exists(executable_path) and not os.access(executable_path, os.X_OK):
        try:
            import stat
            current_permissions = os.stat(executable_path).st_mode
            os.chmod(executable_path, current_permissions | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
            print(f"P2LLVM: Added execute permissions to {executable_path}")
        except Exception as e:
            print(f"P2LLVM: Warning - Could not add execute permissions to {executable_path}: {e}")

# Get P2LLVM toolchain path
toolchain_path = platform_instance.get_package_dir("toolchain-p2llvm")
platform_subdir = get_platform_subdir()

print("P2LLVM: P2LLVM framework initializing (precompiled static libraries)")

# P2LLVM executable paths
clang = os.path.join(toolchain_path, "bin", platform_subdir, get_executable_name("clang"))
clang_cpp = os.path.join(toolchain_path, "bin", platform_subdir, get_executable_name("clang++"))
linker = os.path.join(toolchain_path, "bin", platform_subdir, get_executable_name("ld.lld"))

# Ensure executables have proper permissions
ensure_executable_permissions(clang)
ensure_executable_permissions(clang_cpp)
ensure_executable_permissions(linker)

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
env.Replace(AS=clang, CC=clang, CXX=clang_cpp, LINK=clang)
linker_script_dir = os.path.join(toolchain_path, "linker")
map_file = os.path.join("$BUILD_DIR", "${PROGNAME}.map")

# Standard compile/link flags
env.Append(
    CCFLAGS=[
        "--target=p2",
        "-Os",
        f"-I{libc_include_path}",
        f"-I{libp2_include_path}",
    ],
    CXXFLAGS=["-std=c++14"],
    LINKFLAGS=[
        "--target=p2",
        "-Wl,-gc-sections",
        "-v",
        f"-Wl,-Map,{map_file}"
    ],
    LIBPATH=[lib_path, linker_script_dir],
)

print("P2LLVM: Framework initialization complete - using ld.lld with toolchain linker script and precompiled libraries")
print("P2LLVM: Assembly artifacts (.s files) will be saved in build directory for diagnostics")

# -----------------------------------------------------------------------------
# Add program size reporting using llvm-size
# -----------------------------------------------------------------------------
llvm_size = os.path.join(toolchain_path, "bin", platform_subdir, get_executable_name("llvm-size"))
llvm_objdump = os.path.join(toolchain_path, "bin", platform_subdir, get_executable_name("llvm-objdump"))

ensure_executable_permissions(llvm_size)
ensure_executable_permissions(llvm_objdump)

env.Replace(
    SIZETOOL=llvm_size,
    SIZEPRINTCMD='$SIZETOOL -A -d $SOURCES',
    SIZECHECKCMD='$SIZETOOL -A -d $SOURCES',
    # Flash usage: .text (code) + .rodata (constants) + .data (initialized data)
    SIZEPROGREGEXP=r"^(?:\.text|\.rodata|\.data)\s+(\d+).*",
    # RAM usage: .data (initialized in RAM) + .bss (uninitialized) + .heap + .stack
    SIZEDATAREGEXP=r"^(?:\.data|\.bss|\.heap|\.stack)\s+(\d+).*",
)

# Add custom action to show program information after linking
def print_program_info(source, target, env):
    """Display detailed program information after successful build."""
    import subprocess
    program_path = str(target[0])  # Use target instead of source
    
    print("=" * 80)
    print("P2LLVM: Program Build Information")
    print("=" * 80)
    
    # Show sections with llvm-objdump (includes size, VMA, and type information)
    try:
        result = subprocess.run(
            [llvm_objdump, "-h", program_path],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"P2LLVM: Warning - Could not get section information: {e}")
    except FileNotFoundError:
        print(f"P2LLVM: Warning - llvm-objdump not found at {llvm_objdump}")
    
    print("=" * 80)

# Add the info display as a post-action to the program build
env.AddPostAction("$BUILD_DIR/${PROGNAME}$PROGSUFFIX", print_program_info)

# -----------------------------------------------------------------------------
# Configure LoadP2 uploader (using shared _loadp2.py module)
# -----------------------------------------------------------------------------
setup_loadp2(env, platform_instance)
