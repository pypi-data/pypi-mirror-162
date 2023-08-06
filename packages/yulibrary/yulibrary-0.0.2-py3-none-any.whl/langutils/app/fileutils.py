import datetime
import json
import os
import pathlib
import re
import stat
from pathlib import Path
from shutil import copyfile

from .utils import env_exist, env_expand, env_get, env_int, trycopy, trypaste


def chmod(filepath, stringmode="600"):
    """
    https://stackoverflow.com/questions/15607903/python-module-os-chmodfile-664-does-not-change-the-permission-to-rw-rw-r-bu
    """
    os.chmod(filepath, int(stringmode, base=8))


def chmodrwx(filepath):
    """Removes 'group' and 'other' perms. Doesn't touch 'owner' perms.
    S_IRUSR  (00400)  read by owner
    S_IWUSR  (00200)  write by owner
    S_IXUSR  (00100)  execute/search by owner
    S_IRGRP  (00040)  read by group
    S_IWGRP  (00020)  write by group
    S_IXGRP  (00010)  execute/search by group
    S_IROTH  (00004)  read by others
    S_IWOTH  (00002)  write by others
    S_IXOTH  (00001)  execute/search by others

    Note: Although Windows supports chmod(), you can only set the file’s read-only flag with it (via the stat.S_IWRITE and stat.S_IREAD constants or a corresponding integer value). All other bits are ignored.

    """
    mode = os.stat(filepath).st_mode
    mode -= mode & (stat.S_IRWXG | stat.S_IRWXO)
    os.chmod(filepath, mode)


def get_umask():
    umask = os.umask(0)
    os.umask(umask)
    return umask


def chmod_plus_x(filepath):
    """
    https://stackoverflow.com/questions/12791997/how-do-you-do-a-simple-chmod-x-from-within-python/55591471#55591471
    """
    os.chmod(
        filepath,
        os.stat(filepath).st_mode
        | ((stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH) & ~get_umask()),
    )


def absolute(filepath):
    return os.path.isabs(filepath)


def to_absolute(filepath):
    return os.path.abspath(filepath)


def editfile(dir_or_file):
    os.system(f"code {dir_or_file}")


def perintah(command):
    os.system(command)


def copy_file(src, dst):
    copyfile(src, dst)


def copy_content(filepath):
    trycopy(file_content(filepath))


def json_file_content(json_filepath):
    try:
        with open(json_filepath) as fd:
            return json.load(fd)
    except Exception as err:
        print(f"[fileutils] opening: {json_filepath}", err)
        return None


def json_file_print(json_filepath):
    json_body = json_file_content(json_filepath)
    print(json.dumps(json_body, indent=4))
    return json_body


def json_from_string(content):
    return json.loads(content)


def json_stringify(content, indent=True):
    if indent:
        return json.dumps(content, indent=4)
    return json.dumps(content)


def file_sentences(filepath):
    data = None
    with open(filepath, "r", encoding="utf-8") as fd:
        data = fd.read().replace("\n", "")

    return data


def file_content(filepath):
    """
    retval berupa segelondongan text/string
    https://stackoverflow.com/questions/45529507/unicodedecodeerror-utf-8-codec-cant-decode-byte-0x96-in-position-35-invalid
    update utk:
    'utf-8' codec can't decode byte 0x93 in position 68384: invalid start byte
    errors='ignore'
    """
    return pathlib.Path(filepath).read_text(encoding="utf8", errors="ignore")


def file_content_binary(filepath):
    import io

    content = None
    with io.open(filepath, "rb") as binary_file:
        content = binary_file.read()
    return content


def file_content_ascii(filepath):
    return pathlib.Path(filepath).read_text(encoding="utf-8")


