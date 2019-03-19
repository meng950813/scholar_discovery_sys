"""
author: xiaoniu
date: 2019-03-14
desc: api蓝图，主要负责获取请求并返回需要的数据，格式为json
"""
from flask import Blueprint, request
import json, logging, os
from utils.query import query
import utils.relation
from service.schoolservice import school_service
from service.teacherservice import teacher_service


api_blueprint = Blueprint('api', __name__, url_prefix='/api')


@api_blueprint.route('/school/address', methods=['POST'])
def school_address():
    """
    根据关键字获取满足条件的学校 并返回
    :return: {school: [], college: [}
    """
    keyword = request.form.get('keyword')
    # 限定输出的个数为10个
    max_count = 10
    # 查询
    data = query.do_query(keyword, {})
    results = query.prints_for_school(data, None)
    # 保存所有的学校名称
    school_names = []
    # 规范化名称
    special_cities = ['北京', '天津', '上海', '重庆']
    for result in results:
        if result['province'] in special_cities:
            result['province'] += '市'
        else:
            result['province'] += '省'
        # 转换成map.js需要的格式
        result['school'] = result.pop('school_name')
        result['address'] = ['中国', result.pop('province'), result.pop('city')]
        result['weight'] = result.pop('score')

        school_names.append(result['school'])
    # 查询数据库获得所有的学校的经纬度
    schools = school_service.get_position_by_names(school_names)
    # 整合数据
    for result in results:
        result.update(schools[result['school']])

    return json.dumps(results[:max_count])


@api_blueprint.route('/mapdata/<path:filename>')
def get_mapdata(filename):
    """
    根据文件名获取对应的地图数据，并返回
    :param filename: 文件路径
    :return: 若存在文件，则返回该文件的数据，若不存在，则返回一个空数组
    """
    path = os.path.join(os.getcwd(), 'static', 'mapdata')
    logging.info(os.path.join(path, filename))
    # 读取文件，若没有文件则返回空
    try:
        with open(os.path.join(path, filename), 'r', encoding='utf-8') as fp:
            data = fp.read()
    except FileNotFoundError:
        data = "[]"
    return data


@api_blueprint.route('/person/relation', methods=['POST'])
def person_relation():
    """
    获取个人与其他人的关系
    :return:
    """
    teacher_id = request.form.get('teacher_id', type=int)
    # 获取该老师的所有联系
    relations = teacher_service.get_relations_by_id(teacher_id)
    # 获取有联系的老师的所有老师的ID数组
    teacher_id_set = set()
    for relation in relations:
        teacher_id_set.add(relation['teacher2_id'])
    teacher_id_set.add(teacher_id)
    # 获取所有老师
    teachers = teacher_service.get_teachers_by_ids(teacher_id_set)
    # 获取老师的头衔，如果有的话
    academic_titles = teacher_service.get_academic_titles_by_ids(teacher_id_set)
    # 总的学术头衔
    total_categories = ['未知', '副教授', '教授']
    total_categories.extend(teacher_service.get_total_academic_titles())
    # 获取d3.js封装的RelationGraph所需的数据格式
    data = utils.relation.handle_relations(teachers, relations, academic_titles, total_categories)
    return json.dumps(data)
