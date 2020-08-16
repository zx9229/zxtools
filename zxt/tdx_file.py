import argparse
import datetime
import decimal
import json
import os
import struct


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


class BaseWrap(object):
    '''Base Wrapper'''

    def __init__(self, *args, **kwargs):
        pass

    @property
    def value(self):
        return self.call()

    def call(self):
        raise NotImplementedError('not_implemented_error')


class PlainWrap(BaseWrap):
    '''Plain Wrapper'''

    def __init__(self, value, *args, **kwargs):
        super(PlainWrap, self).__init__(value, *args, **kwargs)
        self._value = value

    def call(self):
        return self._value


class ObjWrap(BaseWrap):
    '''Object Wrapper'''

    def __init__(self, obj, name: str, *args, **kwargs):
        super(ObjWrap, self).__init__(obj, name, *args, **kwargs)
        self._obj = obj
        self._name = name

    def call(self):
        return getattr(self._obj, self._name)


class field_resolver(object):
    def __init__(self, name: str, bintype: str, begindx: int, endindx: int, check: bool = True, ndigits: int = None, *args, **kwargs):  # yapf: disable
        self._name = name
        self._value = None
        self._bintype = bintype
        self._begindx = begindx
        self._endindx = endindx
        self._check = check
        self._ndigits = ndigits

    def calc(self, content: bytes):
        src = content[self._begindx:self._endindx + 1]
        if False:
            pass
        elif self._bintype == 'bytes':
            self._value = field_resolver.bytes_to_bytes(src, self._check)[0]
        elif self._bintype == 'char':
            self._value = field_resolver.bytes_to_char(src, self._check)[0]
        elif self._bintype == 'short':
            self._value = field_resolver.bytes_to_short(src, self._check)[0]
        elif self._bintype == 'unsignedshort':
            self._value = field_resolver.bytes_to_unsignedshort(src, self._check)[0]  # yapf: disable
        elif self._bintype == 'int':
            self._value = field_resolver.bytes_to_int(src, self._check)[0]
        elif self._bintype == 'longlong':
            self._value = field_resolver.bytes_to_longlong(src, self._check)[0]
        elif self._bintype == 'float':
            self._value = field_resolver.bytes_to_float(src, self._check)[0]
            if self._ndigits is not None:
                self._value = round(decimal.Decimal(self._value), self._ndigits)  # yapf: disable
        elif self._bintype == 'double':
            self._value = field_resolver.bytes_to_double(src, self._check)[0]
            if self._ndigits is not None:
                self._value = round(decimal.Decimal(self._value), self._ndigits)  # yapf: disable
        else:
            raise Exception('unknown bintype={}'.format(self._bintype))

    @staticmethod
    def bytes_to_bytes(src, check=True):
        if check:
            assert type(src) == bytes
        return (src, )

    @staticmethod
    def bytes_to_char(src, check=True):
        if check:
            assert type(src) == bytes and len(src) == 1
        return struct.unpack("c", src)

    @staticmethod
    def bytes_to_short(src, check=True):
        if check:
            assert type(src) == bytes and len(src) == 2
        return struct.unpack("h", src)

    @staticmethod
    def bytes_to_unsignedshort(src, check=True):
        if check:
            assert type(src) == bytes and len(src) == 2
        return struct.unpack("H", src)

    @staticmethod
    def bytes_to_int(src, check=True):
        if check:
            assert type(src) == bytes and len(src) == 4
        return struct.unpack("i", src)

    @staticmethod
    def bytes_to_longlong(src, check=True):
        if check:
            assert type(src) == bytes and len(src) == 8
        return struct.unpack("q", src)

    @staticmethod
    def bytes_to_float(src, check=True):
        if check:
            assert type(src) == bytes and len(src) == 4
        return struct.unpack("f", src)

    @staticmethod
    def bytes_to_double(src, check=True):
        if check:
            assert type(src) == bytes and len(src) == 8
        return struct.unpack("d", src)


