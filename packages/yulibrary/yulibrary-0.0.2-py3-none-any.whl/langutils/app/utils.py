import json
import os
import random
import subprocess
import time
import uuid
import webbrowser
from platform import uname as std_uname

from dotenv import load_dotenv

try:
    import readline
except ImportError as err:
    import pyreadline


def u():
    return str(uuid.uuid4())


def platform():
    """
    kembalian:
    linux
    windows
    wsl

    uname_result(system='Windows', node='DESKTOP-7EO5LQL', release='10', version='10.0.19041', machine='AMD64')
    uname_result(system='Windows', node='user-PC', release='10', version='10.0.19044', machine='x86')
    uname_result(system='Linux', node='DESKTOP-7EO5LQL', release='5.4.72-microsoft-standard-WSL2', version='#1 SMP Wed Oct 28 23:40:43 UTC 2020', machine='x86_64')
    uname_result(system='Linux', node='localhost', release='4.4.111-21737876', version='#1 SMP PREEMPT Thu Jul 15 19:28:19 KST 2021', machine='aarch64')
    $ uname -a
    Linux localhost 4.4.111-21737876 #1 SMP PREEMPT Thu Jul 15 19:28:19 KST 2021 aarch64 Android
    """
    kembalian = [
        "linux",  # 0
        "windows",  # 1
        "wsl",  # 2
        "termux",  # 3
        "desktop",  # 4
    ]
    machine = std_uname()
    sistem = machine.system.lower()
    rilis = machine.release.lower()
    mesin = machine.machine.lower()
    # print(f'sis: {sistem}, ril: {rilis}, uname: {machine}')
    if "windows" in sistem:  # sys.platform == 'win32'
        if mesin == "x86":
            return kembalian[4]  # pc desktop 32-bit
        return kembalian[1]
    elif "microsoft" in rilis and "linux" in sistem:
        return kembalian[2]
    elif sistem == "linux" and machine.machine == "aarch64":
        return kembalian[3]
    else:
        return kembalian[0]


def uname():
    """
    desktop
    uname_result(system='Windows', node='user-PC', release='10', version='10.0.19044', machine='x86')
    """
    return std_uname()


def isdesktop():
    sistem = uname()
    return (
        sistem.node == "user-PC"
        and sistem.system == "Windows"
        and sistem.machine == "x86"
    )


def env_get(kunci, default=None):
    if kunci in os.environ:
        return os.environ[kunci]
    return default


# platform == linux
PBPASTE = "xclip -selection clipboard -o"
PBCOPY = "xclip -selection clipboard"

if platform() != "linux":
    PBPASTE = "pbpaste"
    PBCOPY = "pbcopy"


TRANSLATE = "https://translate.google.com/?hl=en&ie=UTF-8&sl=__SOURCE&tl=__TARGET__TEXTPLACEHOLDER__&op=translate"
GOOGLESEARCH = "https://www.google.com/search?q=__TEXTPLACEHOLDER__"
# https://translate.google.com/?hl=en&ie=UTF-8&sl=en&tl=id&op=translate
# https://translate.google.com/?hl=en&ie=UTF-8&sl=en&tl=id&text=libertarian&op=translate

# https://www.google.com/search?client=firefox-b-e&q=christopher+hitchens
# https://www.google.com/search?q=christopher+hitchens

WEBSITES = {
    "https://translate.google.com/?hl=en&ie=UTF-8&sl=en&tl=id&op=translate",
    "https://www.smh.com.au/",
    "https://www.dailymail.co.uk/ushome/index.html",
    "https://www.dailymail.co.uk/auhome/index.html",
    "https://www.scmp.com/",
    "https://stackoverflow.com/questions",
    "https://www.upwork.com/freelance-jobs/python/",
    "http://fulgent.be/m/college/jobs.html",
    "https://leetcode.com/explore/",
    "https://www.glassdoor.com/Job/jakarta-senior-software-developer-jobs-SRCH_IL.0,7_IC2709872_KO8,33.htm?fromAge=3&includeNoSalaryJobs=true",
    "https://www.jobstreet.co.id/en/job-search/senior-software-engineer-jobs/?sort=createdAt",
    "https://remoteok.io/remote-dev-jobs?location=worldwide",
    "https://remotive.io/remote-jobs/software-dev?live_jobs%5Btoggle%5D%5Bus_only%5D=true&live_jobs%5BsortBy%5D=live_jobs_sort_by_date&live_jobs%5Bmenu%5D%5Bcategory%5D=Software%20Development",
    "https://angel.co/jobs?ref=onboarding",
}

