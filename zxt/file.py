import csv
import os


def listTOdict(listLine):
    '''listLine 是 [ ['k1','k2'], ['1v1','1v2'], ['2v1','2v2'] ]'''
    if len(listLine) == 0:
        raise ValueError('invalid param listLine with [len(listLine) == 0]')
    head = listLine[0]
    dictLine = [dict(zip(head, data)) for data in listLine[1:]]
    return dictLine


def dictTOlist(dictLine):
    '''dictLine 是 [ {'k1':'1v1','k2':'1v2'}, {'k1':'2v1','k2':'2v2'} ]'''
    if len(dictLine) == 0:
        raise ValueError('invalid param dictLine with [len(dictLine) == 0]')

    def calcData(d, cols):
        return [d[col] for col in cols]

    head = sorted([k for k in dictLine[0]])
    listLine = [calcData(data, head) for data in dictLine]
    listLine.insert(0, head)
    return listLine


def saveByList(allLine, filename, mode='w', encoding='utf8', dialect='excel', kwds={}, skipLineNum=0):  # yapf: disable
    '''
    以(csv.writer)保存数据
    mode: a(append,附加), w(创建文件/清空文件内容,然后写入)
    encoding = 'utf_8'或'utf8'等.
    skipLineNum = 1 跳过前1行数据(主要用于跳过headline).
    '''
    assert type(allLine) in (list, tuple)
    if 0 < len(allLine):
        assert type(allLine[0]) in (list, tuple)
    if 0 < skipLineNum:
        allLine = allLine[skipLineNum:]
    dirName = os.path.dirname(filename)
    if dirName and (not os.path.exists(dirName)):
        os.makedirs(dirName)
    with open(filename, mode=mode, encoding=encoding, newline='') as f:
        csvWriter = csv.writer(f, dialect=dialect, **kwds)
        csvWriter.writerows(allLine)


def loadByList(filename, mode='r', encoding='utf8', dialect='excel', kwds={}, isListNotDict=True):  # yapf: disable
    '''
    以(csv.reader)加载数据
    isListNotDict = True  (默认值)
    isListNotDict = True  从文件载入数据时,每一行都转换成list
    isListNotDict = False 从文件载入数据时,将首行作为列名,每一行都转换成dict
    '''
    with open(filename, mode=mode, encoding=encoding, newline='') as f:
        allLine = []
        csvReader = csv.reader(f, dialect=dialect, **kwds)
        fields = None
        for row in csvReader:
            if (not isListNotDict) and (fields is None):
                fields = row
                continue
            if isListNotDict:
                allLine.append(row)
            else:
                allLine.append(dict(zip(fields, row)))
        return allLine


def saveByDict(allLine, filename, mode='w', encoding='utf8', dialect='excel', kwds={}):  # yapf: disable
    '''
    以(csv.DictWriter)保存数据
    Python CSV Reader/Writer 例子
    https://blog.csdn.net/u011284860/article/details/51031051
    '''
    assert type(allLine) in (list, tuple)
    if 0 < len(allLine):
        assert type(allLine[0]) is dict
    dirName = os.path.dirname(filename)
    if dirName and (not os.path.exists(dirName)):
        os.makedirs(dirName)
    with open(filename, mode=mode, encoding=encoding, newline='') as f:
        headers = sorted([k for k in allLine[0]])
        csvWriter = csv.DictWriter(f, fieldnames=headers, dialect=dialect, **kwds)  # yapf: disable
        csvWriter.writeheader()
        csvWriter.writerows(allLine)


def loadByDict(filename, mode='r', encoding='utf8', dialect='excel', kwds={}, isListNotDict=False):  # yapf: disable
    '''
    以(csv.DictReader)加载数据
    isListNotDict = False (默认值)
    isListNotDict = True  从文件载入数据时,每一行都转换成list
    isListNotDict = False 从文件载入数据时,将首行作为列名,每一行都转换成dict
    '''
    with open(filename, mode=mode, encoding=encoding, newline='') as f:
        csvReader = csv.DictReader(f, dialect=dialect, **kwds)
        allLine = None

        def toList(d):
            return [d[col] for col in csvReader.fieldnames]

        if isListNotDict:
            allLine = [toList(row) for row in csvReader]
            allLine.insert(0, [col for col in csvReader.fieldnames])
        else:
            allLine = [row for row in csvReader]
        return allLine
