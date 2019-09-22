import datetime
import urllib
import urllib.request


def src2dst(src):
    '''
    一个简单的打印函数
    '''

    def d2s(data: dict):
        lst = sorted(data.items(), key=lambda d: d[0])
        lst = ['"{}" : "{}"'.format(item[0], item[1]) for item in lst]
        data = '{\n' + '\n'.join(lst) + '\n}'
        return data

    if type(src) in (tuple, list):
        dst = ',\n'.join([d2s(item) for item in src])
    else:
        dst = d2s(src)
    return dst


def real(code_list):
    '''
    获取实时行情
    https://blog.csdn.net/u012041523/article/details/71107788
    '''

    def toReal(s):
        # return decimal.Decimal(s) if s else None
        return float(s) if s else None

    def toDateTime(d, t):
        if d and t:
            return datetime.datetime.strptime(d + ' ' + t, '%Y-%m-%d %H:%M:%S')
        else:
            return None

    head = [
        'code', 'name', 'open', 'lclose', 'last', 'high', 'low', 'bidpx',
        'askpx', 'volume', 'turnover', 'bv1', 'bp1', 'bv2', 'bp2', 'bv3',
        'bp3', 'bv4', 'bp4', 'bv5', 'bp5', 'av1', 'ap1', 'av2', 'ap2', 'av3',
        'ap3', 'av4', 'ap4', 'av5', 'ap5', 'date', 'time'
    ]
    if type(code_list) in (tuple, list):
        code_list = ','.join(code_list)
    url = 'http://hq.sinajs.cn/list={codeList}'.format(codeList=code_list)
    content = urllib.request.urlopen(url).read().decode('GB18030')
    lines = [line.strip() for line in content.split(';') if line.strip()]
    lines = [
        line.split('"')[0].replace('var hq_str_', '').replace('=', '') + ',' +
        line.split('"')[1] for line in lines
    ]
    data_list = [dict(zip(head, line.split(','))) for line in lines]
    for data in data_list:
        # code
        # name
        data['open'] = toReal(data.get('open'))
        data['lclose'] = toReal(data.get('lclose'))
        data['last'] = toReal(data.get('last'))
        data['high'] = toReal(data.get('high'))
        data['low'] = toReal(data.get('low'))
        data['bidpx'] = toReal(data.get('bidpx'))
        data['askpx'] = toReal(data.get('askpx'))
        data['volume'] = toReal(data.get('volume'))
        data['turnover'] = toReal(data.get('turnover'))
        data['bv1'] = toReal(data.get('bv1'))
        data['bp1'] = toReal(data.get('bp1'))
        data['bv1'] = toReal(data.get('bv1'))
        data['bp2'] = toReal(data.get('bp2'))
        data['bv2'] = toReal(data.get('bv2'))
        data['bp3'] = toReal(data.get('bp3'))
        data['bv3'] = toReal(data.get('bv3'))
        data['bp4'] = toReal(data.get('bp4'))
        data['bv4'] = toReal(data.get('bv4'))
        data['bp5'] = toReal(data.get('bp5'))
        data['bv5'] = toReal(data.get('bv5'))
        data['av1'] = toReal(data.get('av1'))
        data['ap1'] = toReal(data.get('ap1'))
        data['av1'] = toReal(data.get('av1'))
        data['ap2'] = toReal(data.get('ap2'))
        data['av2'] = toReal(data.get('av2'))
        data['ap3'] = toReal(data.get('ap3'))
        data['av3'] = toReal(data.get('av3'))
        data['ap4'] = toReal(data.get('ap4'))
        data['av4'] = toReal(data.get('av4'))
        data['ap5'] = toReal(data.get('ap5'))
        data['av5'] = toReal(data.get('av5'))
        data['datetime'] = toDateTime(data.get('date'), data.get('time'))
    data_list = data_list[0] if len(data_list) == 1 else data_list
    return data_list


if __name__ == "__main__":
    # print(src2dst(real('sz399006')))
    # print(src2dst(real('sh000016')))
    # print(src2dst(real(['sh600000', 'sz000001'])))
    pass
