import os
import platform
import pathlib

# platform compliance setting
match platform.system():
    case 'Windows':
        appdata_loc = os.getenv('LOCALAPPDATA')
        appdata_rom = os.getenv('APPDATA')
        local_path = appdata_loc + '\\_Ky\\3M'
        minecraft_path = appdata_rom + '\\.minecraft'
    case 'Linux':
        home = os.path.expanduser("~")
        local_path = home + '\\.ky3m'
        minecraft_path = home + '\\.minecraft'
    case _:
        raise OSError(f'Incompatible platform: {platform.system()}')  # TODO (paths) Improve cross-platform

# creating dirs
pathlib.Path(local_path).mkdir(parents=True, exist_ok=True)
pathlib.Path(minecraft_path).mkdir(parents=True, exist_ok=True)

mods_path = minecraft_path + '\\mods'
