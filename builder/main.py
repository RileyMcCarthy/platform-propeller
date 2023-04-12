from os.path import join
from SCons.Script import AlwaysBuild, Builder, Default, DefaultEnvironment

env = DefaultEnvironment()

def run_flexprop(target, source, env):
    import os
    toolchain_path = env.PioPlatform().get_package_dir("toolchain-flexprop")
    cmd = [os.path.join(toolchain_path, "bin", "flexprop"), "-o", str(target[0]), str(source[0])]
    env.Execute(cmd)

env.Replace(
    PROGNAME="flexprop_output",
    PROGSUFFIX=".elf",
    SIZEPROG="size",
)

env.AddPostAction("$BUILD_DIR/${PROGNAME}.elf", run_flexprop)
