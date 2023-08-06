import datetime
import errno
import functools
import os
import pathlib
import re
import tempfile
from stat import S_ISREG, ST_CTIME, ST_MODE, ST_MTIME

# import pyperclip

try:
    HOMEDIR = os.environ["HOME"]
except:
    HOMEDIR = os.environ["USERPROFILE"]


def chdir(folderpath):
    if isdir(folderpath):
        os.chdir(folderpath)


def absize(innerfunc):
    @functools.wraps(innerfunc)
    def wrapper(filepath):
        return os.path.abspath(innerfunc(filepath))

    return wrapper


def dirize(innerfunc):
    @functools.wraps(innerfunc)
    def wrapper(filepath):
        return os.path.dirname(innerfunc(filepath))

    return wrapper


def normalize(innerfunc):
    @functools.wraps(innerfunc)
    def wrapper(*args):
        return os.path.normpath(innerfunc(*args))

    return wrapper


def normy(path):
    return os.path.normpath(path)


def normy_pathlist(pathlist):
    return [normy(path) for path in pathlist]


def subtract_normy_pathlist(pathlist, subtractor):
    return [item.removeprefix(subtractor) for item in normy_pathlist(pathlist)]


def normalizepath(path):
    return os.path.normpath(path)


def absolutenormalizepath(path):
    return os.path.abspath(os.path.normpath(path))


def absnormpath(path):
    return absolutenormalizepath(path)


def ANpath(path):
    return absolutenormalizepath(path)


def printer(valuefunc):
    @functools.wraps(valuefunc)
    def wrapper(*args, **kwargs):
        nilai = valuefunc(*args, **kwargs)
        print(nilai)

    return wrapper


def parentize(innerfunc):
    @functools.wraps(innerfunc)
    def wrapper(filepath, times):
        nilai = filepath
        while times > 0:
            nilai = os.path.join(nilai, os.path.pardir)
            times -= 1
        return nilai

    return wrapper


@normalize
def abs_pardir(filepath):
    """seringnya
    parent/
            ourselves/
                    filepath
    kita pengen parent biasanya, krn ourselves itu module
    utk dapatkan ourselves, gunakan here(__file__)
    """
    return os.path.join(abs_dir(filepath), os.path.pardir)


# pemahamanku:
# absolute kan, lalu ambil dir, later, norm kan
@normalize
@dirize
@absize
def here(filepath):
    """
    kembalikan dirname utk filepath yg diberikan.
    cocok utk terma __file__
    """
    return filepath


# @printer
@normalize
@parentize
def ayah(filepath, times=1):
    return filepath


def basename(filepath):
    return os.path.basename(filepath)


def ayah_basename(filepath, times=1):
    return basename(ayah(filepath, times))


def ayahbasename(filepath, times=1):
    return ayah_basename(filepath, times)


def nonbasename(filepath):
    """
    bukan basename = setara dg dirname
    """
    return os.path.dirname(filepath)


def dirname(filepath):
    return os.path.dirname(filepath)


def get_cwd():
    return os.getcwd()


def getcwd():
    return get_cwd()


def is_file_not_dir(filepath):
    return os.path.basename(filepath) == filepath


def is_dir_not_file(filepath):
    return not is_file_not_dir(filepath)


def abs_dir(filepath):
    """
    biar aman, abs dulu baru dir.
    kita sebut: DA.
    jk dia dir maka kembalikan abs-nya
    jk dia file maka kembalikan abs dir-nya
    """
    if os.path.isdir(filepath):
        return os.path.normpath(os.path.abspath(filepath))

    return os.path.normpath(os.path.dirname(os.path.abspath(filepath)))


def joiner(*args):
    # UPDATE: tambah normy
    return normy(os.path.join(*args))


def joinhere(filehere, *args):
    """
    joinhere(__file__, 'relative/to/path')
    """
    return joiner(ayah(filehere, 1), *args)


