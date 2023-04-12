from os.path import join
from SCons.Script import AlwaysBuild, Builder, Default, DefaultEnvironment

env = DefaultEnvironment()

env.Replace(
    AR="ar",
    CC="gcc",
    CXX="g++",
    LINK="gcc",
    AS="as",
)

env.Append(
    CCFLAGS=["-Wall"],
    LINKFLAGS=["-Wl,-Map=${TARGET}.map"],
)

def run_flexprop(target, source, env):
    import os
    toolchain_path = env.PioPlatform().get_package_dir("toolchain-flexprop")
    cmd = [
        os.path.join(toolchain_path, "flexcc"),
        "-2",  # Compile for Prop2
        "-O2", # Optimization level
        str(target[0]),
        str(source[0]),
    ]
    env.Execute(cmd)


env.Replace(
    PROGNAME="flexprop_output",
    PROGSUFFIX=".elf",
    SIZEPROG="size",
)

env['BUILDERS']['Program'] = Builder(
    action=env.VerboseAction(run_flexprop, "Building $TARGET"),
    suffix=".elf",
)

# Add source files to the build environment
env.Append(
    CPPPATH=[join("$PROJECT_SRC_DIR")],
    SRC_FILTER=[
        "+<*>",
    ],
)

Default([env.Program(join("$BUILD_DIR", "${PROGNAME}"), join("$PROJECT_SRC_DIR", "main.c"))])
