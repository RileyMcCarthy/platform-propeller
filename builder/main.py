import os

from SCons.Script import DefaultEnvironment
import platform

import platform
from subprocess import run

env = DefaultEnvironment()

system = platform.system()
arch = platform.machine()

if system == "Windows":
    flexcc_executable = "flexcc.exe"
    loadp2_executable = "loadp2.exe"
    loadp2_executable = "loadp2.exe"
elif system == "Darwin":
    flexcc_executable = "flexcc.mac"
    loadp2_executable = "loadp2.mac"
elif arch == "armv7l":
    flexcc_executable = "flexcc.rpi"
    loadp2_executable = "loadp2.rpi"
    loadp2_executable = "loadp2.mac"
elif arch == "armv7l":
    flexcc_executable = "flexcc.rpi"
    loadp2_executable = "loadp2.rpi"
else:
    flexcc_executable = "flexcc"
    loadp2_executable = "loadp2"
    loadp2_executable = "loadp2"

toolchain_path = env.PioPlatform().get_package_dir("toolchain-flexprop")
flexcc = os.path.join(toolchain_path, "bin", flexcc_executable)
flexprop_include_path = os.path.join(toolchain_path, "include")
flexcc = os.path.join(toolchain_path, "bin", flexcc_executable)
flexprop_include_path = os.path.join(toolchain_path, "include")

env.Replace(

    AS=flexcc, # assembler
    CC=flexcc, # C compiler
    CXX=flexcc, # C++ compiler

    UPLOADER=os.path.join(env.PioPlatform().get_package_dir("tool-loadp2"),"bin", loadp2_executable),
    SDCARD=os.path.join(env.PioPlatform().get_package_dir("tool-loadp2"),"bin", "loadp2-Linux", "P2ES_sdcard.bin"),
    FLASH=os.path.join(env.PioPlatform().get_package_dir("tool-loadp2"),"bin", "loadp2-Linux", "P2ES_flashloader.bin"),
    UPLOADERFLAGS=["-b230400"],
    UPLOADCMD="$UPLOADER $UPLOADERFLAGS $SOURCES",
)

# Add build flags
env.Append(
    CCFLAGS=["-2", "-Wall", "-O1", "-D__WORKSPACE__='\"$PROJECT_DIR\"'"],
    LINKFLAGS=["-2", "-Wall", "-O1"],
    CPPPATH=[flexprop_include_path],
)

upload_actions = [env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")]

upload_protocol = env.subst("$UPLOAD_PROTOCOL")
if upload_protocol.startswith("flash"):
    env.Replace(
        UPLOADERFLAGS=[
            "-t",
            "-v",
            "-b230400",
            "\"@0=$FLASH,@8000+$SOURCES\"",
        ],
        UPLOADCMD="$UPLOADER $UPLOADERFLAGS",
    )
    upload_actions = ["$UPLOADCMD"]
elif upload_protocol.startswith("sdcard"):
    env.Replace(
        UPLOADERFLAGS=[
            "-t",
            "-v",
            "-b230400",
            "\"@0=$SDCARD,@8000+$SOURCES\"",
        ],
        UPLOADCMD="$UPLOADER $UPLOADERFLAGS",
    )
elif upload_protocol.startswith("serial"):
    env.Replace(
        UPLOADERFLAGS=["-t","-v","-b230400"],
        UPLOADCMD="$UPLOADER $UPLOADERFLAGS $SOURCES",
    )
    upload_actions = ["$UPLOADCMD"]


if not env.get("PIOFRAMEWORK"):
    env.SConscript("frameworks/_bare.py", exports="env")
target_elf = env.BuildProgram()

#
# Target: Upload firmware
#
upload = env.Alias(["upload"], target_elf, "$UPLOADCMD")
AlwaysBuild(upload)

Default([target_elf])
