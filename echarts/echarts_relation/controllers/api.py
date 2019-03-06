"""
author: xiaoniu
date: 2019-03-05
desc: api蓝图，主要负责获取请求并返回需要的数据，格式为json
"""
from flask import Blueprint, request
import json
from service.schoolservice import school_service
from service.teacherservice import teacher_service
import utils

api_blueprint = Blueprint('api', __name__, url_prefix='/api')


@api_blueprint.route('/institution/address')
def institution_address():
    """
    根据关键字和关键字id获取满足条件的学校 学院和学院的位置
    :return: [{'school': school_name, 'institution': institution_name, 'school_address': address1, 'institution_address': address2}, ]
    访问: /api/institution/address?keyword=材料&keyword_id=1
    """
    keyword = request.args.get('keyword')
    keyword_id = request.args.get('keyword_id')
    # 暂时获得定死的数据
    arr = []
    arr.append({'school': '清华大学', 'institution': '材料学院', 'school_address': '北京市海淀区双清路30号',
                'institution_address': '北京市海淀区双清路30号清华园清华大学'})
    arr.append({'school': '复旦大学', 'institution': '材料科学系', 'school_address': '上海市杨浦区邯郸路220号',
                'institution_address': '邯郸路220号复旦大学邯郸校区'})

    return json.dumps(arr)


@api_blueprint.route('/institution/introduction')
def institution_introduction():
    """
    根据学校名school和学院名institution来获取该学院的相关信息
    :return:json格式数据
    """
    # 获取传递的参数
    school_name = request.args.get('school')
    institution_name = request.args.get('institution')
    # 获取相关信息

    return "学院信息"


@api_blueprint.route('/institution/relation')
def institution_relation():
    """
    访问: /api/institution/relation?school=东南大学&institution=计算机科学与工程学院
    获取该学校和院系下的所有老师的联系，并生成echart可用的数据格式，json
    :return: json格式的数据
    """
    # 获取传递的参数
    school_name = request.args.get('school')
    institution_name = request.args.get('institution')
    # 获取该学院和院系对应的所有老师
    teachers = school_service.getTeachers(school_name, institution_name)
    # 预处理
    teacher_id_set = set()
    for teacher in teachers:
        teacher_id_set.add(teacher['ID'])
    # 学术头衔
    academic_titles = teacher_service.getAcademicTitlesByIds(teacher_id_set)
    # 获取老师的联系
    relations = teacher_service.getRelationsByIds(teacher_id_set)
    # 转换成json格式并返回
    data = utils.handleRelations(teachers, relations, academic_titles)
    return json.dumps(data)


@api_blueprint.route('/person/introduction/<int:teacher_id>')
def person_introduction(teacher_id):
    pass


@api_blueprint.route('/person/relation/<int:teacher_id>')
def person_relation(teacher_id):
    # 获取该老师的所有关系
    relations = teacher_service.getRelationById(teacher_id)
    teacher_id_set = set()
    # 获取与之对应的所有的老师的id
    for relation in relations:
        teacher_id_set.add(relation['teacher2_id'])
    # 获取所有老师
    teachers = teacher_service.getTeachersByIds(teacher_id_set)
    # 获取荣誉
    for teacher in teachers:
        teacher_id_set.add(teacher['ID'])
    academic_titles = teacher_service.getAcademicTitlesByIds(teacher_id_set)
    # 获取echarts需要的结构转换成json格式并返回
    data = utils.handleRelations(teachers, relations, academic_titles)
    return json.dumps(data)
