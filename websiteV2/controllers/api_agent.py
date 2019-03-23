"""
author: xiaoniu
date: 2019-03-23
desc: 代理蓝图，有以下几种
GET /api/agent/relation/<int:uid> 获取该uid对应的所有联系
POST /api/agent/relation/ 添加新的资源
PUT /api/agent/relation 修改哪个资源
DELETE /api/agent/relation/<int:id> 删除联系
"""
from flask import Blueprint, request
import json
from service.schoolagentservice import school_agent_service


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
    uid = request.args.get('id', type=int)
    utype = request.args.get('type', type=int)

    results = None
    # 学校商务
    if utype == 0:
        results = school_agent_service.get_relations_by_id(uid)

    return json.dumps(results)


