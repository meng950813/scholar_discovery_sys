"""
UserService
author: chen
date: 2019-03-16
desc: 内部调用了UserDao的函数，并提供了python下易用的函数
"""
from dao.userdao import user_dao
from utils import encrypt

import re, time


class UserService:
    def __init__(self):
        """
        生成正则表达式 匹配 电话/邮箱/6-8位数字的 user_id
        """
        self.tel = re.compile(r"^\d{11}$")
        self.email = re.compile(r"^[\w\d]+@[\w\d]+\.com$")
        self.u_id = re.compile(r"\d{6,8}")

    def dologin(self, username, pwd=""):
        """
        根据账户名密码
        :param username:用户名（str）
        :param pwd: 原始密码（str）
        :return:  字典对象{'ID': 1, 'NAME': '测试账号', 'TYPE': '1'}
                or {'error':True}
        """
        #  加密出密码
        password = encrypt.encryption(pwd)

        back = None

        # 利用正则判断用户名是否符合标准，以减少 sql 注入可能性
        if self.tel.match(username) :
            # 以电话登陆
            back = user_dao.dologin(telphone = username , pwd = password)
        elif self.email.match(username):
             # 以邮件登陆
            back = user_dao.dologin(email = username , pwd = password)
        elif self.u_id.match(username):
            # 以 id 登陆
            back = user_dao.dologin(u_id = username , pwd = password)
        else:
            return {'error':True}

        # 未查询到结果
        if not back:
            return {'error': True}
        # 返回查询结果
        return back


user_service = UserService()

if __name__ == '__main__':
    import utils.db as db
    from config import DB_CONFIG
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine(**DB_CONFIG)

    # u_id
    print(user_service.dologin('111111', 'a'))

    # email
    print(user_service.dologin('c@m.com', 'a'))

    # error tel
    print(user_service.dologin('11', 'a'))
