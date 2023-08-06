import os
import bz2
import base64
import pathlib
import pickle as pcl
from typing import Any

from ky3m.report import Report
from ky3m.common import paths

pcl_path = paths.local_path + '\\pz'
pathlib.Path(pcl_path).mkdir(parents=True, exist_ok=True)


# "save"
def remember(obj: object, save_id: str, _rep: Report, rel_dir='') -> int:
    path = pcl_path + rel_dir + '\\'
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    path += save_id + '.pz'

    # compressing and encrypting
    data = bz2.compress(base64.a85encode(pcl.dumps(obj)))
    with open(path, 'wb') as save:
        save.write(
            b'PZ3M:>' + bytes(list(b ^ 7 for b in data))

        )
    with open(path, 'rb') as save:
        size = len(save.read())

    raw_size = len(pcl.dumps(obj))

    _rep.record(
        f'data remembered!\n'
        f'id: {save_id}, rel dir: {rel_dir}, obj type: {type(obj)}\n'
        f'raw size: {raw_size}, saved size: {size}, efficiency: {round((raw_size - size) / raw_size * 100, 1)}%',
        __name__
    )

    return size


# "load"
def recall(save_id: str, _rep: Report, rel_dir='\\') -> Any | None:
    path = pcl_path + rel_dir + '\\'
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    path += save_id + '.pz'

    # decompressing and decrypting
    try:
        with open(path, 'rb') as save:

            data = bytes(list(b ^ 7 for b in save.read()[6:]))

        try:
            obj = pcl.loads(base64.a85decode(bz2.decompress(data)))
            _rep.record(f'data recalled! id: {save_id}, rel dir: {rel_dir}, obj type: {type(obj)}', __name__)
            return obj

        except (OSError, ValueError):
            _rep.record(f'data was not recalled (invalid file format)! id: {save_id}, rel dir: {rel_dir}', __name__)
            return None

    except FileNotFoundError:
        _rep.record(f'data was not recalled (no such data stored)! id: {save_id}, rel dir: {rel_dir}', __name__)
        return None


def forget(save_id: str, _rep, rel_dir='\\') -> bool:
    path = pcl_path + rel_dir + '\\' + save_id + '.pz'
    try:
        os.remove(path)
        _rep.record(f'data forgot! id: {save_id}, rel dir: {rel_dir}', __name__)
        return True
    except FileNotFoundError:
        _rep.record(f'data was not forgot (no such data stored)! id: {save_id}, rel dir: {rel_dir}', __name__)
        return False