def dirs(
    dirpath,
    find_files=False,
    excludes=["__pycache__", ".git", "node_modules"],
    skip_hidden=False,
):
    curdir = dirpath

    if os.path.isfile(dirpath):
        curdir = here(dirpath)

    if not os.path.isdir(curdir):
        print("[dirs] Error not directory:", curdir)

    # print('dirutils/dirs/curdir=', curdir, 'files/dirs:', 'files' if find_files else 'dirs')
    all_files = os.listdir(curdir)
    if skip_hidden:
        all_files = [item for item in all_files if not item.startswith(".")]

    if find_files:
        return [item for item in all_files if os.path.isfile(joiner(curdir, item))]

    return [
        item
        for item in all_files
        if os.path.isdir(joiner(curdir, item)) and item not in excludes
    ]
    # print('dirs:', hasil, 'listdir:', [basename(item) for item in os.listdir(curdir)], [item in excludes for item in os.listdir(curdir)], 'excludes:', excludes)
    # return hasil


def only_files(dirpath, sort=True):
    if sort:
        return sorted(
            [
                item
                for item in os.listdir(dirpath)
                if os.path.isfile(joiner(dirpath, item))
            ]
        )
    else:
        return [
            item
            for item in os.listdir(dirpath)
            if os.path.isfile(joiner(dirpath, item))
        ]


def only_files_without_ext(dirpath, nosort=True):
    """
    sudah ada: files_noext
    """
    pass


def files(dirpath):
    return dirs(dirpath, True)


def files_filter(dirpath, extension=[], only_filename=False, sort=False):
    """
    only_filename utk strip dir paths dari filepath
    """
    allfiles = dirs(dirpath, find_files=True)
    if extension:
        allfiles = [
            item
            for item in allfiles
            if any([ext for ext in extension if item.endswith(ext)])
        ]
    if only_filename:
        allfiles = [basename(item) for item in allfiles]
    if sort:
        return sorted(allfiles)
    return allfiles


def dirs_files(dirpath):
    # all dirs + all files
    return dirs(dirpath) + files(dirpath)


def sdirs(dirpath, find_files=False):
    return sorted(dirs(dirpath, find_files))


def sfiles(dirpath):
    return sorted(files(dirpath))


def files_noext(dirpath, sorted=True):
    res = [pathlib.Path(item).stem for item in files(dirpath)]
    if sorted:
        return sorted(res)
    return res


def files_noext_filter_by_ext(dirpath, ext=".mk", sorted=True):
    """
    hanya file2 ber-ext mk
    """
    res = [pathlib.Path(item).stem for item in files(dirpath) if item.endswith(ext)]
    if sorted:
        return sorted(res)
    return res


def files_with_pattern(dirpath, pattern, sorted_=True):
    """
    spt files_noext_filter_by_ext, tapi gak hanya ending, bisa awalan dan tengahan
    """
    res = [item for item in sfiles(dirpath) if pattern.lower() in item.lower()]
    if sorted_:
        return sorted(res)
    return res


def isdir(filepath, do_bongkar=True, strip=False):
    if strip:
        filepath = filepath.strip()
    if do_bongkar:
        # return os.path.isdir(bongkar(filepath))
        pecah = bongkar(filepath)
        false_or_path = os.path.isdir(pecah)
        if false_or_path:
            # kembalikan full path hasil bongkar
            return pecah
        return false_or_path
    return os.path.isdir(filepath)


def isdir_simple(filepath):
    return os.path.isdir(filepath)


def isfile(filepath, do_bongkar=True, strip=False):
    if strip:
        filepath = filepath.strip()
    if do_bongkar:
        # return os.path.isfile(bongkar(filepath))
        pecah = bongkar(filepath)
        bool_or_path = os.path.isfile(pecah)
        if bool_or_path:
            # kembalikan full path hasil bongkar
            return pecah
        return bool_or_path
    return os.path.isfile(filepath)


def bongkar_if_not_dir(filepath, strip=False):
    if strip:
        filepath = filepath.strip()
    if os.path.isdir(filepath):
        return filepath
    return bongkar(filepath)


def bongkar_if_not_file(filepath, strip=False):
    """
    bongkar path:
    ULIBPY_*
    ~
    env vars
    """
    if strip:
        filepath = filepath.strip()
    if os.path.isfile(filepath):
        return filepath
    return bongkar(filepath)


def isfolder_dir(filepath):
    """
    dari filepath, cek apa foldernya dir?
    """
    return isdir(ayah(filepath, 1))


def listdir(dirpath):
    return os.listdir(dirpath)


def listdir_onlydirs(dirpath):
    return list(filter(os.path.isdir, os.listdir(dirpath)))


