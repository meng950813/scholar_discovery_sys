"""
author: xiaoniu
date: 2019-03-23
desc: 代理蓝图，有以下几种
GET /api/agent/relation/<int:uid> 获取该uid对应的所有联系
POST /api/agent/relation/ 添加新的资源
PUT /api/agent/relation 修改哪个资源
DELETE /api/agent/relation/<int:id> 删除联系
"""
from flask import Blueprint, request, session, redirect, url_for
import json
from service.agentservice import school_agent_service

agent_blueprint = Blueprint('api/agent', __name__, url_prefix='/api')


@agent_blueprint.route('/agent/relation', methods=['GET'])
def get_agent_relations():
    """
        url: /api/bussiness/relation,
        type: 'GET',
        data: {id: 10000, type: 0},
        dataType: 'json'
    获取该商务所有学院的联系，并生成d3封装的RelationGraph类可用的数据格式，json
    :return: json格式的数据
    """
    user = session.get("username")
    # TODO:判断是否登陆
    if not user:
        return redirect(url_for("login"))

    uid = request.args.get('id', type=int)
    utype = request.args.get('type', type=int)

    results = None
    # 学校商务
    if utype == 0:
        results = school_agent_service.get_relations_by_id(uid)

    return json.dumps(results)


@agent_blueprint.route('/agent/relation', methods=['POST'])
def append_agent_relation():
    """
    创建当前登陆者和别人的联系
    :return: dict : { success:True,create_time:"2019/3/4",id:"123" }
    """
    user = session.get("username")
    # TODO:判断是否登陆
    if not user:
        return redirect(url_for("login"))

    info = {
        "user_id": user["ID"],
        "level_one": request.form['level_one'],
        "level_two": request.form['level_two'],
        "contract_name": request.form['contract_name'],
        "link_method": request.form['link_method'],
        "remark": request.form['remark'],
        "create_time": request.form["create_time"]
    }

    # 企业商务
    if user["TYPE"] == "1":
        # user_service
        pass
    # 高校商务
    else:
        result = school_agent_service.append_relation(info)
        return json.dumps(result)


@agent_blueprint.route('/agent/relation', methods=['DELETE'])
def delete_agent_relation():
    """
    “删除”联系，并不是真正的删除，
    :return:
    """
    user = session.get("username")
    # TODO:判断是否登陆
    if not user:
        return redirect(url_for("login"))
    # 状态码
    ret = {'success': False}
    # 获取参数
    relation_id = request.form.get('relation_id', type=int)
    ret['success'] = school_agent_service.delete_relation(relation_id)

    return ret


@agent_blueprint.route('/agent/relation', methods=['PUT'])
def update_agent_relation():
    """
    更新当前登陆者和别人的联系
    需要 relation_id
    :return: dict : { success:True }
    """
    user = session.get("username")
    if not user:
        return redirect(url_for("login"))

    relation_id = request.form.get('relation_id', type=int)
    ret = {'success': False}

    info = {
        "user_id": user["ID"],
        "level_one": request.form['level_one'],
        "level_two": request.form['level_two'],
        "contract_name": request.form['contract_name'],
        "link_method": request.form['link_method'],
        "remark": request.form['remark'],
    }
    # 企业商务
    if user["TYPE"] == "1":
        # user_service
        pass
    # 高校商务
    else:
        ret['success'] = school_agent_service.update_relation(relation_id, info)
    return ret
