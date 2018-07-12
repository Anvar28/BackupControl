from cx_Freeze import setup, Executable

base = None

executables = [Executable("backupcontrol.py", base=base)]

setup(
    name = "BackUpControl",
    version = "1",
    description = 'Control create backupfiles',
    executables = executables
)