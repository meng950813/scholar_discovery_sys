import pymysql, logging
from DBUtils.PooledDB import PooledDB


POOL = None


class DBError(Exception):
    pass


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
    global POOL
    if POOL is not None:
        raise DBError('Engine is already initialized')

    params = dict(host=host, user=user, password=password, database=database, port=port)
    # 数据库打开的默认值
    defaults = dict(use_unicode=True, autocommit=False)
    # 尝试覆盖默认值
    for k, v in defaults.items():
        params[k] = kw.pop(k, v)
    # 更新其他值
    params.update(kw)

    POOL = PooledDB(
        creator=pymysql,  # 使用pymysql连接数据库
        maxconnections=6,  # 连接池允许的最大连接数目，为0或None时表示不限制连接数目
        mincached=2,  # 初始化时连接池的最少空闲链接
        blocking=True, # 连接池中如果没有可用连接后，是否阻塞等待，为False则报错
        maxusage=None,  # 一个连接最多被复用的次数
        setsession=[],  # 开始会话前执行的命令列表
        ping=0,
        **params
    )
    # output
    logging.info('Init mysql engine ok.')


def _select(sql, first, *args):
    """
    select语句
    :param sql: SQL语句 内部变量使用?
    :param first: 是否只获取一个
    :param args: SQL语句中要使用的变量
    :return: 返回查询的值
    """
    global POOL
    connection = None
    cursor = None
    sql = sql.replace('?', '%s')
    logging.info('SQL: %s %s' % (sql, args if len(args) > 0 else ""))

    try:
        connection = POOL.connection()
        cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
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
    finally:
        cursor.close()
        connection.close()


def select_one(sql, *args):
    """
    执行select SQL语句并返回dict结构的结果或None
    :param sql:select的SQL语句，包含?
    :param args:select的SQL语句所对应的值
    :return: dict结构的一个结果或者None
    """
    return _select(sql, True, *args)


def select(sql, *args):
    """
    执行SQL语句
    :param sql:  select的SQL语句，可含?
    :param args: select的SQL语句所对应的值
    :return: list(dict) 或者None
    """
    return _select(sql, False, *args)


if __name__ == '__main__':
    create_engine('root', '9527', 'training')

    teachers = select('select * from es_teacher limit 0,10')
    print(teachers)

