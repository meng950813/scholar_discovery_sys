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
import utils.wordcloud
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


@api_blueprint.route('/teacher/relation', methods=['POST'])
def teacher_relation():
    """
    获取个人与其他人的关系,请求格式如下
        url: '/api/person/relation',
        type: 'POST',
        data: {teacher_id: 137950},
        dataType: 'json'
    :return: 返回RelationGraph类所需要的json
    """
    # 获取老师id
    teacher_id = request.form.get('teacher_id', type=int)
    # 获取该老师的所有联系
    relations = teacher_service.get_relations_by_ids(teacher_id)
    # 获取有联系的老师的所有老师的ID数组
    teacher_id_set = set([relation['teacher2_id'] for relation in relations])
    teacher_id_set.add(teacher_id)
    # 获取所有老师
    teachers = teacher_service.get_teachers_by_ids(teacher_id_set, ['ID', 'NAME', 'TITLE'])
    # 获取老师的头衔，如果有的话
    academic_titles = teacher_service.get_academic_titles_by_ids(teacher_id_set)
    # 总的学术头衔
    total_categories = ['未知', '副教授', '教授']
    total_categories.extend(teacher_service.get_total_academic_titles())
    # 获取d3.js封装的RelationGraph所需的数据格式
    data = utils.relation.handle_relations(teachers, relations, academic_titles, total_categories)
    return json.dumps(data)


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


@api_blueprint.route('/word_cloud', methods=['POST'])
def get_wordcloud():
    """
    根据老师id获取对应的关键字，并生成WordCloud可用的数据格式
    :return: 依赖于d3.js的WordCloud类可用的数据格式
    """
    teacher_id = request.form.get('teacher_id', type=int)
    # 查询内存，获取研究的词
    words = utils.wordcloud.get_keywords_of_id(teacher_id)
    if words is None:
        return json.dumps([])

    # 获取最大的权值
    handle_data = []
    max_score = None
    for key, value in words.items():
        if max_score is None:
            max_score = value
        handle_data.append({'text': key, 'size': value / max_score * 100})
    # 取前若干个
    return json.dumps(handle_data[:50])


def get_teachers_by_school(school_name, keyword):
    """
    根据学校名和关键字获得该学校的相关的所有老师，并按照学院进行聚合
    :param school_name: 学校名
    :param keyword: 关键字
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
    if len(teacher_ids) > 0:
        keys = ['ID', 'NAME', 'TITLE', 'SCHOOL_ID', 'INSTITUTION_ID', 'BIRTHYEAR', 'FIELDS', 'ACADEMICIAN', 'OUTYOUTH', 'CHANGJIANG']
        data = teacher_service.get_teachers_grouping_institutions(teacher_ids, keys, lambda t: t['FIELDS'] is None)
        # 获取学院信息
        infos = school_service.get_institutions_by_ids(school_id, id_institutions.keys(), institution_keys) if len(id_institutions) > 0 else {}
        # 获取学校
        school = data[school_id]
        # 转换学院id=> 学院名
        for institution_id, values in school.items():
            if isinstance(institution_id, int):
                institution_name = id_institutions[institution_id]
                teacher_count += len(values['teachers'])
                school[institution_name] = {'teachers': school.pop(institution_id)['teachers'], 'info': infos[institution_id]}
    return {
             'number': teacher_count,
             'institutions': school,
    }