def listdir_onlyfiles(dirpath):
    return list(filter(lambda x: not os.path.isdir(x), os.listdir(dirpath)))


def does_not_exist(filepath):
    return not os.path.exists(filepath)


def does_exist(filepath):
    return os.path.exists(filepath)


def exists_in_dir(basedir, filename):
    # filepath = joiner(basedir, filename)
    # return os.path.exists(filepath)
    return filename in os.listdir(basedir)


def not_exists_in_dir(basedir, filename):
    # filepath = joiner(basedir, filename)
    # return not os.path.exists(filepath)
    return not filename in os.listdir(basedir)


def exists_in_dir_bypattern(basedir, filepattern, complete_path=True):
    daftar = only_files(basedir)
    daftar = [item for item in daftar if filepattern in item]
    if complete_path:
        daftar = [joiner(basedir, item) for item in daftar if filepattern in item]

    if not daftar:
        return None

    if len(daftar) == 1:
        return daftar[0]
    else:
        return daftar


def getcwd():
    return os.getcwd()


def disini():
    return os.getcwd()


def pemisah():
    return os.sep


def pemisah_direktori():
    return os.sep


def pemisah_unix_to_windows(filepath):
    return filepath.replace("/", os.sep)


def pemisah_windows_to_unix(filepath):
    return filepath.replace("\\", os.sep)


def path_split(filepath):
    return filepath.split(os.sep)


def bongkar(filepath, normalize=True, debug=False):
    """
    @returns: string bongkared filepath

    intinya: expanduser dan expandvars
    https://docs.python.org/3/library/os.path.html#os.path.expandvars
    $name
    ${name}
    %name% (win32)
    ~
    UPDATE 14-6-2022, kita tambah bisa __PWD
    """
    if "__PWD" in filepath:
        if "ULIBPY__PWD__" in os.environ:
            filepath = filepath.replace(
                "__PWD", os.environ.get("ULIBPY__PWD__", os.getcwd())
            )
        else:
            filepath = filepath.replace("__PWD", os.getcwd())

    pertama = os.path.expanduser(filepath)
    kedua = os.path.expandvars(pertama)

    if filepath == kedua and filepath.startswith("ULIBPY"):
        from .utils import env_replace_filepath

        kedua = env_replace_filepath(kedua)

    if normalize:
        kedua = normy(kedua)

    if debug:
        from rich.pretty import pprint

        pprint(os.environ)

        print(
            f"""[dirutils.bongkar]
		input filepath = {filepath}
		kedua skrg adlh = {kedua}
		cwd adlh = {os.getcwd()}
		"""
        )

    return kedua


def timestamp(time_format="%Y%m%d_%H%M%S"):
    return datetime.datetime.now().strftime(time_format)


def new_filename_timestamp(rootname="delete"):
    return rootname + "_" + timestamp()


def under_tempdir(newdir, persistent=False):
    """
    hasilkan: /tmp/projectdir/
    bukan utk filepath
    utk direktori baru, krn makedirs
    persistent_tempdir adlh ULIBPY_PERSISTENT_TMP, maksudnya krn ditentukan .env maka persistent
    """
    dirpath = os.path.join(persistent_tempdir() if persistent else tempdir(), newdir)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    return dirpath


save_dir_under_tempdir = under_tempdir


def file_under_tempdir(content=None, filename=None, ext=""):
    """
    buat file dalam tempdir
    """
    if not filename:
        filename = "untitled_" + timestamp() + ext

    filepath = os.path.join(tempdir(), filename)

    if not os.path.isfile(filepath):
        pathlib.Path(filepath).touch()

    if content:
        with open(filepath, "w") as fd:
            fd.write(content)

    return filepath


def save_file_under_tempdir(filename, persistent=False):
    """
    hasilkan /tmp/filename
    """
    return joiner(persistent_tempdir() if persistent else tempdir(), filename)


def tempdir(end_with_sepdir=False):
    if end_with_sepdir:
        return tempfile.gettempdir() + pemisah_direktori()
    return tempfile.gettempdir()


def persistent_tempdir():
    return os.environ.get("ULIBPY_PERSISTENT_TMP", "/tmp")


def absolutify(filepath):
    return os.path.abspath(filepath)


def absolute(filepath):
    return os.path.isabs(filepath)


def isabsolute(filepath):
    return absolute(filepath)


