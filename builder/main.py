"""
    Build script for Parallax Propeller
"""
from os.path import join
from SCons.Script import AlwaysBuild, Builder, Default, DefaultEnvironment

env = DefaultEnvironment()

env.Replace(
    AR="llvm-ar",
    AS="clang++",
    CC="clang",
    CXX="clang++",
    OBJCOPY="llvm-objcopy",
    RANLIB="llvm-ranlib",
    SIZETOOL="llvm-size",

    ARFLAGS=["rc"],

    SIZEPROGREGEXP=r"^(?:\.text|\.data)\s+(\d+).*",
    SIZEDATAREGEXP=r"^(?:\.data|\.bss)\s+(\d+).*",
    SIZECHECKCMD="$SIZETOOL -A -d $SOURCES",
    SIZEPRINTCMD='$SIZETOOL -B -d $SOURCES',

    PROGSUFFIX=".elf"
)

env.Append(
    CCFLAGS=["-fno-jump-tables", "--target=p2", "-Os"],
    CXXFLAGS=["-fno-jump-tables", "--target=p2", "-Os"],
    LINKFLAGS=["--target=p2"],

    #LIBS=["additional", "libs", "here"],

    BUILDERS=dict(
        ElfToBin=Builder(
            action=" ".join([
                "$OBJCOPY",
                "-O",
                "binary",
                "$SOURCES",
                "$TARGET"]),
            suffix=".bin"
        )
    )
)

# The source code of "platformio-build-tool" is here
# https://github.com/platformio/platformio-core/blob/develop/platformio/builder/tools/platformio.py

#
# Target: Build executable and linkable firmware
#
target_elf = env.BuildProgram()

#
# Target: Build the .bin file
#
target_bin = env.ElfToBin(join("$BUILD_DIR", "firmware"), target_elf)

#
# Target: Upload firmware
#
upload = env.Alias(["upload"], target_bin, "$UPLOADCMD")
AlwaysBuild(upload)

#
# Target: Define targets
#
Default(target_bin)
