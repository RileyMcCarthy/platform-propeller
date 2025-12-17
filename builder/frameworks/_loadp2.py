"""
Shared LoadP2 uploader configuration for Propeller platforms.
Used by both flexcc and p2llvm frameworks.
"""

import os
import sys

def _system():
    if os.name == 'nt' or sys.platform.startswith('win'):
        return 'Windows'
    elif sys.platform == 'darwin':
        return 'Darwin'
    else:
        return 'Linux'

def _get_loadp2_platform_subdir():
    """Get the platform-specific subdirectory name for LoadP2 tools."""
    system = _system()
    
    if system == "Windows":
        return "windows"
    elif system == "Darwin":  # macOS
        return "macos"
    else:  # Linux
        return "linux"

def _get_executable_name(base_name):
    """Get the executable name based on the current platform."""
    system = _system()
    
    if system == "Windows":
        return f"{base_name}.exe"
    else:
        return base_name

def _ensure_executable_permissions(executable_path):
    """Ensure the executable has execute permissions."""
    if os.path.exists(executable_path) and not os.access(executable_path, os.X_OK):
        try:
            import stat
            current_permissions = os.stat(executable_path).st_mode
            os.chmod(executable_path, current_permissions | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
            print(f"LoadP2: Added execute permissions to {executable_path}")
        except Exception as e:
            print(f"LoadP2: Warning - Could not add execute permissions to {executable_path}: {e}")

def setup_loadp2(env, platform_instance):
    """
    Configure LoadP2 uploader for the environment.
    
    Implements loadp2 command line interface:
    - Flash: @0=flashloader,@8000+program (multi-file loading)
    - SD Card: @0=sdloader,@8000+program
    - Serial/RAM: program (direct load)
    
    Args:
        env: SCons environment
        platform_instance: PlatformIO platform instance
    """
    
    # Get tool-loadp2 package
    loadp2_platform_subdir = _get_loadp2_platform_subdir()
    loadp2_executable = _get_executable_name("loadp2")
    uploader_path = platform_instance.get_package_dir("tool-loadp2")
    
    if not uploader_path or not os.path.isdir(uploader_path):
        print(f"LoadP2: Warning - tool-loadp2 package not found. Upload functionality will be unavailable.")
        return
    
    # Configure uploader paths
    uploader = os.path.join(uploader_path, "bin", loadp2_platform_subdir, loadp2_executable)
    sdcard = os.path.join(uploader_path, "bin", "P2ES_sdcard.bin")
    flash = os.path.join(uploader_path, "bin", "P2ES_flashloader.bin")
    
    # Ensure LoadP2 executable has execute permissions
    _ensure_executable_permissions(uploader)
    
    # Get user configuration
    upload_protocol = env.subst("$UPLOAD_PROTOCOL")
    upload_speed = env.subst("$UPLOAD_SPEED") or "2000000"
    monitor_speed = env.GetProjectOption("monitor_speed", "115200")
    upload_port = env.subst("$UPLOAD_PORT")
    
    # Set up base environment variables
    env.Replace(
        UPLOADER=uploader,
        SDCARD=sdcard,
        FLASH=flash,
    )
    
    # Build base flags: -CHIP is default, -v for verbose
    base_flags = ["-CHIP", "-v","", "-l", upload_speed, "-b", monitor_speed]
    
    # Add port if specified (otherwise let loadp2 auto-detect)
    if upload_port and upload_port != "$UPLOAD_PORT":
        base_flags.extend(["-p", upload_port])
    
    # Configure protocol-specific upload
    if upload_protocol.startswith("flash"):
        env.Replace(
            #UPLOADERFLAGS=base_flags + ['"@0=$FLASH,@8000+$SOURCE"'],
            UPLOADERFLAGS=base_flags + ["-FLASH", '"$SOURCE"'],
            UPLOADCMD='"$UPLOADER" $UPLOADERFLAGS',
        )
    elif upload_protocol.startswith("sdcard"):
        # SD Card: @0=sdloader.bin,@8000+program
        env.Replace(
            UPLOADERFLAGS=base_flags + ['"@0=$SDCARD,@8000+$SOURCE"'],
            UPLOADCMD='"$UPLOADER" $UPLOADERFLAGS',
        )
    else:
        # Serial/RAM: direct load to RAM
        env.Replace(
            UPLOADERFLAGS=base_flags + ["-t", '"$SOURCE"'],
            UPLOADCMD='"$UPLOADER" $UPLOADERFLAGS',
        )