def is_absolute(filepath):
    return absolute(filepath)


def relative(filepath):
    return not os.path.isabs(filepath)


def isrelative(filepath):
    return relative(filepath)


def is_relative(filepath):
    return relative(filepath)


def tree(dirpath, excludes='"*.pyc|d"'):
    curdir = dirpath
    if os.path.isfile(dirpath):
        curdir = here(dirpath)

    os.system(f"tree -I {excludes} {curdir}")


def walk_fullpath(basedir, skip_ends=None, filtered_ends=None):
    """
    skip_ends='.pyc' skip file2 berekstensi pyc
    filtered_ends='.py' hanya file2 berekstensi py
    TODO:
    skip && filter, sekarang masih mutually exclusive
    perlu support skip dan filter list, bukan string
    """
    # return [os.path.join(dp,f) for dp,dn,fn in os.walk(basedir) for f in fn]
    if skip_ends:
        return [
            os.path.join(dp, f)
            for dp, _, fn in os.walk(basedir)
            for f in fn
            if not f.endswith(skip_ends)
        ]
    elif filtered_ends:
        return [
            os.path.join(dp, f)
            for dp, _, fn in os.walk(basedir)
            for f in fn
            if f.endswith(filtered_ends)
        ]
    return [os.path.join(dp, f) for dp, _, fn in os.walk(basedir) for f in fn]


# https://docs.python.org/2/library/stat.html
def sort_mtime_walk_fullpath(basedir):
    """
    kembalikan list of tuples = time, fullpath
    """
    # print('sort_mtime_walk_fullpath, basedir:', basedir)
    walker = [
        (os.stat(path)[ST_MTIME], path) for path in walk_fullpath(basedir, ".pyc")
    ]
    return sorted(walker, reverse=True)


def latest_mtime_files(basedir, jumlah=1000):
    return sort_mtime_walk_fullpath(basedir)[:jumlah]


def latest_files(basedir, jumlah=1000):
    """
    item[0] adlh epoch time
    item[1] adlh filepath
    """
    if isinstance(jumlah, str):
        jumlah = int(jumlah)
    if not jumlah:
        jumlah = 1000

    return [item[1] for item in latest_mtime_files(basedir, jumlah)]


def _path_to_mtime(filepath):
    return os.stat(filepath)[ST_MTIME]


def timeify_filelist(filelist):
    """
    file list belum ada time...
    """

    def format(filepath):
        from .datetimeutils import format_epoch_longer

        waktu = format_epoch_longer(_path_to_mtime(filepath))
        # filepath = time_path[1]
        pemisah = "\n" + " " * 25
        return f"{filepath}{pemisah}{waktu}"

    return [format(item) for item in filelist]


def filter_print_latest_files(code, basedir, cetak_waktu=False):
    """
    kita nanti pengen bikin gini
    |50 word1 word2
    jadi dari hasil |50 kita filter yg mengandung word1 dan word2 saja.
    """
    from .printutils import print_list_warna

    # print(f'cetak latest files [code={code}], [dir={basedir}]')
    if not code:
        code = "10"  # minimal bertujuan utk lihat latest files

    m = re.match(r"^(\d+)\s*(.*)", code)
    if m:
        # print(f"ketemu m dg group: {m.groups()}")
        jumlah = m.group(1)
        jumlah = int(jumlah)
        result = latest_files(basedir, jumlah)

        # jk ada words utk ngefilter hasil ls by time
        allfilters = m.group(2)
        if allfilters:
            """
            di sini tentu pake any
            """
            splittedfilters = allfilters.split()
            # print(f"splitted: {splittedfilters}")
            result = [
                item
                for item in result
                if any([word for word in splittedfilters if word in item])
            ]
            # print(f"result: {result}")

        if cetak_waktu:
            # print(f"sblm timeify")
            result_with_time = timeify_filelist(
                result
            )  # latest_files_with_time(basedir, jumlah)
            # print(f"sblm print list warna")
            print_list_warna(result_with_time)
            return result_with_time
        else:
            print_list_warna(result)
            return result


def sort_filelist_tuple(filelist):
    berwaktu = [(os.stat(path)[ST_MTIME], path) for path in filelist]
    return sorted(berwaktu, reverse=True)


