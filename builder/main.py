"""
    Build script for Parallax Propeller
"""

from os.path import join
from SCons.Script import (ARGUMENTS, COMMAND_LINE_TARGETS, AlwaysBuild,
                          Builder, Default, DefaultEnvironment)


def BeforeUpload(target, source, env):
    upload_options = {}
    if "BOARD" in env:
        upload_options = env.BoardConfig().get("upload", {})
        env.Append(UPLOADERFLAGS=["-b", env.subst("$BOARD")])

    # Extra upload flags
    if "extra_flags" in upload_options:
        env.AppendUnique(UPLOADERFLAGS=upload_options.get("extra_flags"))

    env.AutodetectUploadPort()
    env.Append(UPLOADERFLAGS=["-p", '"$UPLOAD_PORT"'])

    if int(ARGUMENTS.get("PIOVERBOSE", 0)):
        env.Prepend(UPLOADERFLAGS=["-v"])

    # Enable debug mode at upload
    if env.GetBuildType() == "debug":
        env.Prepend(UPLOADERFLAGS=["-g"])


env = DefaultEnvironment()
platform = env.PioPlatform()
#board = env.BoardConfig()

env.Replace(
    AR="llvm-ar",
    AS="clang++",
    CC="clang",
    CXX="clang++",
    OBJCOPY="ç",
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
    #ARFLAGS=["..."],

    #ASFLAGS=["flag1", "flag2", "flagN"],
    CCFLAGS=["-fno-jump-tables", "--target=p2", "-Os"],
    CXXFLAGS=["-fno-jump-tables", "--target=p2", "-Os"],
    LINKFLAGS=["--target=p2"],

    #CPPDEFINES=["DEFINE_1", "DEFINE=2", "DEFINE_N"],

    #LIBS=["additional", "libs", "here"],
)


# Allow user to override via pre:script
if env.get("PROGNAME", "program") == "program":
    env.Replace(PROGNAME="firmware")

#
# Target: Build executable and linkable firmware
#
target_elf = None
if "nobuild" in COMMAND_LINE_TARGETS:
    target_elf = join("$BUILD_DIR", "${PROGNAME}.elf")
    target_firm = target_elf
else:
    target_elf = env.BuildProgram()
    target_firm = target_elf

AlwaysBuild(env.Alias("nobuild", target_firm))
target_buildprog = env.Alias("buildprog", target_firm, target_firm)

#
# Target: Print binary size
#
target_size = env.Alias(
    "size", target_elf,
    env.VerboseAction("$SIZEPRINTCMD", "Calculating size $SOURCE"))
AlwaysBuild(target_size)

#
# Target: Upload firmware to RAM
#
env.Replace(
	UPLOADER=join("$PIOPACKAGES_DIR", "toolchain-parallax", "bin", "loadp2"),
	UPLOADERFLAGS=[
		"-ZERO"
        ],
	UPLOADCMD="$UPLOADER $UPLOADERFLAGS $SOURCE"
    )
upload_source = target_firm
upload_actions = [
	env.VerboseAction(BeforeUpload, "Looking for upload port..."),
	env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE to RAM")
	]
target_upload = env.Alias("upload", upload_source, upload_actions)
AlwaysBuild(target_upload)

#
# Target: Upload firmware to EEPROM
#
env.Replace(
    EUPLOADER = "$UPLOADER",
	EUPLOADERFLAGS=[
		"$UPLOADERFLAGS", "-e"
        ],
	EUPLOADCMD="$EUPLOADER $EUPLOADERFLAGS $SOURCE"
    )
program_actions = [
	env.VerboseAction(BeforeUpload, "Looking for upload port..."),
	env.VerboseAction("$EUPLOADCMD", "Programming $SOURCE to EEPROM")
	]
target_program = env.Alias("program", target_firm, program_actions)
AlwaysBuild(target_program)

#
# Setup default targets
#
Default([target_buildprog, target_size])