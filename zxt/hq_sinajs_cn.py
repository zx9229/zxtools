import datetime
import urllib
import urllib.request
import re


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


def tmp_test(code_list):
    '''
    http://hq.sinajs.cn/list=sh510300
    http://hq.sinajs.cn/list=P_OP_io2007C4700
    http://hq.sinajs.cn/list=CON_OP_10002503
    https://hq.sinajs.cn/list=nf_IF2009
    '''
    if type(code_list) in (tuple, list):
        code_list = ','.join(code_list)

    url = 'http://hq.sinajs.cn/list={codeList}'.format(codeList=code_list)
    content = urllib.request.urlopen(url).read().decode('GB18030')

    result_list = []
    fields_list = [
        ("名字", "今开盘", "昨收盘", "最新价", "最高价", "最低价", "买1价", "卖1价", "成交量", "成交额",
         "买1量", "买1价", "买2量", "买2价", "买3量", "买3价", "买4量", "买4价", "买5量", "买5价",
         "卖1量", "卖1价", "卖2量", "卖2价", "卖3量", "卖3价", "卖4量", "卖4价", "卖5量", "卖5价",
         "日期", "时间", "未知字段1", "未知字段2"),
        ("买1量", "买1价", "最新价", "卖1价", "卖1量", "持仓量", "未知字段1", "行权价", "前结算",
         "今开盘", "涨停价", "跌停价", "卖5价", "卖5量", "卖4价", "卖4量", "卖3价", "卖3量", "卖2价",
         "卖2量", "卖1价", "卖1量", "买1价", "买1量", "买2价", "买2量", "买3价", "买3量", "买4价",
         "买4量", "买5价", "买5量", "时间戳", "未知字段1", "未知字段2", "未知字段3", "未知字段4",
         "未知字段5", "未知字段6", "最高价", "最低价", "未知字段7", "未知字段8", "未知字段9"),
        ("开盘价", "最高价", "最低价", "最新价", "成交量", "未知字段1", "持仓量", "未知字段2", "未知字段3",
         "涨停", "跌停", "未知字段4", "未知字段5", "昨收", "昨结", "昨持仓", "买1价", "买1量", "买价",
         "买量", "买价", "买量", "买价", "买量", "买价", "买量", "卖1价", "卖1量", "卖价", "卖量",
         "卖价", "卖量", "卖价", "卖量", "卖价", "卖量", "日期", "时间", "未知字段6", "未知字段7",
         "未知字段8", "未知字段9", "未知字段10", "未知字段11", "未知字段12", "未知字段13", "未知字段14",
         "未知字段15", "未知字段16", "名字"),
        ("买1量", "买1价", "最新价", "卖1价", "卖1量", "持仓量", "涨跌幅", "行权价", "昨收", "今开",
         "涨停", "跌停", "卖5价", "卖5量", "卖4价", "卖4量", "卖3价", "卖3量", "卖2价", "卖2量",
         "卖1价", "卖1量", "买1价", "买1量", "买2价", "买2量", "买3价", "买3量", "买4价", "买4量",
         "买5价", "买5量", "时间戳", "未知字段1", "未知字段2", "未知字段3", "标的代码", "合约简称", "振幅",
         "最高价", "最低价", "成交量", "未知字段4", "未知字段5", "昨结算", "call_put", "到期日",
         "还有多少天", "未知字段6", "内在价值", "时间价值")
    ]
    rePattern = re.compile(
        r'var hq_str_(?P<sina_code>.*?)="(?P<sina_data>.*?)";')
    for line in content.splitlines():
        reMatch = rePattern.match(line)
        sina_code = reMatch.groupdict()['sina_code']
        sina_data = reMatch.groupdict()['sina_data']
        field_lst = sina_data.split(',')
        for fields in fields_list:
            if len(fields) == len(field_lst):
                field_map = dict(zip(fields, field_lst))
                field_map['sina_code'] = sina_code
                result_list.append(field_map)
                break
    return result_list


if __name__ == "__main__":
    # print(src2dst(real('sz399006')))
    # print(src2dst(real('sh000016')))
    # print(src2dst(real(['sh600000', 'sz000001'])))
    pass