def find_patterns(code, basedir, config=None, kurangi_prefix=None, returning=False):
    """
    ./wmc.py:
            find_patterns(code.replace(';', '', 1), self.konfigurasi.cwd(), self.konfigurasi.config)
            config = app.configuration/Configuration/self.all_configs
            config['find_dirs_also']
            config['case_insensitive_pattern_search']
            config['maximum_result']
            config['last_result']
    ;pat -antipat pat2 -antipat2

            patterns+antipatterns
            ternyata ini hanya cari file
            jk ada code yg berupa dir maka tdk masuk result
    """
    from .printutils import print_list

    if not config:
        # from .configuration import Configuration
        # config = Configuration.config
        # TypeError: 'property' object is not subscriptable
        # config = Configuration.all_configs
        # AttributeError: type object 'Configuration' has no attribute 'all_configs'
        find_dirs_also = False
        case_insensitive_pattern_search = True
        maximum_result = 100
    else:
        find_dirs_also = config["find_dirs_also"]
        case_insensitive_pattern_search = config["case_insensitive_pattern_search"]
        maximum_result = config["maximum_result"]

    if not code:
        print("cara gunakan: KODE <pat> <pat> -<antipat> -<antipat>...")
        return
    code = code.strip()
    sort_mtime = False
    if code.endswith("|"):  # sort mtime
        sort_mtime = True
        code = code.rstrip("|")

    # print(f"[dirutils] Searching [{code}] in {basedir}.")
    code = code.split()
    if not code:
        print("cara gunakan: KODE <pat> <pat> -<antipat> -<antipat>...")
        return

    antipatterns = [
        item.replace("-", "", 1) for item in code if re.match(r"^-[\w\d]+", item)
    ]
    patterns = [item for item in code if not re.match(r"^-[\w\d]+", item)]

    if antipatterns:
        if case_insensitive_pattern_search:
            result = walk_fullpath_antipattern_case_insensitive(
                basedir,
                patterns=patterns,
                antipatterns=antipatterns,
                find_dirs_also=find_dirs_also,
            )
        else:
            result = walk_fullpath_antipattern(
                basedir,
                patterns=patterns,
                antipatterns=antipatterns,
                find_dirs_also=find_dirs_also,
            )
    else:
        result = walk_fullpath_pattern(basedir, code, find_dirs_also=find_dirs_also)

    tuple_result = []

    if sort_mtime:
        # print('masuk sort_mtime')
        # from utils import sort_filelist_tuple
        # kembalian sort_filelist berbentuk: filepath<delim>waktu
        tuple_result = sort_filelist_tuple(
            [item.rstrip("*") if item.endswith("*") else item for item in result]
        )
        # print(f'akhir sort_mtime => {tuple_result}')

        original_result = [pair[1] for pair in tuple_result]  # [filepath]
        result = [pair[0] for pair in tuple_result]  # [filepath<delim>waktu]
    else:
        original_result = result

    if kurangi_prefix:
        result = kurangi_list(result, kurangi_prefix)
    # short result adlh jumlah dibatasi smp 100 utk di-print
    short_result = (
        result
        if len(result) < maximum_result
        else result[:maximum_result] + [f"...({len(result)-maximum_result} more)"]
    )
    print_list(short_result)

    if config:
        config["last_result"] = original_result  # digunakan utk digit_process

    if returning:
        return original_result


def replace_inplace(cari, ganti):
    os.system(f"perl -p -i -e 's/{cari}/{ganti}/g'")


def walk_filenames(basedir, skip_ends=None, filtered_ends=None):
    """
    skip_ends='.pyc' skip file2 berekstensi pyc
    filtered_ends='.py' hanya file2 berekstensi py
    """
    # return [os.path.join(dp,f) for dp,dn,fn in os.walk(basedir) for f in fn]
    # if skip_ends:
    #   return [os.path.join(dp, f) for dp, _, fn in os.walk(basedir) for f in fn if not f.endswith(skip_ends)]
    # elif filtered_ends:
    #   return [os.path.join(dp, f) for dp, _, fn in os.walk(basedir) for f in fn if f.endswith(filtered_ends)]
    return [fn for _, _, fn in os.walk(basedir) if fn]  # ada [] utk sebuah dir