class field_conv(object):
    def __init__(self, name: str, func, *args, **kwargs):
        self._name = name
        self._value = None
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def calc(self):
        self._value = self._func(*self._args, **self._kwargs)

    @staticmethod
    def shrink_int_to_float(arg1, arg2, *args, **kwargs):
        src = arg1.value  # int
        multiple = arg2.value  # int
        return src / multiple

    @staticmethod
    def tdx_field_to_yyyymmdd(arg1, *args, **kwargs):
        d = arg1.value  # int
        year = d // 2048 + 2004
        month = d % 2048 // 100
        day = d % 2048 % 100
        return year * 10000 + month * 100 + day

    @staticmethod
    def tdx_field_to_hhmm(arg1, *args, **kwargs):
        t = arg1.value  # int
        hour = t // 60
        minute = t % 60
        return hour * 100 + minute

    @staticmethod
    def tdx_field_to_datetime(arg1, arg2, *args, **kwargs):
        d = arg1.value  # int
        t = arg2.value  # int
        year = d // 2048 + 2004
        month = d % 2048 // 100
        day = d % 2048 % 100
        hour = t // 60
        minute = t % 60
        return datetime.datetime(year, month, day, hour, minute)

    @staticmethod
    def yyyymmdd_to_datetime(arg1, *args, **kwargs):
        d = arg1.value  # int
        year = d // 10000
        month = d % 10000 // 100
        day = d % 100
        return datetime.datetime(year, month, day)

    @staticmethod
    def yyyymmdd_to_date(arg1, *args, **kwargs):
        d = arg1.value  # int
        year = d // 10000
        month = d % 10000 // 100
        day = d % 100
        return datetime.date(year, month, day)


class line_data_lc(object):
    def __init__(self, content: bytes = None, *args, **kwargs):
        self._r_list = [
            field_resolver('_r_date', 'unsignedshort', 0, 1),
            field_resolver('_r_time', 'short', 2, 3),
            field_resolver('_r_open', 'float', 4, 7, ndigits=4),
            field_resolver('_r_high', 'float', 8, 11, ndigits=4),
            field_resolver('_r_low', 'float', 12, 15, ndigits=4),
            field_resolver('_r_close', 'float', 16, 19, ndigits=4),
            field_resolver('_r_amount', 'float', 20, 23, ndigits=4),
            field_resolver('_r_volume', 'int', 24, 27),
            field_resolver('_r_reserved', 'float', 28, 31, ndigits=4)
        ]
        self._c_list = [
            field_conv('_c_datetime', field_conv.tdx_field_to_datetime, arg1=ObjWrap(self, '_r_date'), arg2=ObjWrap(self, '_r_time'))
        ]  # yapf: disable
        if content is not None:
            self.set_data(content)

    @property
    def dict(self):
        return self._to_dict()

    def set_data(self, content: bytes):
        assert type(content) == bytes and len(content) == 32
        for item in self._r_list:
            item.calc(content)
            setattr(self, item._name, item._value)
        for item in self._c_list:
            item.calc()
            setattr(self, item._name, item._value)

    def _to_dict(self):
        d = {
            "datetime": self._c_datetime,
            "open": self._r_open,
            "high": self._r_high,
            "low": self._r_low,
            "close": self._r_close,
            "amount": self._r_amount,
            "volume": self._r_volume,
            "reserved": self._r_reserved
        }
        return d

    def __str__(self):
        return json_dumps(self.dict)


