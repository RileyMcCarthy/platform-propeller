import os

from SCons.Script import DefaultEnvironment
import platform


env = DefaultEnvironment()

system = platform.system()
arch = platform.machine()

if system == "Windows":
    flexcc_executable = "flexcc.exe"
    loadp2_executable = "loadp2.exe"
elif system == "Darwin":
    flexcc_executable = "flexcc.mac"
    loadp2_executable = "loadp2.mac"
elif arch == "armv7l":
    flexcc_executable = "flexcc.rpi"
    loadp2_executable = "loadp2.rpi"
else:
    flexcc_executable = "flexcc"
    loadp2_executable = "loadp2"

toolchain_path = env.PioPlatform().get_package_dir("toolchain-flexprop")
flexcc = os.path.join(toolchain_path, "bin", flexcc_executable)
flexprop_include_path = os.path.join(toolchain_path, "include")

env.Replace(

    AS=flexcc, # assembler
    CC=flexcc, # C compiler
    CXX=flexcc, # C++ compiler

    UPLOADER=os.path.join(env.PioPlatform().get_package_dir("tool-loadp2"),"bin", loadp2_executable),
    UPLOADCMD="$UPLOADER -b230400 -t $SOURCES"
)

# Add build flags
env.Append(
    CCFLAGS=["-2", "-Wall", "-O1"],
    LINKFLAGS=["-2", "-Wall", "-O1"],
    CPPPATH=[flexprop_include_path],
)

if not env.get("PIOFRAMEWORK"):
    env.SConscript("frameworks/_bare.py", exports="env")

target_elf = env.BuildProgram()

#
# Target: Upload firmware
#
upload = env.Alias(["upload"], target_elf, "$UPLOADCMD")
AlwaysBuild(upload)

Default([target_elf])
