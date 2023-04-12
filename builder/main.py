import os

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

toolchain_path = env.PioPlatform().get_package_dir("toolchain-flexprop")
flexcc = os.path.join(toolchain_path, "bin","flexcc")

env.Replace(
    AR="ar",
    AS=flexcc,
    CC=flexcc,
    CXX=flexcc,
    OBJCOPY="objcopy",
    RANLIB="ranlib",
)

def run_flexprop(target, source, env):
    cmd = [
        flexcc,
        "-2",  # Compile for Prop2
        "-o",
        str(target[0]),
        str(source[0]),
    ]
    env.Execute(cmd)

env.Append(
    BUILDERS=dict(
        ElfToBin=Builder(
            action=env.VerboseAction(f'{flexcc} -c -o $TARGET $CFLAGS $CCFLAGS $_CCCOMCOM $SOURCES', "Compiling $SOURCES"),
            suffix=".o",
            src_suffix=".c",
        ),
    )
)

if not env.get("PIOFRAMEWORK"):
    env.SConscript("frameworks/_bare.py", exports="env")

target_elf = env.BuildProgram()

Default([target_elf])
