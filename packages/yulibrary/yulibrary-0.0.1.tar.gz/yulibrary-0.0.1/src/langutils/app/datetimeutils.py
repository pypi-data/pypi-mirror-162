import datetime
import time
from datetime import datetime as DT
from datetime import timedelta


month2 = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

month3 = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def iso():
    return datetime.datetime.now().isoformat()


def isofied():
    from .stringutils import replace_non_alpha

    return replace_non_alpha(datetime.datetime.now().isoformat())


def sekarang():
    return datetime.datetime.now()


def today():
    return datetime.datetime.today()


def today_ymd():
    """
    1978-08-24
    """
    return datetime.datetime.today().strftime("%Y-%m-%d")


def today_ydm():
    """
    1978-24-08
    """
    return datetime.datetime.today().strftime("%Y-%d-%m")


def today_mdy():
    """
    08-24-1978
    """
    return datetime.datetime.today().strftime("%m-%d-%Y")


def today_dmy():
    """
    24-08-1978
    """
    return datetime.datetime.today().strftime("%d-%m-%Y")


def waktu_hms():
    return datetime.datetime.today().strftime("%H:%M:%S")


def jam_hms():
    return datetime.datetime.today().strftime("%H:%M:%S")


def jam_hm():
    return datetime.datetime.today().strftime("%H:%M")


def sejam(mulai):
    """
    sejam = sudah_sejam (sejak mulai)
    """
    return sekarang() >= mulai + timedelta(hours=1)


def sehari(mulai):
    """
    mencek jika sehari sudah berlalu terhadap rujukan "mulai"
    sehari = sudah_sehari (sejak mulai)
    """
    return sekarang() >= mulai + timedelta(hours=24)


def beda_shm(s=1, m=0, h=0):
    """
    kembalikan datetime dg jarak h:m:s dari sekarang
    beda_shm() = 1 detik dari now
    """
    return sekarang() + timedelta(hours=h, minutes=m, seconds=s)


def epoch():
    """
    returns: float
    """
    epoch_time = int(time.time())
    return epoch_time


def epoch_diff(start, end):
    """
    returns: float
    """
    return end - start


def int_len(myint):
    return len(str(abs(myint)))


def is_epoch_ms(epoch):
    """
    is ms?
    seconds atau ms
    """
    if int_len(epoch) == 13:
        return True
    return False


def fmt(dt, format=None):
    if not format:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt.strftime(format)


def epoch2dt(epoch, utc=True):
    """
    coba cek:
    https://stackoverflow.com/questions/12400256/converting-epoch-time-into-the-datetime
    """
    if is_epoch_ms(epoch):
        epoch = epoch / 1000
    if utc:
        return datetime.datetime.utcfromtimestamp(epoch)
    return datetime.datetime.fromtimestamp(epoch)


def epoch2dtstr(epoch, utc=True, format=None):
    """
    2021-08-18 12:12:52
    current = epoch()
    epoch2dtstr(current)
    """
    dt = epoch2dt(epoch, utc=utc)
    return fmt(dt, format=format)


def format_epoch_longer(epoch, utc=False):
    """
    %A Monday
    %a monday
    """
    # return fmt_epoch('%A, %-m %B %Y, %-H:%M:%S', utc)
    format = "%A, %d %B %Y, %H:%M:%S"
    return fmt(epoch2dt(epoch, utc), format)


def year():
    return DT.now().year


def waktu(mode="year"):
    """
    https://stackoverflow.com/questions/28189442/datetime-current-year-and-month-in-python
    """
    if mode == "year":
        return DT.now().year
    elif mode == "month":
        return DT.now().month
    elif mode == "day":
        return DT.now().day
    elif mode == "hour":
        return DT.now().hour
    elif mode == "minute":
        return DT.now().minute
    elif mode == "second":
        return DT.now().second


def timestamp_for_file():
    tanggal = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S, %A")
    baris = f"[{tanggal}]"
    return baris