PROGRAMS = {
    # "C:\Program Files\Mozilla Firefox\firefox.exe"
    # /mnt/c/Program Files/Mozilla Firefox
    # 'ff'					: '/usr/bin/firefox -no-remote -P',
    # "C:\Program Files\Google\Chrome\Application\chrome.exe"
    # "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"
    # 'ff'				: env_get('SIDOARJO_FIREFOX'),
    "ff": '"C:/Program Files/Mozilla Firefox/firefox.exe" -no-remote -P',
    "ffacer": '"C:/Program Files/Mozilla Firefox/firefox.exe" -no-remote -P',
    "chr": "chromium-browser",
    # 'chrome'			: '/opt/google/chrome/chrome',
    # 'chrome'			: '"/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"',
    "chrome": '"C:/Program Files/Google/Chrome/Application/chrome.exe"',
    "term": '"cmd /k start"',
    "qterm": "qterminal",
    "term2": "gnome-terminal",
    "gterm": "gnome-terminal",
    "xterm": "xterm",
    "xemu": "x-term-emulator",
    "xdg": "xdg-open",
    "atom": "atom",
    "code": "code",
    "note": "notepad",
    "npp": '"C:/Program Files/Notepad++/notepad++.exe"',
}

# initial
curdir = os.path.dirname(__file__)
SCHNELLDIR = env_get("ULIBPY_BASEDIR", os.path.join(curdir, ".."))


def pbcopy_pbpaste():
    global SCHNELLDIR, PBPASTE, PBCOPY
    if env_get("ULIBPY_BASEDIR"):
        SCHNELLDIR = env_get("ULIBPY_BASEDIR")
    if platform() == "linux":
        pass
    elif platform() == "wsl":
        if env_get("PBCOPY_WSL"):
            PBCOPY = env_get("PBCOPY_WSL")
        if env_get("PBPASTE_WSL"):
            PBPASTE = env_get("PBPASTE_WSL")
        # print(f'wsl => schnelldir {SCHNELLDIR}, pbcopy {PBCOPY} dan pbpaste {PBPASTE}')


LANGUAGES = [
    "awk",
    "sh",
    "bat",
    "clang",  # utk modern cpp
    "cpp",
    "cs",
    "css",
    "clj",
    "dart",
    "ex",
    "erl",
    "go",
    "groovy",
    "hs",
    "java",
    "js",
    "kt",
    "perl",
    "php",
    "py",  # agar bisa :py -> if code in languages
    # tapi ini di handle di cleanup_bahasa
    "python",
    "r",
    "rb",
    "rs",
    "scala",
    "sed",
    "swift",
    "ts",
]


try:
    import pyperclip
except ImportError as err:
    pass

from importlib import import_module as std_import_module

from faker import Faker

faker_instance = Faker()


def import_from_string(fq_classname):
    """
    app.transpiler.frontend.fslang.flask.Coordinator
    module:
            app.transpiler.frontend.fslang.flask
    class_name:
            Coordinator
    krn teknik berikut
            module_path, class_name = fq_classname.rsplit('.', 1)
    kita juga bisa:
            app.notfutils.pynotif
            dimana pynotif adlh fungsi
            import_from_string('app.notfutils.pynotif')(judul, badan)
    class_str: str = 'A.B.YourClass'
    """
    try:
        module_path, class_name = fq_classname.rsplit(".", 1)
        module = std_import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise ImportError(fq_classname)


