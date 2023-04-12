import os

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

toolchain_path = env.PioPlatform().get_package_dir("toolchain-flexprop")
flexcc = os.path.join(toolchain_path, "bin","flexcc")

env.Replace(
    AS=flexcc,
    CC=flexcc,
    CXX=flexcc,
)

if not env.get("PIOFRAMEWORK"):
    env.SConscript("frameworks/_bare.py", exports="env")

target_elf = env.BuildProgram()

Default([target_elf])