def walk_fullpath_relative(basedir, skip_ends=None, filtered_ends=None):
    """
    spt walk_fullpath tetapi relative terhadap basedir

    skip_ends='.pyc' skip file2 berekstensi pyc
    filtered_ends='.py' hanya file2 berekstensi py
    """
    # return [os.path.join(dp,f) for dp,dn,fn in os.walk(basedir) for f in fn]
    if skip_ends:
        return [
            os.path.join(dp, f)
            for dp, _, fn in os.walk(basedir)
            for f in fn
            if not f.endswith(skip_ends)
        ]
    elif filtered_ends:
        return [
            os.path.join(dp, f)
            for dp, _, fn in os.walk(basedir)
            for f in fn
            if f.endswith(filtered_ends)
        ]

    return [
        os.path.relpath(os.path.join(dp, f), basedir)
        for dp, _, fn in os.walk(basedir)
        for f in fn
    ]


def walk_fullpath(basedir, skip_ends=None, filtered_ends=None):
    """
    skip_ends='.pyc' skip file2 berekstensi pyc
    filtered_ends='.py' hanya file2 berekstensi py
    """
    # return [os.path.join(dp,f) for dp,dn,fn in os.walk(basedir) for f in fn]
    if skip_ends:
        return [
            os.path.join(dp, f)
            for dp, _, fn in os.walk(basedir)
            for f in fn
            if not f.endswith(skip_ends)
        ]
    elif filtered_ends:
        return [
            os.path.join(dp, f)
            for dp, _, fn in os.walk(basedir)
            for f in fn
            if f.endswith(filtered_ends)
        ]
    return [os.path.join(dp, f) for dp, _, fn in os.walk(basedir) for f in fn]


def walk_fullpath_skipdirs(basedir, skipdirs=[".git, __pycache__"]):
    """
    khusus walk "files", tdk/bukan "dirs"
    """
    denorm = [
        os.path.join(dp, f)
        for dp, _, fn in os.walk(basedir)
        for f in fn
        if not any([exc for exc in skipdirs if exc in dp])
    ]
    return [os.path.normpath(item) for item in denorm]


def walk_fulldirs(basedir, skipdirs=[".git"], cover=True):
    """
    khusus walk "dirs", tdk/bukan "files"
    """
    denorm = [
        os.path.join(root, d)
        for root, dirs, files in os.walk(basedir)
        for d in dirs
        if not any([exc for exc in skipdirs if exc in dirs])
    ]
    if cover:
        # return [ "["+os.path.normpath(item)+"]" for item in denorm]
        return [os.path.normpath(item) + "*" for item in denorm]
    else:
        return [os.path.normpath(item) for item in denorm]


def walk_full_paths_dirs(basedir, skipdirs=[".git", "__pycache__"]):
    """
    ada
    walk_fullpath_skipdirs
    walk_full_paths_dirs
    ini spt walk_fullpath_skipdirs tapi gak skip dirs!!!
    """
    files = walk_fullpath_skipdirs(basedir, skipdirs)
    dirs = walk_fulldirs(basedir, skipdirs)
    return sorted(dirs + files)


def walk_get_files_dirs(basedir, skipdirs=[".git", "__pycache__"]):
    return walk_full_paths_dirs(basedir, skipdirs)


def walk_fullpath_pattern(
    basedir, patterns=None, pathsep="/", combine_pattern=True, find_dirs_also=False
):
    """
    patterns bisa str atau list
            gunakan pathsep utk nyatakan dir/file

    jk combine_pattern = T dan pats = list maka hanya find yg filenya berisi semua patterns specified
    otherwise, any pattern di patterns akan match
    """
    # print(f"input {patterns}.")
    if isinstance(patterns, str):
        patterns = [patterns.replace(pathsep, os.sep)]
    elif isinstance(patterns, list):
        patterns = [item.replace(pathsep, os.sep) for item in patterns]

    # print(f"processing {patterns}.")
    walker = walk_get_files_dirs if find_dirs_also else walk_fullpath_skipdirs
    allfiles = walker(basedir)

    if combine_pattern:
        selected = filter(lambda f: all([item in f for item in patterns]), allfiles)
    else:
        selected = filter(lambda f: any([item in f for item in patterns]), allfiles)

    selected = list(selected)
    # print(f"files {allfiles}.")
    # print(f"returning {selected}.")
    return selected


