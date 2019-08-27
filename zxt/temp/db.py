import zxt.db as db
import zxt.file as file


def dump_mysql(conf, sql, outcsv, outsqlite, outsqlitetable, *args, **kwargs):
    '''转储, 通过conf连接到数据库, 然后执行sql得到数据, 写入outcsv, 写入outsqlite的outsqlitetable表'''
    connection = db.initConnection_mysql(**conf)
    cursor = connection.cursor()
    allLine = db.select_mysql(cursor, sql, True)
    cursor.close()
    connection.close()
    if outcsv:
        file.saveByDict(allLine, outcsv, 'w', None)
    if outsqlite:
        db.saveJsonToSqlite(allLine, outsqlite, outsqlitetable)


def dump_mssql(conf, sql, outcsv, outsqlite, outsqlitetable, *args, **kwargs):
    '''转储, 通过conf连接到数据库, 然后执行sql得到数据, 写入outcsv, 写入outsqlite的outsqlitetable表'''
    connection = db.initConnection_mssql(**conf)
    cursor = connection.cursor()
    allLine = db.select_mssql(cursor, sql, True)
    cursor.close()
    connection.close()
    if outcsv:
        file.saveByDict(allLine, outcsv, 'w', None)
    if outsqlite:
        db.saveJsonToSqlite(allLine, outsqlite, outsqlitetable)


def dump_sqlite(conf, sql, outcsv, outsqlite, outsqlitetable, *args, **kwargs):
    '''转储, 通过conf连接到数据库, 然后执行sql得到数据, 写入outcsv, 写入outsqlite的outsqlitetable表'''
    connection = db.initConnection_sqlite(**conf)
    cursor = connection.cursor()
    allLine = db.select_sqlite(cursor, sql, True)
    cursor.close()
    connection.close()
    if outcsv:
        file.saveByDict(allLine, outcsv, 'w', None)
    if outsqlite:
        db.saveJsonToSqlite(allLine, outsqlite, outsqlitetable)


def dump_db(db, conf, sql, outcsv, outsqlite, outsqlitetable, *args, **kwargs):
    if False:
        pass
    elif db == 'mysql':
        dump_mysql(conf, sql, outcsv, outsqlite, outsqlitetable)
    elif db == 'mssql':
        dump_mssql(conf, sql, outcsv, outsqlite, outsqlitetable)
    elif db == 'sqlite':
        dump_sqlite(conf, sql, outcsv, outsqlite, outsqlitetable)
    else:
        raise ValueError("unknown param db = " + db.__repr__())


if __name__ == '__main__':
    dbName = 'mysql'
    conf = {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "toor",
        "database": "mysql",
        "charset": "utf8",
        "local_infile": False
    }
    sql = 'SELECT * FROM mysql.user'
    outcsv = './outcsv.csv'
    outsqlite = './outsqlite.db'
    outsqlitetable = 'tmp_user'
    dump_db(dbName, conf, sql, outcsv, outsqlite, outsqlitetable)
