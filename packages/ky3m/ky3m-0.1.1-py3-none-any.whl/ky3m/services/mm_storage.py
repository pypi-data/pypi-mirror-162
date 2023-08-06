import os

from ky3m.report import Report
from ky3m.common.str_base import str_base
from ky3m.common.latin import latin_36_human
from ky3m.common import paths

from . import pickler as pcl


# list all .jar files in \.minecraft\mods folder
def list_jars(_rep: Report) -> dict:
    jars = {}
    for file in os.listdir(paths.mods_path):
        if file.endswith('.jar'):
            jars[str_base(id(file), latin_36_human)] = file

    if len(jars) > 1:
        # simplify INSPECT mod keys
        jars_c = jars.copy()
        while len(jars.keys()) == len(jars_c.keys()):
            jars = jars_c.copy()
            jars_c = dict(zip(list(key[1:] for key in jars_c.keys()), jars_c.values()))
    elif len(jars) == 1:
        jars = {list(jars.keys())[0][-1]: list(jars.values())[0]}

    # save keys to pcl
    pcl.remember(jars, 'listed_ids', _rep)

    _rep.record(f'jars listed: {len(jars)}', __name__)
    return jars


# get certain .jar file from \.minecraft\mods folder
def get_jar(listed_id: str, _rep: Report) -> bytes | None:
    listed_jars = pcl.recall('listed_ids', _rep)
    if listed_jars:
        if listed_id in listed_jars:
            with open(paths.mods_path + '\\' + listed_jars[listed_id], 'rb') as file:
                jar = file.read()
            _rep.record(f'requested .jar file provided! listed id: {listed_id.upper()}', __name__)
            return jar
        else:
            _rep.record(f'requested .jar file not found! listed id: {listed_id.upper()}', __name__)
            return None
    else:
        _rep.record(f'requested .jar file is in invalid format! listed id: {listed_id.upper()}', __name__)
        return None


# create .jar file with certain content in \.minecraft\mods folder
def insert_jar(jar: bytes, name: str, _rep: Report) -> bool:
    name += '.jar'
    try:
        with open(paths.mods_path + '\\' + name, 'xb') as file:
            file.write(jar)
        _rep.record(f'provided .jar inserted! name: {name}', __name__)
        return True
    except FileExistsError:
        _rep.record(f'unable to insert provided .jar! (file with same name exists) name: {name}', __name__)
        return False


# delete certain .jar file from \.minecraft\mods folder
def delete_jar(listed_id: str, _rep: Report) -> bool:
    listed_jars = pcl.recall('listed_ids', _rep)
    name = listed_jars[listed_id]
    try:
        os.remove(paths.mods_path + '\\' + name)
        _rep.record(f'requested .jar removed! listed id: {listed_id}, name: {name}', __name__)
        return True
    except FileNotFoundError:
        _rep.record(f'unable to remove requested .jar! (file not fount) '
                    f'name: listed id: {listed_id}, name: {name}', __name__)
        return False