def faker(methodname, *args, **kwargs):
    if hasattr(faker_instance, methodname):
        return getattr(faker_instance, methodname)(*args, **kwargs)

    return None


def print_faker(methodname, *args, **kwargs):
    hasil = None

    if hasattr(faker_instance, methodname):
        hasil = getattr(faker_instance, methodname)(*args, **kwargs)

    if hasil:
        print(hasil)


def printcopy_faker(methodname, *args, **kwargs):
    hasil = None

    if hasattr(faker_instance, methodname):
        hasil = getattr(faker_instance, methodname)(*args, **kwargs)

    if hasil:
        trycopy(hasil)
        print(hasil)


def acak(min=0, max=100):
    return random.randint(min, max)


def ambil(datalist):
    return random.choice(datalist)


def sampling(datalist, k=1, stringify=False):
    """
    random.choices population tetap
    random.sample population berkurang
    """
    if stringify:
        return "\n".join(random.sample(datalist, k))
    return random.sample(datalist, k)


def tidur(s=0.0, ms=0.0):
    if s:
        time.sleep(s)
    elif ms:
        time.sleep(ms / 1000.0)


def env_add(kunci, nilai):
    os.environ[kunci] = nilai


def env_set(kunci, nilai):
    if isinstance(nilai, int):
        nilai = str(nilai)
    os.environ[kunci] = nilai


def env_exist(kunci):
    return kunci in os.environ


def env_get_fuzzy(code):
    # envulibs = env_ulibpy_values()
    result = [item for item in env_ulibpy() if code.lower() in item.lower()]
    if result:
        return result[0]

    return None


def env_ulibpy():
    daftar = os.environ
    return [item for item in daftar if item.startswith("ULIBPY")]


def env_ulibpy_values():
    daftar = os.environ
    return [f"{item} = {env_get(item)}" for item in daftar if item.startswith("ULIBPY")]


def env_replace_filepath(filepath, normalize=False):
    for envvar in env_ulibpy():
        expanded = env_get(envvar)
        # if envvar in filepath:
        # 	print(f'expanding {envvar} => {expanded}')
        filepath = filepath.replace(envvar, expanded)
    if normalize:
        from .dirutils import normy

        filepath = normy(filepath)
    return filepath


def expand_ulib_path(filepath):
    # print('old filepath:', filepath)
    if "ULIBPY_" in filepath:
        # from .utils import env_replace_filepath
        filepath = env_replace_filepath(filepath, normalize=True)
        # print('new filepath:', filepath)
    return filepath


def env_print(only_ulibpy=True):
    daftar = os.environ
    if only_ulibpy:
        daftar = [item for item in daftar if item.startswith("ULIBPY")]

    print(json.dumps(daftar, indent=4))


def env_int(kunci, default=0):
    if kunci in os.environ:
        return int(os.environ[kunci])
    return default


def env_reload():
    # ULIBPY_BASEDIR
    if "ULIBPY_BASEDIR" in os.environ:
        filepath = env_get("ULIBPY_BASEDIR")
    else:
        filepath = os.path.join(os.path.dirname(__file__), os.path.pardir)
    env_file = os.path.join(filepath, ".env")
    load_dotenv(env_file)
    print("environ reloaded...")


def env_load(env_file=os.path.join(SCHNELLDIR, ".env")):
    load_dotenv(env_file)


def env_expand(source, special_resources="gaia", bongkarin=False):
    """
    expand ULIBPY_... in string
    kita bikin special agar ngetik gak capek:
    gaia => ULIBPY_RESOURCES

    bongkarin => expand ~, shell vars, dll
    """
    from .dirutils import bongkar

    source = source.replace(special_resources, "ULIBPY_RESOURCES")

    for k in os.environ:
        if k.startswith("ULIBPY"):
            source = source.replace(k, os.environ[k])

    if bongkarin:
        return bongkar(source)
    else:
        return source


