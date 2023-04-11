from platformio.builder.tools import platformio as 
platformio_builder_tools

Import("env")

def run_flexprop(target, source, env):
    cmd = ["path/to/flexprop", "-o", str(target[0]), str(source[0])]
    env.Execute(cmd)

env.AddPostAction("$BUILD_DIR/${PROGNAME}.elf", run_flexprop)
env.Replace(PROGNAME="flexprop_output")

