from app.redisutils import ada as ada_original
from app.redisutils import ambil, connect, kasih, search_keys
from app.utils import env_get

conn = None


def get_conn(db=0, host="localhost", port=None, password=None, forced=False):
    global conn
    if port is None:
        port = env_get("ULIBPY_REDIS_PORT")
    if forced or conn is None:
        conn = connect(db=db, host=host, port=port, password=password)
    return conn


def daftar(pattern="*"):
    return search_keys(get_conn(), pattern)


def daftarstr(pattern="*"):
    hasil = search_keys(get_conn(), pattern)
    hasil = [item.decode("utf8") for item in hasil]
    return hasil


def ada(key):
    # print('[redis_helper/ada]', key)
    return ada_original(get_conn(), key)


def set(key, value):
    return kasih(get_conn(), key, value)


def get(key):
    return ambil(get_conn(), key)


def getstr(key):
    return ambil(get_conn(), key).decode("utf8")


def ada_getstr(key):
    if not ada(key):
        return None
    return getstr(key)


def ada_inlist(key, keys):
    """
    cek value key ada dalam option di keys
    """
    if not ada(key):
        return False
    return getstr(key) in keys


def redis_process(command, args):
    if command == "get":
        key = args[0]
        return get(key)
    elif command == "set":
        key, value = args
        return set(key, value)
    elif command == "list":
        pattern = args[0]
        return daftar(pattern)
    elif command == "exists":
        pattern = args[0]
        return ada(pattern)
    elif command == "connect":
        dbconfig = args[0]
        dbconfig.update({"forced": True})
        get_conn(**dbconfig)
        return daftar("*")[:10]
    elif command == "reset":
        dbconfig = {"db": 0, "forced": True}
        get_conn(**dbconfig)
        return daftar("*")[:10]
