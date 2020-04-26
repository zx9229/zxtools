import struct
import codecs
import datetime
import decimal
import json
import os
import argparse


def json_dumps(src):
    def json_handler(obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S.%f")
        if isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        if isinstance(obj, bytes):
            return obj.__repr__()
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        raise TypeError(obj.__repr__() + " is not JSON serializable")

    return json.dumps(src, sort_keys=True, indent=2, default=json_handler)


# 通达信各周期数据格式（day、lc5、lc1）详解
# http://www.sigmagu.com/paper/7
# 通达信5分钟线数据格式解析
# https://bbs.csdn.net/topics/392327877
# 通达信日线 数据格式
# https://www.cnblogs.com/zeroone/archive/2013/07/10/3181251.html
# Python中struct.pack()和struct.unpack()用法详细说明
# https://blog.csdn.net/weiwangchao_/article/details/80395941


def bytes_to_char(src, do_check=True):
    if do_check:
        assert type(src) == bytes and len(src) == 1
    return struct.unpack("c", src)


def bytes_to_short(src, do_check=True):
    if do_check:
        assert type(src) == bytes and len(src) == 2
    return struct.unpack("h", src)


def bytes_to_int(src, do_check=True):
    if do_check:
        assert type(src) == bytes and len(src) == 4
    return struct.unpack("i", src)


def bytes_to_float(src, do_check=True):
    if do_check:
        assert type(src) == bytes and len(src) == 4
    return struct.unpack("f", src)


def bytes_to_double(src, do_check=True):
    if do_check:
        assert type(src) == bytes and len(src) == 8
    return struct.unpack("d", src)


def bytes_to_longlong(src, do_check=True):
    if do_check:
        assert type(src) == bytes and len(src) == 8
    return struct.unpack("q", src)


class line_data_lc(object):
    def __init__(self, content=None, *args, **kwargs):
        if content is not None:
            self.set_data(content)

    @property
    def dict(self):
        return self._to_dict()

    @property
    def datetime(self):
        return line_data_lc._calc_datetime(self._date, self._time)

    @property
    def date(self):
        return line_data_lc._calc_date(self._date)

    @property
    def time(self):
        return line_data_lc._calc_time(self._time)

    def set_data(self, content):
        assert type(content) == bytes and len(content) == 32
        self._date = content[0:2]
        self._time = content[2:4]
        self._open = content[4:8]
        self._high = content[8:12]
        self._low = content[12:16]
        self._close = content[16:20]
        self._oi = content[20:24]
        self._volume = content[24:28]
        self._reserved = content[28:32]
        self._date = bytes_to_short(self._date, False)[0]
        self._time = bytes_to_short(self._time, False)[0]
        self._open = bytes_to_float(self._open, False)[0]
        self._high = bytes_to_float(self._high, False)[0]
        self._low = bytes_to_float(self._low, False)[0]
        self._close = bytes_to_float(self._close, False)[0]
        self._oi = bytes_to_int(self._oi, False)[0]
        self._volume = bytes_to_int(self._volume, False)[0]
        self._reserved = bytes_to_int(self._reserved, False)[0]
        self._open = round(decimal.Decimal(self._open), 4)
        self._high = round(decimal.Decimal(self._high), 4)
        self._low = round(decimal.Decimal(self._low), 4)
        self._close = round(decimal.Decimal(self._close), 4)

    @staticmethod
    def _calc_date(d):
        year = d // 2048 + 2004
        month = d % 2048 // 100
        day = d % 2048 % 100
        return year * 10000 + month * 100 + day

    @staticmethod
    def _calc_time(t):
        hour = t // 60
        minute = t % 60
        return hour * 100 + minute

    @staticmethod
    def _calc_datetime(d, t):
        year = d // 2048 + 2004
        month = d % 2048 // 100
        day = d % 2048 % 100
        hour = t // 60
        minute = t % 60
        return datetime.datetime(year, month, day, hour, minute)

    def _to_dict(self):
        d = {
            "datetime": self.datetime,
            "open": self._open,
            "high": self._high,
            "low": self._low,
            "close": self._close,
            "volume": self._volume,
            "oi": self._oi,
            "reserved": self._reserved
        }
        return d

    def __str__1(self):
        return '{datetime}, {open}, {high}, {low}, {close}, {volume}, {oi}, {reserved}'.format(
            datetime=self.datetime.strftime('%Y-%m-%d %H:%M:%S'),
            open=self._open,
            high=self._high,
            low=self._low,
            close=self._close,
            volume=self._volume,
            oi=self._oi,
            reserved='{:08X}'.format(self._reserved))

    def __str__2(self):
        def json_handler(obj):
            if isinstance(obj, datetime.datetime):
                return obj.strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(obj, datetime.date):
                return obj.strftime("%Y-%m-%d")
            if isinstance(obj, bytes):
                return obj.__repr__()
            if isinstance(obj, decimal.Decimal):
                return float(obj)
            raise TypeError(obj.__repr__() + " is not JSON serializable")

        return json.dumps(
            self._to_dict(), sort_keys=True, indent=2, default=json_handler)

    def __str__(self):
        return json_dumps(self.dict)


class line_data_day(object):
    def __init__(self, content=None, *args, **kwargs):
        if content is not None:
            self.set_data(content)

    @property
    def dict(self):
        return self._to_dict()

    @property
    def datetime(self):
        return line_data_day._calc_datetime(self._date)

    @property
    def date(self):
        return self._date

    def set_data(self, content):
        assert type(content) == bytes and len(content) == 32
        self._date = content[0:4]
        self._open = content[4:8]
        self._high = content[8:12]
        self._low = content[12:16]
        self._close = content[16:20]
        self._oi = content[20:24]
        self._volume = content[24:28]
        self._settle = content[28:32]
        self._date = bytes_to_int(self._date, False)[0]
        self._open = bytes_to_float(self._open, False)[0]
        self._high = bytes_to_float(self._high, False)[0]
        self._low = bytes_to_float(self._low, False)[0]
        self._close = bytes_to_float(self._close, False)[0]
        self._oi = bytes_to_int(self._oi, False)[0]
        self._volume = bytes_to_int(self._volume, False)[0]
        self._settle = bytes_to_float(self._settle, False)[0]
        self._open = round(decimal.Decimal(self._open), 4)
        self._high = round(decimal.Decimal(self._high), 4)
        self._low = round(decimal.Decimal(self._low), 4)
        self._close = round(decimal.Decimal(self._close), 4)
        self._settle = round(decimal.Decimal(self._settle), 4)

    @staticmethod
    def _calc_datetime(d):
        year = d // 10000
        month = d % 10000 // 100
        day = d % 100
        return datetime.datetime(year, month, day)

    def _to_dict(self):
        d = {
            "datetime": self.datetime,
            "open": self._open,
            "high": self._high,
            "low": self._low,
            "close": self._close,
            "volume": self._volume,
            "oi": self._oi,
            "settle": self._settle
        }
        return d

    def __str__1(self):
        return '{datetime}, {open}, {high}, {low}, {close}, {volume}, {oi}, {settle}'.format(
            datetime=self.datetime.strftime('%Y-%m-%d'),
            open=self._open,
            high=self._high,
            low=self._low,
            close=self._close,
            volume=self._volume,
            oi=self._oi,
            settle=self._settle)

    def __str__2(self):
        def json_handler(obj):
            if isinstance(obj, datetime.datetime):
                return obj.strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(obj, datetime.date):
                return obj.strftime("%Y-%m-%d")
            if isinstance(obj, bytes):
                return obj.__repr__()
            if isinstance(obj, decimal.Decimal):
                return float(obj)
            raise TypeError(obj.__repr__() + " is not JSON serializable")

        return json.dumps(
            self._to_dict(), sort_keys=True, indent=2, default=json_handler)

    def __str__(self):
        return json_dumps(self.dict)


def loadFile(filename, isDay):
    dst = []
    line_data = line_data_day() if isDay else line_data_lc()
    with codecs.open(filename, 'rb') as f:
        content = f.read()
    assert len(content) % 32 == 0
    for idx in range(0, len(content) // 32, 1):
        line_data.set_data(content[idx * 32:(idx + 1) * 32])
        dst.append(line_data.dict)
    return dst


if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument('-f', '--file', type=str)
    args = parse.parse_args()
    if args.file is None:
        filepath = r"C:/new_tdxqh/vipdoc/ds/lday/30#AUL8.day"  # 黄金主连.
        filepath = r"C:/new_tdxqh/vipdoc/ds/minline/30#AUL8.lc1"  # 黄金主连.
    else:
        filepath = args.file
    ext = os.path.splitext(filepath)[1]
    if ext in ('.lc1', '.lc5'):
        line_data = line_data_lc()
    elif ext in ('.day'):
        line_data = line_data_day()
    else:
        raise Exception('unknown file filename extension.')

    with codecs.open(filepath, 'rb') as f:
        content = f.read()
    assert len(content) % 32 == 0

    for idx in range(0, len(content) // 32, 1):
        line_data.set_data(content[idx * 32:(idx + 1) * 32])
        print(line_data)

    print('DONE.')
