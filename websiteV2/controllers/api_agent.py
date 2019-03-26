"""
author: xiaoniu
date: 2019-03-23
desc: 代理蓝图，有以下几种
GET /api/agent/relation/<int:uid> 获取该uid对应的所有联系
POST /api/agent/relation/ 添加新的资源
PUT /api/agent/relation 修改哪个资源
DELETE /api/agent/relation 删除联系
"""
from flask import Blueprint, request, session, redirect, url_for
import json
from service.agentservice import school_agent_service
from controllers.user import login_required

api_agent_blueprint = Blueprint('api/agent', __name__, url_prefix='/api')


@api_agent_blueprint.route('/agent/relation', methods=['GET'])
@login_required
def get_agent_relations():
    """
        url: /api/bussiness/relation,
        type: 'GET',
        dataType: 'json'
    获取该商务所有学院的联系，并生成d3封装的RelationGraph类可用的数据格式，json
    :return: json格式的数据
    """
    current_user = session['username']
    # 获取具体数据
    uid = int(current_user['ID'])
    utype = int(current_user['TYPE'])

    results = None
    # 学校商务
    if utype == 0:
        results = school_agent_service.get_relations_by_id(uid, isSchool = True)
    
    # 企业商务
    else:
        results = school_agent_service.get_relations_by_id(uid , isSchool = False)


    return json.dumps(results)


@api_agent_blueprint.route('/agent/relation', methods=['POST'])
@login_required
def append_agent_relation():
    """
    创建当前登陆者和别人的联系
    :return: dict : { success:True,create_time:"2019/3/4",id:"123" }
    """
    current_user = session['username']

    # 获取信息
    info = {
        "user_id": current_user["ID"],
        "level_one": request.form['level_one'],
        "level_two": request.form['level_two'],
        "contract_name": request.form['contract_name'],
        "link_method": request.form['link_method'],
        "remark": request.form['remark'],
        "create_time": request.form["create_time"]
    }
    
    # 企业商务
    if current_user["TYPE"] == "1":
        result = school_agent_service.append_relation(info , isSchool = False)
    # 高校商务
    else:
        result = school_agent_service.append_relation(info, isSchool = True)
    
    return json.dumps(result)


@api_agent_blueprint.route('/agent/relation', methods=['DELETE'])
@login_required
def delete_agent_relation():
    """
    “删除”联系，并不是真正的删除，
    :return:
    """
    # 状态码
    ret = {'success': False}
    # 获取参数
    relation_id = request.form.get('relation_id', type=int)

    current_user = session['username']
    
    # 企业商务
    if current_user["TYPE"] == "1":
        ret['success'] = school_agent_service.delete_relation(relation_id, isSchool = False)
    
    else:
        ret['success'] = school_agent_service.delete_relation(relation_id, isSchool = True)
        
    return json.dumps(ret)


@api_agent_blueprint.route('/agent/relation', methods=['PUT'])
@login_required
def update_agent_relation():
    """
    更新当前登陆者和别人的联系
    需要 relation_id
    :return: dict : { success:True }
    """
    current_user = session['username']
    relation_id = request.form.get('id', type=int)
    ret = {'success': False}

    info = {
        "level_one": request.form['level_one'],
        "level_two": request.form['level_two'],
        "contract_name": request.form['contract_name'],
        "link_method": request.form['link_method'],
        "remark": request.form['remark'],
        "create_time": request.form['create_time'],
    }

    # 企业商务
    if current_user["TYPE"] == "1":
        ret['success'] = school_agent_service.update_relation(relation_id, info , isSchool = False)

    # 高校商务
    else:
        ret['success'] = school_agent_service.update_relation(relation_id, info , isSchool = True)

    return json.dumps(ret)