class line_data_lc_qh(object):
    '''分钟线,期货,比如通达信的(IFL8)(沪深主连)'''
    def __init__(self, content: bytes = None, *args, **kwargs):
        self._r_list = [
            field_resolver('_r_date', 'unsignedshort', 0, 1),
            field_resolver('_r_time', 'short', 2, 3),
            field_resolver('_r_open', 'float', 4, 7, ndigits=4),
            field_resolver('_r_high', 'float', 8, 11, ndigits=4),
            field_resolver('_r_low', 'float', 12, 15, ndigits=4),
            field_resolver('_r_close', 'float', 16, 19, ndigits=4),
            field_resolver('_r_oi', 'int', 20, 23),
            field_resolver('_r_volume', 'int', 24, 27),
            field_resolver('_r_reserved', 'float', 28, 31, ndigits=4)
        ]
        self._c_list = [
            field_conv('_c_datetime', field_conv.tdx_field_to_datetime, arg1=ObjWrap(self, '_r_date'), arg2=ObjWrap(self, '_r_time'))
        ]  # yapf: disable
        if content is not None:
            self.set_data(content)

    @property
    def dict(self):
        return self._to_dict()

    def set_data(self, content: bytes):
        assert type(content) == bytes and len(content) == 32
        for item in self._r_list:
            item.calc(content)
            setattr(self, item._name, item._value)
        for item in self._c_list:
            item.calc()
            setattr(self, item._name, item._value)

    def _to_dict(self):
        d = {
            "datetime": self._c_datetime,
            "open": self._r_open,
            "high": self._r_high,
            "low": self._r_low,
            "close": self._r_close,
            "io": self._r_oi,
            "volume": self._r_volume,
            "reserved": self._r_reserved
        }
        return d

    def __str__(self):
        return json_dumps(self.dict)


class line_data_day_stock(object):
    '''日线,股票'''

    def __init__(self, content: bytes = None, *args, **kwargs):
        self._r_list = [
            field_resolver('_r_date', 'int', 0, 3),
            field_resolver('_r_open', 'int', 4, 7, ndigits=4),
            field_resolver('_r_high', 'int', 8, 11, ndigits=4),
            field_resolver('_r_low', 'int', 12, 15, ndigits=4),
            field_resolver('_r_close', 'int', 16, 19, ndigits=4),
            field_resolver('_r_amount', 'float', 20, 23, ndigits=4),
            field_resolver('_r_volume', 'int', 24, 27),
            field_resolver('_r_lclose', 'int', 28, 31)
        ]
        self._c_list = [
            field_conv('_c_datetime', field_conv.yyyymmdd_to_datetime, arg1=ObjWrap(self, '_r_date')),
            field_conv('_c_open', field_conv.shrink_int_to_float, arg1=ObjWrap(self, '_r_open'), arg2=PlainWrap(100)),
            field_conv('_c_high', field_conv.shrink_int_to_float, arg1=ObjWrap(self, '_r_high'), arg2=PlainWrap(100)),
            field_conv('_c_low', field_conv.shrink_int_to_float, arg1=ObjWrap(self, '_r_low'), arg2=PlainWrap(100)),
            field_conv('_c_close', field_conv.shrink_int_to_float, arg1=ObjWrap(self, '_r_close'), arg2=PlainWrap(100)),
            field_conv('_c_lclose', field_conv.shrink_int_to_float, arg1=ObjWrap(self, '_r_lclose'), arg2=PlainWrap(100))
        ]  # yapf: disable
        if content is not None:
            self.set_data(content)

    @property
    def dict(self):
        return self._to_dict()

    def set_data(self, content: bytes):
        assert type(content) == bytes and len(content) == 32
        for item in self._r_list:
            item.calc(content)
            setattr(self, item._name, item._value)
        for item in self._c_list:
            item.calc()
            setattr(self, item._name, item._value)

    def _to_dict(self):
        d = {
            "datetime": self._c_datetime,
            "open": self._c_open,
            "high": self._c_high,
            "low": self._c_low,
            "close": self._c_close,
            "amount": self._r_amount,
            "volume": self._r_volume,
            "lclose": self._c_lclose
        }
        return d

    def __str__(self):
        return json_dumps(self.dict)