def file_content_safe(filepath):
    """
    retval berupa segelondongan text/string
    kadang kasus https://stackoverflow.com/questions/42339876/error-unicodedecodeerror-utf-8-codec-cant-decode-byte-0xff-in-position-0-in
    invalid start byte.
    """
    # return pathlib.Path(filepath).read_text(encoding='utf-8')
    path_obj = pathlib.Path(filepath)
    try:
        content = path_obj.read_text(encoding="utf-8")
    except Exception as err:
        # https://stackoverflow.com/questions/42339876/error-unicodedecodeerror-utf-8-codec-cant-decode-byte-0xff-in-position-0-in
        # bisa jadi dia utf16
        content = path_obj.read_bytes()
        if env_int("ULIBPY_FMUS_DEBUG") > 1:
            print("file_content:", filepath, "PRE decode bytes to utf8")
        content = content.decode("utf-16")
        if env_int("ULIBPY_FMUS_DEBUG") > 1:
            print("file_content:", filepath, "POST decode bytes to utf8")
    return content


def file_content_old(filepath):
    """
    retval berupa segelondongan text/string
    """
    content = None
    with open(filepath, encoding="utf-8") as fd:
        content = fd.read()

    return content


def file_copy(lama, baru):
    file_write(baru, file_content(lama))


def count_lines(filepath):
    return len(file_lines)


def file_lines(filepath, strip_newline=False, skip_emptylines=False):
    """
    retval [line1, line2, ...]
    """
    content = None
    with open(filepath, encoding="utf-8") as fd:
        content = fd.readlines()

    if skip_emptylines:
        content = [item for item in content if item.strip()]

    if strip_newline:
        return [item.rstrip() for item in content]
    else:
        return content


def file_blocks(filepath, delimiter="#####", strip_newline=False):
    """
    kembalikan list of block dlm file terpisah delimiter
    digunakan di app.transpiler.snippets utk cari di dalam snippets.txt
    """
    content = file_content(filepath)
    content = content.split(delimiter)
    return [item.strip() if strip_newline else item for item in content if item.strip()]


def non_empty_lines(lines):
    return [item for item in lines if item.strip()]


def file_words(filepath):
    """
    kembalikan list of words
    pd gabung, empty line jadi extra space
    dg split(), multiple space setara satu space, jadi hilang dlm hasil akhir
    """
    content = file_lines(filepath)
    # hilangkan empty lines
    # bisa juga [item for item in content if item.strip()]
    gabung = " ".join([item.strip() for item in content])
    return gabung.split()


def line_contains(filepath, kunci):
    return [item for item in file_lines(filepath) if kunci in item]


def create_if_empty_file(filepath):
    if not os.path.exists(filepath):
        pathlib.Path(filepath).touch()


def get_extension(filepath, no_dot=True):
    """
    with_dot	-> .txt
    no_dot 		-> txt
    """
    if no_dot:
        return pathlib.Path(filepath).suffix[1:]

    return pathlib.Path(filepath).suffix


def get_filename_full(filepath):
    """
    renaming path_filename
    /home/usef/untitled.txt -> untitled.txt
    """
    return os.path.basename(filepath)


def get_filename_part(filepath):
    """
    get_filename dg nama yg benar
    """
    return pathlib.Path(filepath).stem


def get_filename(filepath):
    """
    harusnya dinamai: get_filename_part
    path_filename			-> untitled.txt
    get_filename			-> untitled

    biasanya os.path.splitext(path)[0]
    lebih baik pake Path
    >>> Path('/a/b/c/d/untitled.txt').stem
    'untitled'

    untitled.txt -> untitled
    """
    return pathlib.Path(filepath).stem


def get_lastpath_and_filename(filepath):
    """
    ini beresiko jk parent gak dapat etc
    """
    # return pathlib.Path(filepath).stem
    return pathlib.Path(filepath).parent.stem + "/" + pathlib.Path(filepath).stem


def path_filename(filepath):
    """
    /home/usef/untitled.txt -> untitled.txt
    """
    return os.path.basename(filepath)


def path_dirname(filepath):
    """
    /home/usef/untitled.txt -> /home/usef
    """
    return os.path.dirname(filepath)


def get_dirname(filepath):
    return path_dirname(filepath)


