import redis

from .dirutils import walk_fullpath
from .fileutils import file_content
from .printutils import indah4
from .utils import env_get, env_int


def connect(host=None, port=None, db=None, password=None, strict=False):
    """
    utk aplikasi terpisah, env_load() terlebih dahulu, baru panggil fungsi ini
    """
    if host is None:
        host = env_get("ULIBPY_REDIS_HOST")
    if port is None:
        port = env_int("ULIBPY_REDIS_PORT")
    if db is None:
        db = env_int("ULIBPY_REDIS_DBNO")
    # if not host:
    # 	host = 'localhost'
    # if not port:
    # 	port = 6379
    # if not db:
    # 	db = 0
    conn_params = {
        "host": host,
        "port": port,
        "db": db,
    }
    # print('[app.redisutils] redis connect:', conn_params)
    if password is not None:
        conn_params.update(
            {
                "password": password,
            }
        )

    if strict:
        r = redis.StrictRedis(**conn_params)
    else:
        r = redis.Redis(**conn_params)
    return r


def kasih(r, k, v):
    r.set(k, v)


set = kasih


def ambil(r, k):
    return r.get(k)


get = ambil


def hapus(r, keys):
    return r.delete(keys)


def masuk(r, key, values, depan=True):
    """
    https://pythontic.com/database/redis/list
    lpush masuk di head ~ insert(0, ..)
    rpush masuk di tail
    """
    if not depan:
        r.rpush(r, key, *values)
    else:
        r.lpush(r, key, *values)


def keluar(r, key, depan=True):
    if not depan:
        return r.rpop(key)
    return r.lpop(key)


def didalam(r, key):
    return r.llen(key)


def ubah(r, listkey, index, value):
    return r.lset(listkey, index, value)


def terletak(r, key, index=0):
    """
    lpush(kota, 'jakarta', 'bandung', 'surabaya')
    lindex       0          1          2
    """
    return r.lindex(index)


def ltrim(r, listkey, values):
    return r.ltrim(listkey, *values)


def rtrim(r, listkey, values):
    return r.rtrim(listkey, *values)


def ada(r, names):
    return r.exists(names)


def search_keys(r, pattern):
    return r.keys(pattern)


def search_values(r, pattern, start=0, limit=10000):
    result = []
    all = r.keys("*")
    if limit and len(all) > limit:
        all = all[start : start + limit]
    for k in all:
        v = r.get(k)
        if pattern in v:
            entry = (k, v)
            result.append(entry)

    return result


def load_file_content(r, basedir):
    allfiles = walk_fullpath(basedir, skip_ends=[".pyc"])
    for filepath in allfiles:
        kasih(r, filepath, file_content(filepath))

    indah4(f"{len(allfiles)} files loaded", warna="white")


# next = lpush/rpush/lrange, sadd/smembers, hmset/hgetall
