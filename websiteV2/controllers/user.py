"""
author: chen
date: 2019-03-16
desc: user蓝图，主要负责获取请求并返回需要的数据，格式为json
"""

from flask import Blueprint, request,redirect,url_for,session
from service.userservice import user_service
import json

user_blueprint = Blueprint('user', __name__, url_prefix='/user')

@user_blueprint.route('/dologin', methods=['POST'])
def dologin():
    """
    处理登录事件
    :return:
    """
    name = request.form['username']
    pwd = request.form['password']
    

    result = user_service.dologin(name,pwd)

    if "error" in result:
        # 请求失败
        return redirect(url_for("login" , error = 1))

    session["username"] = result

    # print(result)
    
    # TODO 根据用户身份重定向
    if result["TYPE"] == "1":

        return redirect(url_for("governPersonal"))

    return redirect(url_for("schoolPersonal"))


if __name__ == '__main__':
    pass