def file_remove(filepath):
    """
    os.remove() removes a file.
            If the file doesn't exist, os.remove() throws an exception, so it may be necessary to check os.path.isfile() first, or wrap in a try
            the exception thrown by os.remove() if a file doesn't exist is FileNotFoundError
            missing_ok=True, added in 3.8 solves that!
    os.rmdir() removes an empty directory.

    shutil.rmtree() deletes a directory and all its contents.

    Path objects from the Python 3.4+ pathlib module also expose these instance methods:

    pathlib.Path.unlink() removes a file or symbolic link.
            file_to_rem = pathlib.Path("/tmp/<file_name>.txt")
            file_to_rem.unlink()

            Path.unlink(missing_ok=False)
            Unlink method used to remove the file or the symbolik link.

            If missing_ok is false (the default), FileNotFoundError is raised if the path does not exist.
            If missing_ok is true, FileNotFoundError exceptions will be ignored (same behavior as the POSIX rm -f command).
            Changed in version 3.8: The missing_ok parameter was added.
    pathlib.Path.rmdir() removes an empty directory.
    """
    if os.path.exists(filepath):
        os.remove(filepath)
    else:
        print(f"{filepath} not found")


def dir_remove(dirpath):
    os.rmdir(dirpath)


def write_list(filepath, daftar, combiner="\n"):
    with open(filepath, mode="w", encoding="utf8") as fd:
        fd.write(combiner.join(daftar))


def write_file(filepath, text, write_mode="w"):
    with open(filepath, mode=write_mode, encoding="utf8") as fd:
        fd.write(text)


def file_write(filepath, text, write_mode="w"):
    write_file(filepath, text, write_mode=write_mode)


def append_file(filepath, text):
    with open(filepath, mode="a", encoding="utf8") as fd:
        fd.write(text)


def file_append(filepath, text):
    append_file(filepath, text)


def clipboard_to_file(filepath):
    content = trypaste()
    with open(filepath, "w", encoding="utf-8") as fd:
        fd.write(content)


def del_lines(filepath, baris_regex):
    """
    https://stackoverflow.com/questions/4710067/using-python-for-deleting-a-specific-line-in-a-file
    contoh baris_regex: "^p$" atau "^p\\s*$"
    tentu juga:
    "^#"
    """
    with open(filepath, mode="r+", encoding="utf8") as fd:
        content = fd.readlines()
        fd.seek(0)
        for line in content:
            m = re.match(baris_regex, line)
            if not m:
                fd.write(line)
        fd.truncate()  # hapus sisa baris2


def mk_file_to_dict(filepath, reverse=True):
    """
    utk auto completer agar

    int main() { ..	| main function
    """
    dictionary_result = {}
    dictionary_result_reverse = {}

    entry_header = None
    entry_body = []
    collecting = False
    with open(filepath, encoding="utf-8") as fd:
        for line in fd.readlines():
            if collecting:
                if re.search(r"^--#", line):
                    entry_content = "".join(entry_body)
                    entry_content = entry_content.strip()

                    dictionary_result.update({entry_header: entry_content})
                    dictionary_result_reverse.update({entry_content: entry_header})
                    entry_body = []
                    collecting = False
                else:
                    entry_body.append(line)
            elif re.search(r"^\s*--%\s+", line):
                # entah kenapa entry kedua dst suka \n--% baris
                entry_header = line.replace("--%", "", 1).strip()
                collecting = True

    if reverse:
        return dictionary_result_reverse

    return dictionary_result


def kurangi(banyak, dikit):
    """
    string arithmetic:
    kurangi(sebuah_nama_panjang, sebuah_nama)
    hasilkan: _panjang
    """
    return banyak.replace(dikit, "", 1).strip()


