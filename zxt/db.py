import datetime
import decimal
import json
import pymssql
import pymysql
import sqlite3


def initConnection_mysql(host, port, user, password, database, charset, local_infile=False, *args, **kwargs):  # yapf: disable
    '''
    执行 help(pymysql.connections.Connection.__init__) 查看详情
    params = { 'host': '主机', 'port': 0, 'user': '用户', 'password': '密码', 'database': '', 'charset': 'utf8', 'local_infile': False }
    connection = initConnection_mysql(**params)
    '''
    port = int(port) if type(port) == str else port
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=database, charset=charset, cursorclass=pymysql.cursors.DictCursor, local_infile=local_infile)  # yapf: disable
    # 要执行(LOAD DATA)需要(local_infile=1)
    return connection


def initConnection_mssql(host, port, user, password, database, charset, *args, **kwargs):  # yapf: disable
    '''
    执行 help(pymssql.connect) 查看详情
    params = { 'host': '主机', 'port': 0, 'user': '用户', 'password': '密码', 'database': '', 'charset': 'utf8', 'local_infile': False }
    connection = initConnection_mysql(**params)
    '''
    port = str(port) if type(port) == int else port
    connection = pymssql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)  # yapf: disable
    return connection


def initConnection_sqlite(database, *args, **kwargs):
    connection = sqlite3.connect(database)
    return connection


def select_mysql(cursor, sqlStr, isDictNotList=True):
    cursor.execute(sqlStr)
    if isDictNotList:
        results = [dict(row) for row in cursor]
    else:

        def calcData(d, cols):
            return [d[col] for col in cols]

        head = [col[0] for col in cursor.description]
        results = [calcData(row, head) for row in cursor]
        results.insert(0, head)
    return results


def select_mssql(cursor, sqlStr, isDictNotList=True):
    cursor.execute(sqlStr)
    if isDictNotList:
        head = [col[0] for col in cursor.description]
        results = [dict(zip(head, data)) for data in cursor.fetchall()]
    else:
        head = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        results.insert(0, head)
    return results


def select_sqlite(cursor, sqlStr, isDictNotList=True):
    return select_mssql(cursor, sqlStr, isDictNotList)


def guess_placeholder(cursor, PH):
    '''
    PH(placeholder)(SQL占位符)可能为 %s 或 ?
    '''
    if not PH:
        if isinstance(cursor, pymysql.cursors.DictCursor):
            PH = '%s'
        else:
            PH = '?'
    return PH


def execute_update_4_upsert(cursor, tbName, kvs: dict, uniqueKeys, PH):
    PH = guess_placeholder(cursor, PH)
    uniKVs = dict([(unikey, kvs[unikey]) for unikey in uniqueKeys])
    kvs_K, kvs_V = [*zip(*kvs.items())]
    uniKVs_K, uniKVs_V = [*zip(*uniKVs.items())]
    kvs_K_str = ','.join([k + '=' + PH for k in kvs_K])
    uniKVs_K_str = ' AND '.join([k + '=' + PH for k in uniKVs_K])
    sqlFmt = 'UPDATE {} SET {} WHERE {}'.format(tbName, kvs_K_str, uniKVs_K_str)  # yapf: disable
    cursor.execute(sqlFmt, kvs_V + uniKVs_V)


def execute_insert_4_upsert(cursor, tbName, kvs: dict, uniqueKeys, PH):
    ''' INSERT INTO {tbName}({KEYS}) SELECT {VALS} FROM DUAL WHERE NOT EXISTS(SELECT 1 FROM {tbName} WHERE {QUERY_COND}) '''
    PH = guess_placeholder(cursor, PH)
    uniKVs = dict([(unikey, kvs[unikey]) for unikey in uniqueKeys])
    kvs_K, kvs_V = [*zip(*kvs.items())]
    uniKVs_K, uniKVs_V = [*zip(*uniKVs.items())]
    kvs_K_str = ','.join(kvs_K)
    kvs_V_str = ','.join([PH for v in kvs_V])
    uniKVs_K_str = ','.join([k + '=' + PH for k in uniKVs_K])
    sqlFmt = 'INSERT INTO {} ({}) SELECT {} FROM DUAL WHERE NOT EXISTS(SELECT 1 FROM {} WHERE {})'.format(tbName, kvs_K_str, kvs_V_str, tbName, uniKVs_K_str)  # yapf: disable
    cursor.execute(sqlFmt, kvs_V + uniKVs_V)


