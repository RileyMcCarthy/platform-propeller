from os.path import join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

env.Append(
    BUILDERS=dict(
        FlexProp=env.Builder(
            action=env.VerboseAction(
                " ".join(
                    [
                        join(env["PROJECT_PACKAGES_DIR"], "toolchain-flexprop", "flexcc"),
                        "-2",
                        "-o",
                        "$TARGET",
                        "$SOURCES",
                    ]
                ),
                "Compiling $SOURCES",
            ),
            suffix=".elf",
            src_suffix=".c",
        ),
    )
)

if not env.get("PIOFRAMEWORK"):
    env.SConscript("frameworks/_bare.py", exports="env")

target_elf = env.FlexProp(join("$BUILD_DIR", "flexprop_output"), "src/main.c")

Default([target_elf])