def env_expand_removeprefix(source, prefix, remove_strip=True):
    source = source.removeprefix(prefix)
    if remove_strip:
        source = source.strip()
    return env_expand(source)


def trycopy(content):
    try:
        pyperclip.copy(content)
    except Exception as err:
        pass


def trypaste():
    try:
        content = pyperclip.paste()
        return content
    except Exception as err:
        return None


def try_copy(content):
    trycopy(content)


def try_paste():
    return trypaste()


def yesno(message, yes_callback=None, warna="bright_magenta"):
    from .printutils import indah0

    indah0(message, warna=warna)
    yesno = input(" ")
    if yesno == "y" or yesno == "yes" or yesno == "Y":
        if yes_callback:
            yes_callback()
        return True

    return False


def list_set(myarr):
    """
    input: list
    output: list
    process:
    - unik-kan
    - balikkan lagi ke list
    """
    return list(set(myarr))


def datadir(filename=None):
    rootdir = env_get("ULIBPY_ROOTDIR")
    datadir_relative = env_get("ULIBPY_DATA_FOLDER")
    datafolder = os.path.join(rootdir, datadir_relative)
    if filename:
        return os.path.join(datafolder, filename)
    return datafolder


class TabCompleter:
    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
        if state == 0:  # on first trigger, build possible matches
            if text:  # cache matches (entries that start with entered text)
                self.matches = [s for s in self.options if s and s.startswith(text)]
            else:  # no text entered, all matches possible
                self.matches = self.options[:]

        # return match indexed by state
        try:
            return self.matches[state]
        except IndexError:
            return None


def complete(completer, read_history=False):
    readline.set_completer(completer.complete)
    readline.parse_and_bind("tab: complete")
    if read_history:
        try:
            readline.read_history_file()
        except FileNotFoundError as notfound:
            print(f"readline: Gagal baca history file {notfound}.")


def complete_from_list(keywords, read_history=False):
    """
    cara pake
    cmds = []
    complete_from_list(cmds)
    """
    complete(TabCompleter(keywords), read_history)


def input_until_end(ender="###", line_callback=None):
    """
    line_callback
            jk kita pengen bisa proses per line, misal utk exec sesuatu dan skip masukkan ke result
    """
    print(f"Enter line until {ender}.")
    result = []
    baris = input(">> ")
    while baris != ender:
        if line_callback:
            masukkan = line_callback(baris)
            if masukkan:
                result.append(baris)
                # jk return False, kita gak mau masukkan baris yg sdh diproses tsb.
        else:
            result.append(baris)

        baris = input(">> ")

    if baris:
        return "\n".join(result)

    return None


def perintah(cmd):
    """
    alt pake subprocess
    """
    if env_int("ULIBPY_FMUS_DEBUG") > 1:
        from .printutils import indah_debug

        indah_debug(f"perintah: {cmd}", warna="red")
    os.system(cmd)


def perintahsp(prefix, cmd):
    """
    alt pake subprocess
    https://linuxhint.com/execute_shell_python_subprocess_run_method/#:~:text=To%20capture%20the%20output%20of,named%20%E2%80%9Ccapture_output%3DTrue%E2%80%9D.&text=You%20can%20individually%20access%20stdout,stdout%E2%80%9D%20and%20%E2%80%9Coutput.
    output = subprocess.run(["cat", "data.txt"], capture_output=True)
    subprocess.run(["cat", "data.txt"])
    """
    output = subprocess.run(prefix.split() + [cmd], capture_output=True)
    return output


def perintahsp_simple(complete_command):
    subprocess.run(complete_command.split())


def perintahsp_simple_chdir(complete_command, workdir=None):
    from .dirutils import chdir, disini

    olddir = disini()
    if workdir:
        chdir(workdir)
        # print('perintahsp_simple_chdir mulai di:', disini())
    subprocess.run(complete_command.split(), shell=True)
    if workdir:
        chdir(olddir)
        # print('perintahsp_simple_chdir berarkhir di:', disini())