class line_data_day_fund(object):
    '''日线,基金'''

    def __init__(self, content: bytes = None, *args, **kwargs):
        self._r_list = [
            field_resolver('_r_date', 'int', 0, 3),
            field_resolver('_r_open', 'int', 4, 7, ndigits=4),
            field_resolver('_r_high', 'int', 8, 11, ndigits=4),
            field_resolver('_r_low', 'int', 12, 15, ndigits=4),
            field_resolver('_r_close', 'int', 16, 19, ndigits=4),
            field_resolver('_r_amount', 'float', 20, 23, ndigits=4),
            field_resolver('_r_volume', 'int', 24, 27),
            field_resolver('_r_lclose', 'int', 28, 31)
        ]
        self._c_list = [
            field_conv('_c_datetime', field_conv.yyyymmdd_to_datetime, arg1=ObjWrap(self, '_r_date')),
            field_conv('_c_open', field_conv.shrink_int_to_float, arg1=ObjWrap(self, '_r_open'), arg2=PlainWrap(1000)),
            field_conv('_c_high', field_conv.shrink_int_to_float, arg1=ObjWrap(self, '_r_high'), arg2=PlainWrap(1000)),
            field_conv('_c_low', field_conv.shrink_int_to_float, arg1=ObjWrap(self, '_r_low'), arg2=PlainWrap(1000)),
            field_conv('_c_close', field_conv.shrink_int_to_float, arg1=ObjWrap(self, '_r_close'), arg2=PlainWrap(1000)),
            field_conv('_c_lclose', field_conv.shrink_int_to_float, arg1=ObjWrap(self, '_r_lclose'), arg2=PlainWrap(1000))
        ]  # yapf: disable
        if content is not None:
            self.set_data(content)

    @property
    def dict(self):
        return self._to_dict()

    def set_data(self, content: bytes):
        assert type(content) == bytes and len(content) == 32
        for item in self._r_list:
            item.calc(content)
            setattr(self, item._name, item._value)
        for item in self._c_list:
            item.calc()
            setattr(self, item._name, item._value)

    def _to_dict(self):
        d = {
            "datetime": self._c_datetime,
            "open": self._c_open,
            "high": self._c_high,
            "low": self._c_low,
            "close": self._c_close,
            "amount": self._r_amount,
            "volume": self._r_volume,
            "lclose": self._c_lclose
        }
        return d

    def __str__(self):
        return json_dumps(self.dict)


def guess_resolver(filepath: str = None, resolver_name: str = None):
    resolver_object = None
    if resolver_name is not None:
        resolver_object = eval('{name}()'.format(name=resolver_name))
    else:
        basename = os.path.split(filepath)[1]
        name, ext = os.path.splitext(basename.lower())
        if ext in ('.lc1', '.lc5'):
            resolver_object = line_data_lc()
        elif ext in ('.day'):
            if name.startswith('sh6'):
                resolver_object = line_data_day_stock()
            elif name.startswith('sh5'):
                resolver_object = line_data_day_fund()
            elif name.startswith('sh0'):
                resolver_object = line_data_day_stock()
            else:
                raise ValueError('invalid filepath name={}'.format(name))
        else:
            raise ValueError('invalid filepath ext={}'.format(ext))
    return resolver_object


if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument('-f', '--file', type=str)
    parse.add_argument('-r', '--resolver', type=str)
    args = parse.parse_args()

    resolver_name = args.resolver
    filepath = args.file
    if filepath is None:
        filepath = r"C:/new_tdxqh/vipdoc/ds/lday/30#AUL8.day"  # 黄金主连.
        filepath = r"C:/new_tdxqh/vipdoc/ds/minline/30#AUL8.lc1"  # 黄金主连.
        filepath = r"C:/new_tdx/vipdoc/ds/minline/7#IO6T04V1.lc1"
        filepath = r"C:/new_tdx/vipdoc/sh/lday/sh688001.day"
        filepath = r"C:/new_tdx/vipdoc/sh/lday/sh510300.day"
        filepath = r"C:/new_tdx/vipdoc/sh/lday/sh000300.day"

    line_data = guess_resolver(filepath, resolver_name)

    with open(filepath, 'rb') as f:
        all_content = f.read()
    assert len(all_content) % 32 == 0

    for idx in range(0, len(all_content) // 32, 1):
        line_data.set_data(all_content[idx * 32:(idx + 1) * 32])
        print(line_data)

    print('DONE,', filepath)
