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

# Define all framework identification constants (always available)
flexcc_value = 1
p2llvm_value = 2
selected_framework = 0
if "flexcc" in frameworks:
    selected_framework = flexcc_value
    print("Selected framework: FlexCC")
elif "p2llvm" in frameworks:
    selected_framework = p2llvm_value
    print("Selected framework: P2LLVM")
else:
    print("No specific framework selected; using bare framework.")

env.Append(
    CPPDEFINES=[
        ("FLEXCC", flexcc_value),
        ("P2LLVM", p2llvm_value),
        ("PROPELLER_FRAMEWORK", selected_framework),
    ]
)

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
