"""
Main PlatformIO builder for Propeller platforms.
"""

import os
from SCons.Script import DefaultEnvironment, AlwaysBuild, Default

env = DefaultEnvironment()

# Framework loading is handled automatically by PlatformIO
# Only load bare framework if no framework is specified
if not env.get("PIOFRAMEWORK"):
    env.SConscript("frameworks/_bare.py", exports="env")

# Handle any special framework pre-processing here if needed
frameworks = env.get("PIOFRAMEWORK", [])
# Example: if "somespecialframework" in frameworks:
#     # Special pre-processing

#
# Target: Build executable and linkable firmware
#
target_elf = env.BuildProgram()

#
# Target: Upload firmware
#
upload = env.Alias(["upload"], target_elf, "$UPLOADCMD")
AlwaysBuild(upload)

Default([target_elf])

#
# Target: Upload firmware
#
upload = env.Alias(["upload"], target_elf, "$UPLOADCMD")
AlwaysBuild(upload)

Default([target_elf])
