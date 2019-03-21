"""
author: chen
date: 2019-03-16
desc: user蓝图，主要负责获取请求并返回需要的数据，格式为json
"""

from flask import Blueprint, request,redirect,url_for,session
import json
from service.userservice import user_service

user_blueprint = Blueprint('user', __name__, url_prefix='/user')

@user_blueprint.route('/dologin', methods=['POST'])
def dologin():
    """
    处理登录事件
    :return:
    """
    name = request.form['username']
    pwd = request.form['password']
    
    # TODO 添加 session 部分

    result = user_service.dologin(name,pwd)

    if "error" in result:
        # 请求失败
        return redirect(url_for("login" , error = 1))

    session["username"] = result

    print(result)
    
    # TODO 根据用户身份重定向
    if result["TYPE"] == "1":

        return redirect(url_for("governPersonal"))

    return redirect(url_for("schoolPersonal"))


@user_blueprint.route('/createRelationship', methods=['POST'])
def createRelationship():
    """
    创建联系
    :return: dict : { success:True,create_time:"2019/3/4",id:"123" }
    """

    user = session.get("username")
    # 判断是否登陆
    if not user:
         return redirect(url_for("login")) 
    
    info = {
        "user_id" : user["ID"],
        "level_one" : request.form['level_one'],
        "level_two" : request.form['level_two'],
        "contract_name" : request.form['contract_name'],
        "link_method" : request.form['link_method'],
        "remark" : request.form['remark'],
        "create_time" : request.form["create_time"]
    }

    # 企业商务
    if user["TYPE"] == "1":
        # user_service
        pass
    # 高校商务
    else:
        result = user_service.createSchoolRelation(info)
        print("in user.py , " , result )
        return json.dumps(result)

if __name__ == '__main__':
    pass