def perintahsp_capture(complete_command):
    output = subprocess.run(complete_command.split(), capture_output=True)
    return output


def perintahsp_outerr(complete_command):
    """
    gagal utk:
    curl http://localhost:8080/urls -X POST -H "Content-type: application/json" -d '{ "name": "usef" }'
    """
    output = subprocess.run(complete_command.split(), capture_output=True)
    _stdout = output.stdout.decode("utf8")
    _stderr = output.stderr.decode("utf8")
    return _stdout, _stderr


def perintah_shell(command):
    """
    juga perlu coba:
    subprocess.Popen(command, shell=True).wait()
    """
    if env_int("ULIBPY_FMUS_DEBUG") > 1:
        print(f"run shell: {command}.")
    subprocess.run(command, shell=True)


def perintah_shell_wait(command):
    """
    juga perlu coba:
    subprocess.Popen(command, shell=True).wait()
    juga ada
    communicate()
    """
    if env_int("ULIBPY_FMUS_DEBUG") > 1:
        print(f"run shell: {command}.")
    # subprocess.run(command, shell=True)
    subprocess.Popen(command, shell=True).wait()


def perintahsp_outerr_as_shell(complete_command):
    """
    berhasil utk:
    curl http://localhost:8080/urls -X POST -H "Content-type: application/json" -d '{ "name": "usef" }'
    """
    cmdlist = complete_command.split()
    # print(f'perintahsp_outerr_as_shell: asli [{complete_command}], listify {cmdlist}')
    output = subprocess.run(complete_command, capture_output=True, shell=True)
    _stdout = output.stdout.decode("utf8")
    _stderr = output.stderr.decode("utf8")
    # if _stdout is None:
    # 	'''
    # 	utk hindari
    # 	out, err = process_curl(program, True)
    # 	TypeError: cannot unpack non-iterable NoneType object
    # 	wkt _stdout = None
    # 	'''
    # 	_stdout = ''
    return _stdout, _stderr


def get_suffix_angka(text, cari="0123456789", pipa=None):
    """
    mystr[len(mystr.rstrip('0123456789')):]
    mystr[len(mystr.rstrip('|0123456789')):]

    a = get_suffix_angka(mystr)
    b = get_suffix_angka(mystr, '|')
    if b == '|'+a: berarti mystr diakhiri dengan |<angka>
    """
    if pipa:
        berpipa = pipa + cari
        bisa_berangka_dikiri = text[len(text.rstrip(berpipa)) :]
        return bisa_berangka_dikiri.lstrip(cari)
    else:
        return text[len(text.rstrip(cari)) :]


def python_package(pkg):
    # https://stackoverflow.com/questions/247770/how-to-retrieve-a-modules-path
    import importlib
    import inspect

    package = importlib.import_module(pkg)
    if package:
        lokasi_file = inspect.getfile(package)
        lokasi = os.path.dirname(lokasi_file)
        return lokasi

    return None


def replace_wiekes(result, wiekes):
    prefix = env_get("ULIBPY_WIEKES_TEMPLATE_PREFIX")
    capper = env_get("ULIBPY_WIEKES_CAPITALIZE_SYMBOL")
    wiekeplural = env_get("ULIBPY_WIEKES_PLURALIZE_SYMBOL")
    wiekelower = env_get("ULIBPY_WIEKES_LOWERIZE_SYMBOL")
    wiekeupper = env_get("ULIBPY_WIEKES_UPPERIZE_SYMBOL")
    replacers = wiekes
    templates = [prefix + str(angka).zfill(2) for angka in range(1, len(replacers) + 1)]
    for index, wieke in enumerate(replacers):
        result = result.replace(templates[index] + capper, wieke.capitalize())
        result = result.replace(templates[index] + wiekeplural, wieke + "s")
        result = result.replace(templates[index] + wiekelower, wieke.lower())
        result = result.replace(templates[index] + wiekeupper, wieke.upper())
        result = result.replace(templates[index], wieke)
    return result


