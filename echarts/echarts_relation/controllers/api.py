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


@api_blueprint.route('/institution/address', methods=['POST'])
def institution_address():
    """
    根据关键字和关键字id获取满足条件的学校 学院和学院的位置
    :return: {school: [], college: [}
    """
    keyword = request.form.get('keyword')
    keyword_id = request.form.get('keyword_id')
    # 获取相应的学校和学院
    schools, colleges = school_service.getSchoolsByKeyword(keyword)

    return json.dumps({
        'school': schools,
        'college': colleges
    })


@api_blueprint.route('/institution/introduction', methods=['POST'])
def institution_introduction():
    """
    根据学校名school和学院名institution来获取该学院的相关信息
    :return:json格式数据
    """
    # 获取传递的参数
    school_name = request.form.get('school', type=str)
    institution_name = request.form.get('institution')
    # 获取相关信息

    return "学院信息"


@api_blueprint.route('/institution/relation', methods=['POST'])
def institution_relation():
    """
    访问: /api/institution/relation?school=东南大学&institution=计算机科学与工程学院
    获取该学校和院系下的所有老师的联系，并生成echart可用的数据格式，json
    :return: json格式的数据
    """
    # 获取传递的参数
    school_name = request.form.get('school')
    institution_name = request.form.get('institution')
    # 获取该学院和院系对应的所有老师
    teachers = school_service.getTeachersBySchool(school_name, institution_name)
    # 老师对应的学术头衔
    academic_titles = teacher_service.getAcademicTitlesByIds(teachers.keys())
    # 总的学术头衔类别
    total_categories = teacher_service.getCategoriesOfAcademicTitles()
    total_categories.insert(0, '副教授')
    total_categories.insert(0, '教授')
    total_categories.insert(0, '未知')
    # 获取老师的联系
    relations = teacher_service.getRelationsByIds(teachers.keys())
    # 转换成json格式并返回
    data = utils.handleRelations(teachers, relations, academic_titles, total_categories)
    # 设置名称
    data['title'] = school_name + '-' + institution_name
    return json.dumps(data)


@api_blueprint.route('/person/introduction', methods=['POST'])
def person_introduction():
    teacher_id = request.form.get('teacher_id', type=int)
    pass


@api_blueprint.route('/person/relation', methods=['POST'])
def person_relation():
    teacher_id = request.form.get('teacher_id', type=int)
    # 获取该老师的所有关系
    relations = teacher_service.getRelationById(teacher_id)
    teacher_id_set = set()
    # 获取与之对应的所有的老师的id
    for relation in relations:
        teacher_id_set.add(relation['teacher2_id'])
    teacher_id_set.add(teacher_id)
    # 获取所有老师
    teachers = teacher_service.getTeachersByIds(teacher_id_set)
    # 获取荣誉
    academic_titles = teacher_service.getAcademicTitlesByIds(teacher_id_set)
    # 总的学术头衔类别
    total_categories = teacher_service.getCategoriesOfAcademicTitles()
    total_categories.insert(0, '副教授')
    total_categories.insert(0, '教授')
    total_categories.insert(0, '未知')
    # 获取echarts需要的结构转换成json格式并返回
    data = utils.handleRelations(teachers, relations, academic_titles, total_categories)
    return json.dumps(data)
