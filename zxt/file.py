import codecs
import csv
import os


def saveByList(allLine, filename, mode, encoding, dialect=None, kwds={}, skipLineNum=0):  # yapf: disable
    '''
    以(csv.writer)保存数据
    mode: a(append,附加), w(清空文件内容然后写入)
    encoding = 'utf_8'或'utf8'等.
    skipLineNum = 1 跳过前1行数据.
    '''
    assert type(allLine) in (list, tuple)
    if 0 < len(allLine):
        assert type(allLine[0]) in (list, tuple)
    if 0 < skipLineNum:
        allLine = allLine[skipLineNum:]
    dirName = os.path.dirname(filename)
    if dirName and (not os.path.exists(dirName)):
        os.makedirs(dirName)
    with open(filename, mode, encoding=encoding, newline='') as f:
        csvWriter = csv.writer(f, dialect=dialect, **kwds)
        csvWriter.writerows(allLine)


def loadByList(filename, mode='r', encoding=None, dialect=None, kwds={}, isListNotDict=True):  # yapf: disable
    '''以(csv.reader)加载数据'''
    with codecs.open(filename, mode=mode, encoding=encoding) as f:
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


def saveByDict(allLine, filename, mode, encoding, dialect=None, kwds={}):
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
    with open(filename, mode, encoding=encoding, newline='') as f:
        headers = sorted([k for k in allLine[0]])
        csvWriter = csv.DictWriter(f, fieldnames=headers, dialect=dialect, **kwds)  # yapf: disable
        csvWriter.writeheader()
        csvWriter.writerows(allLine)


def loadByDict(filename, mode='r', encoding=None, dialect=None, kwds={}, isListNotDict=True):  # yapf: disable
    '''以(csv.DictReader)加载数据'''
    with open(filename, mode, encoding=encoding, newline='') as f:
        csvReader = csv.DictReader(f, dialect=dialect, **kwds)
        allLine = None
        def toList(d): return [d[col] for col in csvReader.fieldnames]
        if isListNotDict:
            allLine = [toList(row) for row in csvReader]
        else:
            allLine = [row for row in csvReader]
        return allLine
