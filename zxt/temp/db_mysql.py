import csv


def calcSqlLoadData(filename,
                    tablename,
                    mode='r',
                    encoding='utf8',
                    dialect="excel",
                    isLocal=True,
                    emptyReplaceIgnore='',
                    setSection='',
                    *args,
                    **kwargs):
    '''
    https://dev.mysql.com/doc/refman/8.0/en/load-data.html
    LOAD DATA
        [LOW_PRIORITY | CONCURRENT] [LOCAL]
        INFILE 'file_name'
        [REPLACE | IGNORE]
        INTO TABLE tbl_name
        [PARTITION (partition_name [, partition_name] ...)]
        [CHARACTER SET charset_name]
        [{FIELDS | COLUMNS}
            [TERMINATED BY 'string']
            [[OPTIONALLY] ENCLOSED BY 'char']
            [ESCAPED BY 'char']
        ]
        [LINES
            [STARTING BY 'string']
            [TERMINATED BY 'string']
        ]
        [IGNORE number {LINES | ROWS}]
        [(col_name_or_user_var
            [, col_name_or_user_var] ...)]
        [SET col_name={expr | DEFAULT}
            [, col_name={expr | DEFAULT}] ...]
    '''
    filename = filename.replace('\\', '/')
    emptyReplaceIgnore = emptyReplaceIgnore.upper()
    if emptyReplaceIgnore not in ('', 'REPLACE', 'IGNORE'):
        raise ValueError('invalid param emptyReplaceIgnore')

    def funIFNULL(src, dst):
        return dst if src is None else src

    def convertParam(key):
        kvs = {
            '\t': r'\t',
            '\r': r'\r',
            '\n': r'\n',
            '\r\n': r'\r\n',
            '\\': r'\\'
        }
        val = kvs.get(key)
        val = key if val is None else val
        return val

    with open(file=filename, mode=mode, encoding=encoding, newline='') as f:
        csvReader = csv.DictReader(f, dialect=dialect)
        headline = csvReader.fieldnames
        cDialect = csv.get_dialect(dialect)
    sqlStatement = '''
    LOAD DATA {local} INFILE '{filename}' {emptyReplaceIgnore}
    INTO TABLE {tablename}
    FIELDS TERMINATED BY '{ftb}' ENCLOSED BY '{fencb}' ESCAPED BY '{fescb}'
    LINES  TERMINATED BY '{ltb}' STARTING BY ''
    IGNORE 1 ROWS
    ({field_name_list})
    '''.format(
        local='LOCAl' if isLocal else '',
        filename=filename,
        emptyReplaceIgnore=emptyReplaceIgnore,
        tablename=tablename,
        ftb=convertParam(cDialect.delimiter),
        fencb=convertParam(cDialect.quotechar),
        fescb=funIFNULL(convertParam(cDialect.escapechar), r''),
        # fescb=funIFNULL(convertParam(cDialect.escapechar), r'\\'),
        ltb=convertParam(cDialect.lineterminator),
        field_name_list=','.join(headline))
    if setSection:
        sqlStatement += ('SET ' + setSection)
    return sqlStatement


def mysqlLoadData(cursor, filename, tablename, *args, **kwargs):
    '''
    记得自己写[connection.commit()]以提交数据;
    '''
    sqlStr = calcSqlLoadData(filename, tablename, *args, **kwargs)
    cursor.execute(sqlStr)


if __name__ == '__main__':
    print('Not Implemented')
