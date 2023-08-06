import time

from ky3m.report import Report
from ky3m.common.str_base import str_base
from ky3m.common.latin import latin_36_human

from . import pickler as pcl

rel_dir = '\\saved_jars'


# get saved ids
def get_ids(_rep: Report) -> dict:
    ids = pcl.recall('saved_ids', _rep)
    if ids:
        _rep.record(f'Got saved ids! length: {len(ids)}', __name__)
        return ids
    else:
        _rep.record('Did not get any saved ids!', __name__)
        return {}


# simplify ids (for human)
def get_ids_simplified(ids: list, _rep: Report) -> dict:
    if len(ids) > 1:
        # equate length
        max_len = max(len(i) for i in ids)
        ids = list(i.rjust(max_len, 'U') for i in ids)
        ids_o = ids.copy()
        ids = dict(zip(ids, ids))
        ids_c = ids.copy()
        while len(ids.keys()) == len(ids_c.keys()):
            ids = ids_c.copy()
            ids_c = dict(zip(list(key[1:] for key in ids_c.keys()), ids_c.values()))
        _rep.record(f'Ids list simplified! Cut: {len(ids_o[0]) - len(list(ids.keys())[0])}', __name__)
        return dict(zip((val.strip('U') for val in ids.values()), ids.keys()))
    elif len(ids) == 1:
        _rep.record(f'Id simplified to one char!', __name__)
        return {ids[0]: ids[0][-1]}
    else:
        _rep.record(f'Nothing to simplify!', __name__)
        return {}


# anti get_ids_simplified()
def get_true_id(ids: dict, sid, _rep: Report) -> str | None:
    ids = dict(zip(ids.values(), ids.keys()))
    try:
        tid = ids[sid]
        _rep.record(f'ID converted to a true id! simple ID: {sid} true id: {tid}', __name__)
    except KeyError:
        tid = None
        _rep.record(f'ID could not be converted to a true ID! simple id: {sid}', __name__)
    return tid


def check_id_free(x: str, _rep: Report) -> bool:
    return not bool(pcl.recall(x, _rep, rel_dir))


# save jar
def save(jar: bytes, name: str, _rep: Report) -> str:
    # get id
    saved_id = str_base(abs(hash(jar + bytes([time.time_ns() % 256]))), latin_36_human)
    while not check_id_free(saved_id, _rep):
        # when id is not free, can happen theoretically (super ultra mega rare)
        # chance for 32-bit system: ~1/2.1B, chance for 64-bit systems: ~1/9.2Q
        # also can happen if user saves the same file several times (1/256 chance)
        saved_id = str_base(abs(hash(jar + bytes([hash(saved_id) + time.time_ns()]))), latin_36_human)
    _rep.record(f'Unique id provided! ({saved_id.upper()})', __name__)

    # save jar
    pcl.remember(jar, saved_id, _rep, rel_dir)
    _rep.record(f'.jar saved! saved_id: {saved_id.upper()}', __name__)

    # save id
    ids = get_ids(_rep)
    ids[saved_id] = name
    pcl.remember(ids, 'saved_ids', _rep)

    saved_id = get_ids_simplified(list(ids.keys()), _rep)[saved_id]

    return saved_id


# load saved jar
def load(saved_id: str, _rep: Report) -> tuple[bytes, bool]:
    # load .jar
    jar = pcl.recall(saved_id, _rep, '\\saved_jars')

    if jar:
        _rep.record(f'.jar loaded! saved_id: {saved_id.upper()}', __name__)
        return jar, True
    else:
        _rep.record(f'unable to load .jar! saved_id: {saved_id.upper()}', __name__)


# delete saved jar
def delete(saved_id: str, _rep: Report) -> bool:
    # unsave .jar
    status = pcl.forget(saved_id, _rep, '\\saved_jars')
    _rep.record(f'.jar unsaved! saved_id: {saved_id.upper()}', __name__)

    # unsave id
    ids = get_ids(_rep)
    try:
        ids.pop(saved_id)
        pcl.remember(ids, 'saved_ids', _rep)
        _rep.record(f'id unsaved! saved_id: {saved_id.upper()}', __name__)
    except KeyError:
        _rep.record(f'id not found! saved_id: {saved_id.upper()}', __name__)
    return status