def line_number_expression(content_length, line_expression):
    """
    memproses expression spt berikut:
            1
            ~
            1-5,17,~
            17-~

    @returns:
    list of line numbers indexed from 0

    @usage:
    content = file read lines
    line_nos = line_number_expression(len(content), line_expression)
            kita butuh len(content) krn butuh representasi ~ sbg last line
    content_with_indexes = [(index, baris) for (index, baris) in enumerate(content)]
    result = [
            (process(baris) if index in line_nos else baris)
            for (index, baris) in content_with_indexes]
    if result:
            write lines to file(result)
    """
    result = []
    # content_length = len(line_of_contents)
    for expr in [item.strip() for item in line_expression.split(",")]:
        if "-" in expr:
            start, end = [item.strip() for item in expr.split("-")]
            start = int(start) - 1
            if end == "~":
                end = content_length  # krn utk range
            else:
                end = int(end)
            for k in range(start, end):
                result.append(k)
        else:
            if expr == "~":
                k = content_length - 1  # krn utk indexing
            else:
                k = int(expr) - 1
            result.append(k)
    return result


def against_regex(regexfile, filepath):
    """
    u -e"/file>rx/rx.txt|users.txt"
    isi rx.txt:
    (?P<id>\d+)\t(?P<firstname>\w+)\t(?P<lastname>\w+|\-|\s)\t(?P<phone>\d+)\t(?P<email>[\.\w+]+@[\w]+\.[\w]+)\t(?P<pwd>[\w\$\/\.]+)\t(?P<enabled>1|0)\t(?P<activated>1|0)\t(?P<token>\w+|\\N)\t(?P<confirm_code>\d+)\t(?P<note>\\N)\t(?P<cr_date>[\d\-]+\s[\d:]+\.[\d\+]+)\t(?P<activated_date>[\d\-]+\s[\d:]+\.[\d\+]+|\\N)\t(?P<old_email>\\N)\t(?P<old_email_verify_code>\\N)\t(?P<old_phone>\\N)\t(?P<old_phone_verify_code>\\N)\t(?P<new_email>\\N)\t(?P<new_email_verify_code>\\N)\t(?P<new_phone>\\N)\t(?P<new_phone_verify_code>\\N)\t(?P<kyc_flag>1|0)\t(?P<setuju_snk>1|0)\t(?P<tgl_setuju_snk>[\d\-]+\s[\d:]+\.[\d\+]+|\\N)\t(?P<progres_registrasi>\d+)\t(?P<progres_kyc>\d+)\t(?P<lastlogin>[\d\-]+\s[\d:]+\.[\d\+]+|\\N)\t(?P<customerno>\\N)\t(?P<flag_login>1|0)\t(?P<fcm_token>[\w\d\-_:]+|\\N)\t(?P<role>\w+|\\N)\t(?P<referral_code>\w+|\\N)\t(?P<referrer_id>\\N)\t(?P<profile_image>[\w\d:\/\.]+|\\N)\t(?P<change_data_info>\\N)
    """
    from .dirutils import isfile
    from .printutils import indah4

    if not isfile(regexfile) and isfile(filepath):
        print(f"no regexfile {regexfile} and no targetfile {filepath}")
        return
    regexpattern = file_content(regexfile).strip()
    content = file_lines(filepath)
    # indah4(f'''[against_regex]
    # pattern = [{regexpattern}]
    # ''', warna='white')
    # result = []

    # content_with_indexes = [(index, baris) for (index, baris) in enumerate(content)]
    # result = [(baris.replace('\n', appender+'\n') if index in lines else baris) for (index,baris) in content_with_indexes]
    match_counter = 0
    for (index, baris) in enumerate(content):
        # coba = re.match(regexpattern, baris)
        coba = re.search(regexpattern, baris)
        if coba:
            match_counter += 1