def execute_insert(cursor, tbName, kvs: dict, PH):
    '''
    记得自己写[connection.commit()]以提交数据; (PH=None)时,代码会猜测占位符.
    '''
    PH = guess_placeholder(cursor, PH)
    kvs_K, kvs_V = [*zip(*kvs.items())]
    kvs_K_str = ','.join(kvs_K)
    kvs_V_str = ','.join([PH for v in kvs_V])
    sqlFmt = 'INSERT INTO {} ({}) VALUES ()'.format(tbName, kvs_K_str, kvs_V_str)  # yapf: disable
    cursor.execute(sqlFmt, kvs_V)


def execute_update(cursor, tbName: str, kvs: dict, uniqueKeys, PH):
    '''
    记得自己写[connection.commit()]以提交数据; (PH=None)时,代码会猜测占位符.
    '''
    execute_update_4_upsert(cursor, tbName, kvs, uniqueKeys, PH)


def execute_update_whereCond(cursor, tbName, kvs: dict, whereCond, PH=None):
    '''
    记得自己写[connection.commit()]以提交数据; (PH=None)时,代码会猜测占位符.
    '''
    PH = guess_placeholder(cursor, PH)
    kvs_K, kvs_V = [*zip(*kvs.items())]
    kvs_K_str = ','.join([k + '=' + PH for k in kvs_K])
    sqlFmt = 'UPDATE {} SET {} WHERE {}'.format(tbName, kvs_K_str, whereCond)
    cursor.execute(sqlFmt, kvs_V)


def execute_upsert(cursor, tbName, kvs: dict, uniqueKeys, PH=None):
    '''
    记得自己写[connection.commit()]以提交数据; (PH=None)时,代码会猜测占位符.
    判断(uniqueKeys)能否作为主键的SQL语句:
    SELECT * FROM table_name GROUP BY key1,key2,key3 HAVING COUNT(0)>1;
    '''
    execute_update_4_upsert(cursor, tbName, kvs, uniqueKeys, PH)
    execute_insert_4_upsert(cursor, tbName, kvs, uniqueKeys, PH)


def saveToDbTable(cursor, tbName, allLine, uniqueKeys, PH=None):
    '''
    记得自己写[connection.commit()]以提交数据; (PH=None)时,代码会猜测占位符.
    '''
    for line in allLine:
        if uniqueKeys:
            execute_upsert(cursor, tbName, line, uniqueKeys, PH)
        else:
            execute_insert(cursor, tbName, line, PH)


def saveJsonToSqlite(allLine, dbName, tbName, dtie=False, dvie=False):
    ''' SELECT json_extract(jsontext, '$.column1') FROM tbName '''

    def JSON_EXTRACT(jsontext, jsonpath):
        pass

    if allLine:
        if type(allLine[0]) in (tuple, list):
            # 此时,需求:第0个数据是head,后续的数据都是data.
            if [line for line in allLine if len(allLine[0]) != len(line)]:
                raise ValueError('param allLine illegal')
            allLine = [dict(zip(allLine[0], line)) for line in allLine[1:]]
        elif type(allLine[0]) is dict:
            pass
        else:  # ValueError:传入无效的参数.
            raise ValueError('param allLine illegal')
    connection = initConnection_sqlite(dbName)
    connection.create_function('JSON_EXTRACT', 2, JSON_EXTRACT)
    cursor = connection.cursor()
    if dtie:  # Drop Table If Exists
        sqlStatement = 'DROP TABLE IF EXISTS {}'.format(tbName)
        cursor.execute(sqlStatement)
    if dvie:  # Drop View If Exists
        sqlStatement = 'DROP VIEW  IF EXISTS {}_v'.format(tbName)
        cursor.execute(sqlStatement)
    sqlStatement = 'CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY AUTOINCREMENT, jsontext TEXT NOT NULL)'.format(tbName)  # yapf: disable
    cursor.execute(sqlStatement)

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

    allKey = {}
    sqlStatement = 'INSERT INTO {} (jsontext) VALUES (?)'.format(tbName)
    for line in allLine:
        allKey.update(dict([(key, True) for key in line.keys()]))
        jsontext = json.dumps(line, separators=(',', ':'), ensure_ascii=False, default=json_handler)  # yapf: disable
        cursor.execute(sqlStatement, (jsontext, ))
    allKey = sorted(allKey.keys())
    allKey = ["JSON_EXTRACT(jsontext, '$.{0}') AS {0}".format(key) for key in allKey]  # yapf: disable
    allKey.insert(0, 'id')
    sqlStatement = 'CREATE VIEW IF NOT EXISTS {0}_v AS SELECT {1} FROM {0}'.format(tbName, ',\r\n'.join(allKey) + '\r\n')  # yapf: disable
    cursor.execute(sqlStatement)
    cursor.close()
    connection.commit()
    connection.close()


if __name__ == '__main__':
    print('Not Implemented')
