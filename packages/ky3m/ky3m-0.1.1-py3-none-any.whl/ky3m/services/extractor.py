import zipfile
import io
import json

import toml

from ky3m.report import Report

from .mcmod import *


def extract_info(jar: bytes, _rep: Report) -> MCMod | None:
    with zipfile.ZipFile(io.BytesIO(jar)) as zf:
        name_list = zf.namelist()

        mcmod_info_path = ''.join(name if 'mcmod.info' in name else '' for name in name_list)
        if mcmod_info_path:  # MC Forge (1.13]
            loader = 'Forge'

            data = json.loads(zf.read(mcmod_info_path))
            _rep.record('extracted mcmod.info!', __name__)

            # format differences possible
            try:
                mod_id = data[0]['modid']
                mc_version = data[0]['mcversion']
                name = data[0]['name']
                version = data[0]['version']
                description = data[0]['description']
            except KeyError:  # can happen in some cases
                mod_id = data['modList'][0]['modid']
                mc_version = data['modList'][0]['mcversion']
                name = data['modList'][0]['name']
                version = data['modList'][0]['version']
                description = data['modList'][0]['description']

            # mod class initialization
            mod = MCMod(mod_id, mc_version)
            mod.name = name
            mod.version = version
            mod.description = description
            mod.loader = loader

            _rep.record(f'mod class provided! modid: {mod_id}, mcversion: {mc_version}', __name__)

            return mod

        elif 'META-INF/mods.toml' in name_list:  # MC Forge [1.14)
            loader = 'Forge'

            # replace() below was used because toml.py doesn't properly handle /r
            data = toml.loads(zf.read('META-INF/mods.toml').decode('UTF-8').replace('\r', ''))
            _rep.record('extracted mods.toml!', __name__)

            mod_id = data['mods'][0]['modId']
            name = data['mods'][0]['displayName']
            version = data['mods'][0]['version']
            description = data['mods'][0]['description']

            try:
                mc_version = list(dep['versionRange']
                                  for dep in data['dependencies'][mod_id]
                                  if dep['modId'] == 'minecraft')[0]  # str
            except KeyError:  # can happen at some cases
                mc_version = 'unknown'

            # mod class initialization
            mod = MCMod(mod_id, mc_version)
            mod.name = name
            mod.version = version
            mod.description = description
            mod.loader = loader

            _rep.record(f'mod class provided! modid: {mod_id}, mcversion: {mc_version}', __name__)

            return mod

        elif 'fabric.mod.json' in name_list:  # MC Fabric
            loader = 'Fabric'

            data = json.loads(zf.read('fabric.mod.json'))
            _rep.record('extracted fabric.mod.json!', __name__)

            mod_id = data['id']
            name = data['name']
            version = data['version']
            description = data['description']

            # mcversion stored in META-INF/MANIFEST.MF
            mc_version = list(
                line.removeprefix('Fabric-Minecraft-Version:').strip('\n').strip()
                for line in zf.read('META-INF/MANIFEST.MF').decode('UTF-8').split('\n')
                if line.startswith('Fabric-Minecraft-Version: '))[0]  # str

            # mod class initialization
            mod = MCMod(mod_id, mc_version)
            mod.name = name
            mod.version = version
            mod.description = description
            mod.loader = loader

            _rep.record(f'mod class provided! modid: {mod_id}, mcversion: {mc_version}', __name__)

            return mod

        else:
            _rep.record('data was not extracted! (no mod data found)', __name__)
            return None
