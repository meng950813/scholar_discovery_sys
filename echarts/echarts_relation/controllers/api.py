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
    # 获取院系简介
    text = """
    清华大学机械工程学科建设始于1932年，机械工程学科在国际上享有盛誉，连续多年在QS世界大学排名的机械学科中位列全球前20。
清华大学机械工程学院拥有一支杰出的人才队伍，其中包括院士13名、千人（含青千）28名、长江学者（含青年长江）23名、杰青/优青21名、万人计划人才2名。
学院现有多个国家和部委级科研和教学平台，包括5个国家重点实验室：电力系统及发电设备控制和仿真国家重点实验室、水沙科学与水利水电工程国家重点实验室、精密测试技术及仪器国家重点实验室（清华分室）、摩擦学国家重点实验室、汽车安全与节能国家重点实验室。 
2个国家工程实验室：工业锅炉及民用煤清洁燃烧国家工程研究中心、燃气轮机与煤气化联合循环国家工程研究中心。
另有导航技术工程中心、微米纳米技术研究中心、宇航技术研究中心、质谱仪器研究中心、海洋技术研究中心、清华大学-三菱重工业联合研发中心、清华大学-东芝能源与环境研究中心、清华大学燃烧能源研究中心、清华大学盐碱地区生态修复与固碳研究中心、北京市盐碱及荒漠化地区生态修复与固碳工程技术研究中心、汽车发展研究中心。
    """
    data = {'brief': text}
    return json.dumps(data)


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
