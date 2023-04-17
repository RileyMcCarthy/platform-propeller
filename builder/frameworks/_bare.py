from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

env.Append(
    CPPDEFINES=[
        # Define any needed global compiler definitions here
    ],

    CPPPATH=[
        # Add any necessary include paths for header files here
    ],

    LIBPATH=[
        # Add any necessary library paths for linker here
    ],

    LIBS=[
        # Add any necessary libraries for linker here
    ],
)
