"""
author: 任继位
date: 2019-03-01
数据库访问
可使用的函数有
create_engine 表示创建链接只需要调用一次即可
select_one 从数据库中获取一行dict格式的数据
select 从数据库中获得list(dict) 数据
_select 不关闭数据库的cursor
with connection():
    sql语句执行
    sql语句执行
examples:
sql = 'select * from teacher where id=? and school=?'
sql语句内部不需要加单引号/双引号
select(sql, 102, '清华大学')

TODO:注意：本内容中的SQL语句占位符为? 目前暂时未添加事务的相关处理
"""
import pymysql
import logging
import threading
import functools


# 全局变量
engine = None


class DBError(Exception):
    pass


class _Engine(object):
    """
    _Engine 私有
    """

    def __init__(self, connect):
        """
        初始化函数
        :param connect: 是一个函数 主要用于滞后赋值
        :return:
        """
        self._connect = connect

    def connect(self):
        return self._connect()


def create_engine(user, password, database, host='127.0.0.1', port=3306, **kw):
    """
    初始化全局变量engine,仅仅需要初始化一次即可
    :param user: 数据库用户名
    :param password: 数据库密码
    :param database: 使用哪个数据库
    :param host: 数据库域名
    :param port: 数据库端口
    :param kw: 额外参数
    :return: None
    """
    global engine
    if engine is not None:
        raise DBError('Engine is already initialized')

    params = dict(host=host, user=user, password=password, database=database, port=port)
    # 数据库打开的默认值
    defaults = dict(use_unicode=True, autocommit=False)
    # 尝试覆盖默认值
    for k, v in defaults.items():
        params[k] = kw.pop(k, v)
    # 更新其他值
    params.update(kw)

    # 赋给函数，滞后赋值
    engine = _Engine(lambda: pymysql.connect(**params))
    # output
    logging.info('Init mysql engine ok.')


class _LazyConnection(object):
    """
    _LazyConnection "懒惰"的数据库连接 滞后数据连接,在第一次使用时会连接数据库
    简单地封装了 pymysql的部分函数
    内部使用了全局变量engine,
    内部的connection对象为真正的pymysql.connect()所返回的对象
    """

    def __init__(self):
        self.connection = None

    def cursor(self):
        if self.connection is None:
            logging.info('open connection...')
            self.connection = engine.connect()
        # TODO:数据为dict
        return self.connection.cursor(cursor=pymysql.cursors.DictCursor)

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def cleanup(self):
        if self.connection is not None:
            connection = self.connection
            self.connection = None
            logging.info('close connection ...')

            # 关闭数据库连接
            connection.close()


class _DbContext(threading.local):
    """
    threading.local的子类 添加了多线程可用的函数
    self.connection对象的类型为_LazyConnection
    """
    def __init__(self):
        self.connection = None
        self.transactions = 0

    def is_init(self):
        return self.connection is not None

    def init(self):
        logging.info('open lazy connection...')
        self.connection = _LazyConnection()
        self.transactions = 0

    def cleanup(self):
        self.connection.cleanup()
        self.connection = None

    def cursor(self):
        return self.connection.cursor()


# thread-local db context
_dbContext = _DbContext()


class _ConnectionCtx(object):
    """
    _ConnectionCtx 类用于打开和关闭Connection Context
    """
    def __enter__(self):
        global _dbContext
        self.should_cleanup = False

        if not _dbContext.is_init():
            _dbContext.init()
            self.should_cleanup = True
        return _dbContext.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _dbContext
        if self.should_cleanup:
            _dbContext.cleanup()


def connection():
    """
    :return: _ContextCtx()类，即可以用于
    with connection():
        pass
    """
    return _ConnectionCtx()


def with_select(sql, *args):
    """
    with_select 需要和connection配合使用
    :param sql:
    :param args:
    :return:
    """
    global _dbContext
    cursor = None
    sql = sql.replace('?', '%s')
    logging.info('SQL: %s %s' % (sql, args if len(args) > 0 else ""))

    try:
        cursor = _dbContext.connection.cursor()
        # 执行语句
        cursor.execute(sql, args)

        results = cursor.fetchall()
        return results
    except Exception as e:
        print(e)


def with_connection(func):
    """
    装饰器 内部调用了_ConnectionCtx对象 即返回一个可用的cursor
    @with_connection
    def foo(*args, **kw):
        f1()
        f2()
        f3()
    :param func:
    :return:
    """
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        with _ConnectionCtx():
            return func(*args, **kw)
    return _wrapper


def _select(sql, first, *args):
    """
    select语句
    :param sql: SQL语句 内部变量使用?
    :param first: 是否只获取一个
    :param args: SQL语句中要使用的变量
    :return: 返回查询的值
    """
    global _dbContext
    cursor = None
    sql = sql.replace('?', '%s')
    logging.info('SQL: %s %s' % (sql, args if len(args) > 0 else ""))

    try:
        cursor = _dbContext.connection.cursor()
        # 执行语句
        cursor.execute(sql, args)

        if first:
            result = cursor.fetchone()
            return result
        else:
            results = cursor.fetchall()
            return results
    except Exception as e:
        print(e)
    #finally:
    #    if cursor:
    #        cursor.close()


@with_connection
def select_one(sql, *args):
    """
    执行select SQL语句并返回dict结构的结果或None
    :param sql:select的SQL语句，包含?
    :param args:select的SQL语句所对应的值
    :return: dict结构的一个结果或者None
    """
    return _select(sql, True, *args)


@with_connection
def select(sql, *args):
    """
    执行SQL语句
    :param sql:  select的SQL语句，可含?
    :param args: select的SQL语句所对应的值
    :return: list(dict) 或者None
    """
    return _select(sql, False, *args)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    create_engine('root', '9527', 'training')

    table_names = ['paper', 'keyword']

    # select函数一次获取全部值
    results = select('select * from %s limit 0,10' % table_names[0])
    print(results)

    with connection() as conn:
        # 注意:conn 的类型为_LazyConnection
        cursor1 = conn.cursor()
        cursor1.execute('select * from %s limit 0, 1' % table_names[1])
        result = cursor1.fetchone()
        print(result)

        print(_select('select * from %s limit 0,1' % table_names[1], True))
        print(_select('select * from %s limit 1,1' % table_names[1], True))

