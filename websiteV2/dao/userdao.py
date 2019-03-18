"""
author: chen
date: 2019-03-16
desc:  主要用在UserService类中，简单封装了和数据库的交互的SQL语句
"""

import utils.db as db


class UserDao:

    def dologin(self, telphone = None, email = None , u_id = None , pwd = ""):
        """
        根据 账号信息 及 密码 查询用户信息
        :param telphone: 手机号
        :param email: 邮箱
        :param u_id: 用户id
        :param pwd: 密码（32位字符串）
        :return: 用户信息 ： （ID,NAME，TYPE）
        """
        sql_base = "select ID,NAME,TYPE from sys_user where "
        argu = None
        if telphone:
            sql_base += "TEL_NUMBER = ?"
            argu = telphone
        elif email:
            sql_base += "EMAIL = ?"
            argu = email
        elif u_id:
            sql_base += "ID = ?"
            argu = u_id
        else:
            print("error arugments")
            return  False
        sql_base += " and PASSWORD = ?"
        # 调用语句
        result = db.select_one(sql_base, argu, pwd )

        return result

user_dao = UserDao()


if __name__ == '__main__':
    import utils.db as db
    from config import DB_CONFIG
    import logging


    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine(DB_CONFIG['user'], DB_CONFIG['pwd'], DB_CONFIG['db_name'])

    print(user_dao.dologin(telphone = 123 , pwd = "1f89eaa608f335e37869c84d856bf235"))
    print(user_dao.dologin(email = 123 , pwd = "1f89eaa608f335e37869c84d856bf235"))
    print(user_dao.dologin(u_id = 1 , pwd="1f89eaa608f335e37869c84d856bf235"))