def run_in_server(command):
    if env_exist("ULIBPY_SERVER_SSH"):
        from .printutils import indah0

        prefix = env_get("ULIBPY_SERVER_SSH")
        print("Ready to roll di server", prefix)
        output = perintahsp(prefix, command)
        _stdout = output.stdout.decode("utf8")
        _stderr = output.stderr.decode("utf8")
        if _stderr:
            indah0(_stderr, warna="red", bold=True, newline=True)
        indah0(_stdout, warna="cyan", bold=True, newline=True)
    else:
        print("Gak ada alamat server ULIBPY_SERVER_SSH di env")


def vscode_edit_file(filepath):
    cmd = f"code {filepath}"
    # print('cmd dg --goto line:', cmd)
    # Arguments in `--goto` mode should be in the format of `FILE(:LINE(:CHARACTER))`
    # perintahsp_simple(cmd)
    perintah(cmd)


def vscode_edit_at_line(filepath, lineno):
    if not lineno or lineno < 0:
        lineno = 0

    cmd = f'code --goto "{filepath}:{lineno}:1"'
    # print('cmd dg --goto line:', cmd)
    # Arguments in `--goto` mode should be in the format of `FILE(:LINE(:CHARACTER))`
    # perintahsp_simple(cmd)
    perintah(cmd)


def buka(alamat):
    webbrowser.open(alamat)


class Launcher:
    def __init__(self):
        pass

    @staticmethod
    def launch(key):
        if key in PROGRAMS:
            cmd = PROGRAMS[key]
            completecmd = cmd + " 2>/dev/null &"
            if platform() in ["win32", "windows"]:
                completecmd = cmd
            print(completecmd)
            os.system(completecmd)
        elif " " in key:
            from .stringutils import splitspace

            cmd, args = splitspace(key)
            # print(f'''
            # cmd		{cmd}
            # type c	{type(cmd)}
            # args	{args}
            # type a	{type(args)}
            # ''')
            if cmd == "o":
                """
                key = 		l 		o 		trans
                                cmd   args

                jk args punya , berarti ini trans
                jk args punya | berarti ini google search
                l o trans,en#sublime
                l o goog|christopher walken
                """
                __SOURCE = "en"
                __TARGET = "id"
                __TEXTPLACEHOLDER__ = ""
                if "|" in args:
                    # l o goog|...
                    goog, __placeholder = args.split("|")
                    __TEXTPLACEHOLDER__ = __placeholder.replace(" ", "+")
                    alamat = GOOGLESEARCH.replace(
                        "__TEXTPLACEHOLDER__", __TEXTPLACEHOLDER__
                    )
                    url = [alamat]
                elif "," in args and not args.startswith("http"):
                    """
                    l o trans,en
                    l o trans,en,id
                    perlu juga: kasih text
                    l o trans,en#sublime
                    """
                    if args.count(",") == 1:
                        """
                        jk cuma 1 language diberikan
                        dia jadi source atau target? source saja dulu
                        """
                        trans, __SOURCE = args.split(",")
                    elif args.count(",") == 2:
                        trans, __SOURCE, __TARGET = args.split(",")

                    if "#" in __SOURCE:
                        __SOURCE, __placeholder = __SOURCE.split("#")
                        __TEXTPLACEHOLDER__ = f"&text={__placeholder}"
                    alamat = (
                        TRANSLATE.replace("__SOURCE", __SOURCE)
                        .replace("__TARGET", __TARGET)
                        .replace("__TEXTPLACEHOLDER__", __TEXTPLACEHOLDER__)
                    )
                    url = [alamat]

                else:
                    url = [item for item in WEBSITES if args.lower() in item.lower()]
                    # jika l o alamat dan alamat tdk ada dlm WEBSITES
                    if not url:
                        url = [args]
                    else:
                        print("url:", url)

                if url:
                    if len(url) == 1:
                        buka(url[0])
                    else:
                        from .printutils import print_list_warna

                        print_list_warna(url)
                        return url
            elif cmd in PROGRAMS:
                cmd = PROGRAMS[cmd]
                args = env_expand(args, bongkarin=True)
                if cmd == "qterminal":
                    cmd = f"{cmd} -w "
                cmd = cmd + f' "{args}"'
                print(cmd)
                os.system(cmd + " 2>/dev/null &")