def walk_fullpath_antipattern(
    basedir,
    patterns=None,
    antipatterns=None,
    pathsep="/",
    combine_pattern=True,
    find_dirs_also=False,
):
    """
    combine_pattern:
                    semua pattern yg dispecify hrs masuk ke kriteria pencarian
    patterns utk yg diperkenankan ada
    antipatterns utk semua yg tdk diperkenankan ada
    """
    print(f"[dirutils] walk_fullpath_antipattern + {patterns} and - {antipatterns}.")
    if isinstance(patterns, str):
        patterns = [patterns.replace(pathsep, os.sep)]
    elif isinstance(patterns, list):
        patterns = [item.replace(pathsep, os.sep) for item in patterns]

    # print(f"processing {patterns}.")
    # ini fungsi utama walker: walker find files saja atau dirs juga
    walker = walk_get_files_dirs if find_dirs_also else walk_fullpath_skipdirs
    allfiles = walker(basedir)
    # allfiles = walk_fullpath_skipdirs(basedir) # ini gak kita pake dong

    if combine_pattern:
        """
        ini bukannya all(patterns + antipatterns) gampangnya?
        err...antipatterns hrs dibuang, patterns hrs diambil
        """
        # ambil file2 dari daftar yg pattern ada dlm nama file tsb
        pre_selected = filter(
            lambda fullpath: all([item in fullpath for item in patterns]), allfiles
        )

        # print('all+preselected, allfiles#', len(allfiles), 'preselected#', len(pre_selected), 'patterns:', patterns)
        # dari daftar tersebut, hilangkan yg ada antipatternsnya
        selected = filter(
            lambda fullpath: all([item not in fullpath for item in antipatterns]),
            pre_selected,
        )

        # print('all+selected, allfiles#', len(allfiles), 'selected#', len(selected), 'patterns:', patterns)
    else:
        """
        bukannya bisa any(patterns+antipatterns)
        err...antipatterns hrs dibuang, patterns hrs diambil
        """
        pre_selected = filter(lambda f: any([item in f for item in patterns]), allfiles)
        selected = filter(
            lambda fullpath: any([item not in fullpath for item in antipatterns]),
            pre_selected,
        )

    selected = list(selected)
    # print(f"files {allfiles}.")
    # print(f"returning {selected}.")
    return selected


def walk_fullpath_pattern_case_sensitive(
    basedir,
    patterns=None,
    antipatterns=None,
    pathsep="/",
    combine_pattern=True,
    find_dirs_also=False,
):
    """
    patterns bisa str atau list
                                    gunakan pathsep utk nyatakan dir/file

    jk combine_pattern = T dan pats = list maka hanya find yg filenya berisi semua patterns specified
    otherwise, any pattern di patterns akan match
    """
    # print(f"input {patterns}.")
    if isinstance(patterns, str):
        patterns = [patterns.replace(pathsep, os.sep)]
    elif isinstance(patterns, list):
        patterns = [item.replace(pathsep, os.sep) for item in patterns]

    # print(f"processing {patterns}.")
    walker = walk_get_files_dirs if find_dirs_also else walk_fullpath_skipdirs
    allfiles = walker(basedir)

    if combine_pattern:
        pre_selected = filter(
            lambda arsip: all([item in arsip for item in patterns]), allfiles
        )
        selected = filter(
            lambda arsip: all([item not in arsip for item in antipatterns]),
            pre_selected,
        )
    else:
        pre_selected = filter(
            lambda arsip: any([item in arsip for item in patterns]), allfiles
        )
        selected = filter(
            lambda arsip: any([item not in arsip for item in antipatterns]),
            pre_selected,
        )

    selected = list(selected)
    # print(f"files {allfiles}.")
    # print(f"returning {selected}.")
    return selected