def view_lines_between(filepath, baris_cari_start, baris_cari_end=None):
    """
    print lines antara /baris_cari_start/ dan /baris_cari_end/
    """
    from .dirutils import isfile

    if not isfile(filepath):
        print(f"{filepath} not found")
        return None

    content = None

    with open(filepath, "r", encoding="utf-8") as fd:
        content = fd.readlines()

    # print('content:', content if len(content)<10 else f'{len(content)} lines')
    # print('\n\n\n', '='*40, filepath)

    if content:
        mulai = [item for item in content if baris_cari_start in item]
        mulai = mulai[-1]  # mulai paling late
        index_mulai = content.index(mulai)
        if baris_cari_end:
            akhir = [item for item in content if baris_cari_end in item]
            if len(mulai) >= 1 and len(akhir) >= 1:  # ambil yg pertama match
                # mulai = mulai[0]
                # print('found akhir:', akhir)
                # get akhir yg > mulai
                filtered_bigger = [
                    item for item in akhir if content.index(item) >= index_mulai
                ]
                if filtered_bigger:
                    akhir = filtered_bigger[0]  # akhir paling early
                    index_akhir = content.index(akhir)
                    # print(f'index mulai {index_mulai} dan index akhir {index_akhir}')
                    content = content[index_mulai : index_akhir + 1]
                    return content
        else:
            return content[index_mulai:]

    return None


def tab_to_space_all(filepath, tabstop=2):
    content = file_content(filepath)
    write_file(content.replace("t", tabstop * " "))


def tab_to_space_start(filepath, tabstop=2):
    if env_exist("ULIBPY_TABSPACE"):
        tabstop = env_int("ULIBPY_TABSPACE")

    content = file_content(filepath)
    baca = content.splitlines()
    hasil = []
    for line in baca:
        m = re.match("^(\s+)(\S.*)+", line)
        if m:
            ubah = m.group(1)
            isi = m.group(2)
            # print(line, f' => [{ubah}]')
            hasil.append(ubah.replace("\t", tabstop * " ") + isi)
        else:
            # print('*no*', line)
            hasil.append(line)

    result = "\n".join(hasil)

    write_file(filepath, result)


def space_to_tab_start(filepath, tabstop=2):
    if env_exist("ULIBPY_TABSPACE"):
        tabstop = env_int("ULIBPY_TABSPACE")

    content = file_content(filepath)
    baca = content.splitlines()
    hasil = []
    for line in baca:
        m = re.match("^(\s+)(\S.*)+", line)
        if m:
            ubah = m.group(1)
            isi = m.group(2)
            # print(line, f' => [{ubah}]')
            # hasil.append(ubah.replace('\t', tabstop*' ') + isi)
            hasil.append(ubah.replace(tabstop * " ", "\t") + isi)
        else:
            # print('*no*', line)
            hasil.append(line)

    result = "\n".join(hasil)

    write_file(filepath, result)


def find_entry_by_content(filepath, content_pattern, search_with_in=True):
    """
    utk content-based search
    teknik sementara:
    if content_pattern in baris
    """
    content = []
    with open(filepath, encoding="utf-8") as fd:
        content = fd.readlines()
    if search_with_in:
        lokasi = [
            (index, item)
            for (index, item) in enumerate(content)
            if content_pattern in item
        ]
    else:
        # search dg regex
        lokasi = [
            (index, item, re.match(content_pattern, item))
            for (index, item) in enumerate(content)
            if re.match(content_pattern, item)
        ]

    if lokasi:
        ketemu = lokasi[0]
        if len(lokasi) > 1:
            print(f"multi {len(lokasi)} matches:", lokasi)

    # cari top, for item in reversed(list[:mundur])
    # cari bottom, for item in list[maju:]


def ulib_history():
    # import sys, tempfile

    disini = os.path.realpath(__file__)
    disini = os.path.dirname(disini)  # schnell/app
    disini = os.path.join(disini, os.pardir, os.pardir, "data")
    disini = os.path.abspath(disini)
    filename = "ulibpy.hist"

    file_location = os.path.join(disini, filename)
    # print('ulib_history', file_location)
    # if env_exist('ULIBPY_HISTORY_FILE'):
    # 	file_location = env_get('ULIBPY_HISTORY_FILE')
    # 	if sys.platform == 'win32' and env_exist('ULIBPY_HISTORY_FILE_WIN32'):
    # 		file_location = os.path.join(tempfile.gettempdir(), env_get('ULIBPY_HISTORY_FILE_WIN32'))

    return file_location