def half_backslash(filepath):
    return filepath.replace("\\\\", "\\")


def double_backslash(filepath):
    return filepath.replace("\\", "\\\\")


def quad_backslash(filepath):
    return double_backslash(double_backslash(filepath))


def wslify(filepath, rewindows=False, no_double_back=True, manual=False):
    """
	linux path -> wsl path
	windows path -> wsl path
		rewindows = true

	kita gunakan jk original filepath ada di linux

	manual jk env var kosong, maka prefix wsl$ kita kasih secara hardcoded
	rewindows = ubah / jadi \\
	no_double_back = double backslash diawal utk wsl diubah jadi single backslash
	manual = kasih \\wsl dst. di awal
	"""
    prefix = env_get("ULIBPY_WSL_ADDRESS")
    if manual:
        prefix = "\\\\wsl$\\Ubuntu-20.04"
    hasil = filepath
    if prefix:
        # return prefix + filepath.replace('/', os.sep)
        hasil = prefix + filepath
        if rewindows:
            hasil = prefix + filepath.replace("/", "\\")
        if no_double_back:
            hasil = hasil.replace("\\\\", "\\")
    return hasil


def linuxpath_to_wslpath(filepath, manual=False, untested_new_feature=False):
    """
    jadi aneh utk W=*outlay gagal
    maka buatkan untested_new_feature False secara default
    """
    prefix = env_get("ULIBPY_WSL_ADDRESS")
    if manual:
        prefix = "\\\\wsl$\\Ubuntu-20.04"
    hasil = filepath
    if prefix:
        hasil = prefix + double_backslash(filepath.replace("/", "\\"))
        if untested_new_feature:
            hasil = double_backslash(hasil)  # krn backslash dimakan shell...
    return hasil


def wslpath_to_linuxpath(filepath):
    """
    pathsource bisa windows (/mnt/c/...) atau linux (/home/usef/...)
    kita sebut pathsource: linuxsource dan windowssource
    """
    prefix = env_get("ULIBPY_WSL_ADDRESS")
    halfback_prefix = half_backslash(prefix)
    if filepath.startswith(prefix):
        # [\\wsl$\Ubuntu-20.04\home\usef\work\ulibs\schnell\app\transpiler\frontend\fslang\misc\work.fmus
        filepath = filepath.removeprefix(prefix).replace("\\", "/")
        if filepath.startswith("/mnt/c"):
            # ini kita masih dlm linux, jadi dont send windows path
            # kembalikan c:/path/to/target bukan c:\path\to\target
            # return filepath.replace('/mnt/c/', 'c:/')
            return filepath
        elif filepath.startswith("c:\\"):
            # buka code di windows path
            # c:\work\oprek\cmake-qt\ecommdj\fshelp\work
            return linuxify(filepath)
        else:
            return filepath
    elif filepath.startswith(halfback_prefix):
        print(f"wslpath_to_linuxpath diawali: {halfback_prefix}")
        filepath = filepath.removeprefix(halfback_prefix).replace("\\", "/")
        print(f"wslpath_to_linuxpath menjadi: {filepath}")
        return filepath
    elif filepath.startswith("c:\\"):
        # buka code di windows path
        # c:\work\oprek\cmake-qt\ecommdj\fshelp\work
        return linuxify(filepath)
    return filepath


def linuxify(filepath):
    """
    kita gunakan jk original filepath ada di windows (c:\...)

    c:\tmp -> /mnt/c/tmp
    """
    lower_drive = filepath[0].lower() + filepath[1:]
    res = lower_drive.replace("c:\\", "/mnt/c/")
    res = res.replace("c:/", "/mnt/c/")
    res = res.replace("\\", "/")
    return res