def walk_fullpath_antipattern_case_insensitive(
    basedir,
    patterns=None,
    antipatterns=None,
    pathsep="/",
    combine_pattern=True,
    find_dirs_also=False,
):
    """
    patterns utk yg diperkenankan ada
    antipatterns utk semua yg tdk diperkenankan ada
    find_dirs_also
                    item/
                    item.exe
                    akan diperoleh dari search "item"

    """
    print(
        f"[dirutils] walk_fullpath_antipattern_case_insensitive + {patterns} and - {antipatterns}, all over any: {combine_pattern}."
    )
    if isinstance(patterns, str):
        patterns = [patterns.replace(pathsep, os.sep)]
    elif isinstance(patterns, list):
        patterns = [item.replace(pathsep, os.sep) for item in patterns]

    # print(f"processing {patterns}.")
    walker = (
        walk_get_files_dirs if find_dirs_also else walk_fullpath_skipdirs
    )  # ini fungsi utama walker
    allfiles = walker(basedir)
    # allfiles = walk_fullpath_skipdirs(basedir) # ini gak kita pake dong

    if combine_pattern:
        # semua pattern hrs dipenuhi
        pre_selected = filter(
            lambda arsip: all([item.lower() in arsip.lower() for item in patterns]),
            allfiles,
        )
        selected = filter(
            lambda arsip: all(
                [item.lower() not in arsip.lower() for item in antipatterns]
            ),
            pre_selected,
        )
    else:
        # any pattern dipenuhi saja cukup
        pre_selected = filter(
            lambda arsip: any([item.lower() in arsip.lower() for item in patterns]),
            allfiles,
        )
        selected = filter(
            lambda arsip: any(
                [item.lower() not in arsip.lower() for item in antipatterns]
            ),
            pre_selected,
        )

    selected = list(selected)
    # print(f"files {allfiles}.")
    # print(f"returning {selected}.")
    return selected


def make_folder(folder, basedir=".", silent=False):
    """
    silent = no exception if exist
    """
    folderpath = os.path.join(basedir, folder)
    if not os.path.isdir(folderpath):
        if silent:
            create_dir_silent(folderpath)
        else:
            create_dir(folderpath)


def create_dir_silent(folder):
    """
    https://stackoverflow.com/questions/273192/how-can-i-safely-create-a-nested-directory-in-python
    mkpath creates the nested directory, and does nothing if the directory already exists.
    This works in both Python 2 and 3.
    """
    import distutils.dir_util

    distutils.dir_util.mkpath(folder)


def create_dir_with_parent(folder):
    """
    pathlib.Path.mkdir as used above recursively creates the directory
    and does not raise an exception if the directory already exists.
    If you don't need or want the parents to be created,
    skip the parents argument.
    """
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)


def create_dir(folder):
    try:
        os.makedirs(folder)
    except OSError as e:
        if e.errno != errno.EEXIST and os.path.isdir(folder):
            raise


def create_if_empty_dir(dirpath):
    if not os.path.exists(dirpath):
        create_dir(dirpath)


def kurangi(banyak, dikit):
    """
    pada dasarnya ini relpath yg terima (lokasi-input, starting-dir)
    /a/b/c/d, /a/b
    hasilkan: c/d
    """
    # ini gak elegant
    # return banyak.replace(dikit, '', 1).strip()
    return os.path.relpath(banyak, dikit)


def kurangi_list(the_list, dikit):
    """
    utk list of filepaths, kita kurangi
    """
    return [kurangi(item, dikit) for item in the_list]


def first_part_of_relative_dir(filepath, starting_dir):
    """
    filepath: /a/b/c/d
    starting_dir: /a
    kita pengen terima "basename": b

    satu = '/a/b/c/d/'
    dua = '/a'
    Path.relative_to(Path(satu), Path(dua))
    => WindowsPath('b/c/d')
    Path.relative_to(Path(satu), Path(dua)).parts[0]
    => b
    """
    from pathlib import Path

    b = Path.relative_to(Path(filepath), Path(starting_dir)).parts[0]
    return b


def get_latest_file_in_dir(basedir=HOMEDIR):
    """
    kita pengen: screenshot -> file -> base64
    import (image magick)
    gnome-screenshot -a -f namafile -> subprocess sampai errno success
    """
    import glob

    list_of_files = glob.glob(f"{basedir}/*")
    latest_file = max(list_of_files, key=os.path.getctime)
    # print(latest_file)
    return latest_file


def within_same_folder(filepath, filename):
    return joiner(here(filepath), filename)


def first_part(dirpath):
    """
    /a/b/c/d -> /a
    """
    bagian = pathlib.Path(dirpath).parts
    if len(bagian) >= 2:
        return bagian[0] + bagian[1]

    return ""


def is_windows_drive(filepath):
    """
    c:\...
    """
    return re.match(r"^[c-z]:", filepath.lower())


def is_wsl_drive(filepath):
    return not is_windows_drive(filepath)
