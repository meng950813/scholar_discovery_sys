"""
author: xiaoniu
date: 2019-03-19
desc: api蓝图，主要负责获取请求并返回需要的数据，格式为json
"""
from flask import Blueprint, request
import json
import logging
import os
import time
import utils.query
from utils.query import query
import utils.relation
from service.schoolservice import school_service
from service.teacherservice import teacher_service


api_blueprint = Blueprint('api', __name__, url_prefix='/api')
# 全局变量 用于地图名和对应的文件路径的映射
mapping = None


@api_blueprint.route('/school/address', methods=['POST'])
def school_address():
    """
    根据关键字获取满足条件的学校 并返回
    :return: {school: [], college: [}
    """
    keyword = request.form.get('keyword')
    # 查询
    data = query.do_query(keyword, {})
    results = query.prints_for_school(data, None)
    # 保存所有的学校名称
    school_names = []
    # 规范化
    special_cities = ['北京', '天津', '上海', '重庆']
    for result in results:
        result['province'] += '市' if result['province'] in special_cities else '省'
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

    return json.dumps(results[:10])


@api_blueprint.route('/school/addressV2', methods=['POST'])
def get_school_address_by_keywords():
    """
    根据关键字获取满足条件的学校 并返回满足条件的排名好的学校
    :return: 不限制数量
    """
    keyword = request.form.get('keyword')
    maximum = request.form.get('maximum', type=int)
    # 查询
    data = query.do_query(keyword, {})
    results = query.prints_for_school(data, None)
    # 保存所有的学校名称
    school_names = []
    # 规范化
    special_cities = ['北京', '天津', '上海', '重庆']
    for result in results:
        result['province'] += '市' if result['province'] in special_cities else '省'

        school_names.append(result['school_name'])
    # 查询数据库获得所有的学校的经纬度
    schools = school_service.get_position_by_names(school_names)
    # 整合数据
    for result in results:
        result.update(schools[result['school_name']])

    return json.dumps(results[:maximum])


@api_blueprint.route('/school/scholar_number', methods=['POST'])
def get_school_scholar_number():
    """
    根据学校名获取学校的各个学者的数量，并返回
    :return:
    """
    # 获取学校名数组
    school_names = request.form.getlist('school_names[]')
    # 获取数据
    results = school_service.get_total_scholars_by_schools(school_names)
    return json.dumps(results)


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


@api_blueprint.route('/mapdata/mapping/<name>')
def get_mapdata_by_mapping(name):
    """
    根据名称获取对应的地图数据，并返回数据
    依赖于get_mapdata()函数
    :param name: "中国" 则是中国地图数据，"中国,江苏"则是江苏地图数据
    :return: 若存在该文件，则返回该文件的数据；若不存在，则返回一个空的数组
    """
    base_path = os.path.join(os.getcwd(), 'static', 'mapdata')
    global mapping
    data = []
    # 尝试加载映射数据
    if mapping is None:
        try:
            fp = open(os.path.join(base_path, 'mapping.json'), 'r', encoding='utf-8')
            mapping = json.loads(fp.read())
            fp.close()
        except FileNotFoundError as e:
            print(e)
            return []
    # 是否存在地图对应的路径
    try:
        filename = mapping[name]
    except KeyError as e:
        print(e)
        return []
    # 获取地图数据
    return get_mapdata(filename)


@api_blueprint.route('/institution/relation', methods=['POST'])
def institution_relation():
    """
        url: /api/institution/relation,
        type: 'POST',
        data: {school_id: 17134, institution_id: 557},
        dataType: 'json'
    获取该学校和院系下的所有老师的联系，并生成d3封装的RelationGraph类可用的数据格式，json
    :return: json格式的数据
    """
    # 获取传递的参数
    school_id = request.form.get('school_id', type=int)
    institution_id = request.form.get('institution_id', type=int)
    # 获取该学院和院系对应的所有老师
    teachers = school_service.get_teachers_by_school(school_id, institution_id)
    # 老师的id数组
    teacher_ids = teachers.keys()
    # 老师对应的学术头衔
    academic_titles = teacher_service.get_academic_titles_by_ids(teacher_ids)
    # 总的学术头衔类型
    total_categories = ['未知', '副教授', '教授']
    total_categories.extend(teacher_service.get_total_academic_titles())
    # 获取老师的联系
    relations = teacher_service.get_relations_by_ids(teacher_ids)
    # 获取d3.js封装的RelationGraph所需的数据格式
    data = utils.relation.handle_relations(teachers, relations, academic_titles, total_categories)
    return json.dumps(data)


def get_teachers_by_school(school_name, keyword, limit_teacher_num=3):
    """
    根据学校名和关键字获得该学校的相关的所有老师，并按照学院进行聚合
    :param school_name: 学校名
    :param keyword: 关键字
    :param limit_teacher_num: 限制的老师数目 默认为三个
    :return: dict
    """
    # 查询
    results = utils.query.query_all('老师', keyword, school_name)
    teacher_ids = []
    # 获取学校id
    school_id = None
    school = {}
    teacher_count = 0
    # 学院用得到的键名
    institution_keys = ['ID', 'NKD_NUM', 'SKL_NUM', 'ACADEMICIAN_NUM']
    # 学院id和学院名称映射表
    id_institutions = {}
    for result in results:
        school_id = result['school_id']
        # 添加学院id、学院名映射表
        id_institutions[result['institution_id']] = result['institution_name']
        # 保存老师id
        teacher_ids.append(result['teacher_id'])
    # 查表获取老师的信息
    colleges = {}
    if len(teacher_ids) > 0:
        keys = ['ID', 'NAME', 'TITLE', 'SCHOOL_ID', 'INSTITUTION_ID', 'BIRTHYEAR', 'FIELDS', 'ACADEMICIAN', 'OUTYOUTH', 'CHANGJIANG']
        teachers = teacher_service.get_teachers_by_ids(teacher_ids, keys)
        # 获取学院信息
        infos = school_service.get_institutions_by_ids(school_id, id_institutions.keys(), institution_keys) \
            if len(id_institutions) > 0 else {}
        for result in results:
            college_name = result['institution_name']
            college_id = result['institution_id']
            teacher_id = result['teacher_id']
            score = result['score']

            if college_name not in colleges:
                colleges[college_name] = {'teachers': [], 'info': infos[college_id],'scores':0}
            # 添加学者
            length = len(colleges[college_name]['teachers'])
            if length < limit_teacher_num:
                teacher = teachers[teacher_id]
                if teacher['fields'] is None:
                    continue
                # 添加老师
                colleges[college_name]['teachers'].append(teacher)
                colleges[college_name]['scores'] += result['score']
                length += 1
                teacher_count += 1
    #院系按所展示的人得分排序
    colleges = dict(sorted(colleges.items(),key=lambda x:x[1]['scores'],reverse=True))

    return {
             'number': teacher_count,
             'institutions': colleges,
    }