def is_windows():
    # return not platform() == 'linux'
    return platform() in ["win32", "windows", "desktop"]


def windowsify(filepath):
    return filepath.replace("/", "\\")


def is_the_same_folder(filepath1, filepath2):
    return windowsify(filepath1.lower()) == windowsify(filepath2.lower())


def not_the_same_folder(filepath1, filepath2):
    return windowsify(filepath1.lower()) != windowsify(filepath2.lower())


def salin_objek(sumber):
    import copy

    return copy.copy(sumber)


def wslpath2winpath(filepath):
    # /mnt/c/fullstack/django_pg/kt.us
    if filepath.startswith("/mnt/c/"):
        return filepath.replace("/mnt/c/", "c:/")
    return filepath


def wslpath2winpath_condition(filepath):
    """
    filepath = wslpath2winpath_condition(filepath)
    """
    # print('wslpath:', filepath)
    if platform() == "wsl":
        if filepath.startswith("/mnt/c/"):
            return filepath.replace("/mnt/c/", "c:/")
        else:
            # /home/usef ... etc
            return linuxpath_to_wslpath(filepath, untested_new_feature=False)
    return filepath


def winpath_to_wslpath(filepath):
    return filepath.replace("\\", "/")


def import_module_original(dotted_filepath, redot=False):
    """
    import_module_original('a/b/c/d', redot=True)
    import_module_original('a.b.c.d')
    """
    # from importlib import import_module
    if redot:
        dotted_filepath = dotted_filepath.replace("/", ".")
    module = std_import_module(dotted_filepath)
    return module


def import_module(MODULE_NAME, MODULE_PATH):
    """
        'generator': '/home/usef/work/ulibs/schnell/app/transpiler/frontend/fslang/z/quick/campur/wp5/wd4/__init__.py',
        'fmusfile': '/home/usef/work/ulibs/schnell/app/transpiler/frontend/fslang/z/quick/campur/wp5/wd4/index-input.mk'

        spec_from_file_location(name,
                                location=None,
                                                        *, <- sering lihat gini, ini artinya positional args kan ya...
                                                        loader=None,
                            submodule_search_locations=_POPULATE)
        Return a module spec based on a file location.

    To indicate that the module is a package, set
    submodule_search_locations to a list of directory paths.
        An empty list is sufficient, though its not otherwise useful to the import system.

    The loader must take a spec as its only __init__() arg.
    """
    # https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
    # MODULE_PATH = "/path/to/your/module/__init__.py"
    # MODULE_NAME = "mymodule"
    import importlib
    import sys

    spec = importlib.util.spec_from_file_location(MODULE_NAME, MODULE_PATH)

    if not spec:
        from .dirutils import ayah

        print("[app.utils] respeccing...")
        submodule_search_locations = ayah(MODULE_PATH, 1)
        spec = importlib.util.spec_from_file_location(
            MODULE_NAME,
            MODULE_PATH,
            submodule_search_locations=(submodule_search_locations,),
        )
        if not spec:
            from importlib._bootstrap_external import \
                _get_supported_file_loaders

            a = _get_supported_file_loaders()
            print("[app.utils] double respeccing...")
            print(a)

    # print(f'''[utils/import_module]
    # MODULE_NAME	= {MODULE_NAME}
    # MODULE_PATH	= {MODULE_PATH}
    # spec = {spec}
    # ''')

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def micro(filepath=None):
    from .dirutils import bongkar, joiner
    from .envvalues import schnelldir

    microdir = joiner(schnelldir(), "vendor/micro/micro")
    if is_windows:
        microdir = linuxify(microdir)  # c:/ jadi /mnt/c
        if not filepath:
            perintah_shell(f"wsl {microdir}")
        else:
            """
            biasanya dari ULIBPY_BASEDIR/data/oprek.py dll
            """
            filepath = bongkar(filepath)
            filepath = linuxify(filepath)
            perintah_shell(f"wsl {microdir} {filepath}")
