"""
author: xiaoniu
date: 2019-03-18
desc: 主要用在TeacherService类中，简单封装了和数据库的交互的SQL语句
"""
import utils
from dao.teacherdao import teacher_dao
import json
import time


class TeacherService:
    @staticmethod
    def get_relations_by_ids(id_list):
        """
        获取老师id对应的所有有联系的老师id
        :param id_list: 老师id数组 或单个id
        :return: array
        """
        if isinstance(id_list, int):
            id_list = [id_list]
        results = teacher_dao.get_relations_by_ids(id_list)
        return results

    def get_teachers_by_ids(self, id_list, keys=None):
        """
        根据老师id数组获取所有的老师
        :param id_list: 老师id所组成的数组
        :param keys: 要获得的键值数组 如['ID', 'NAME'] 为空则获取所有的键值对
        :return: 查询成功的结果数组
        """
        results = teacher_dao.get_teachers_by_ids(id_list, keys=keys)
        # 转换成键值对的形式
        teachers = {}
        for result in results:
            teacher_id = result['ID']
            result.pop('ID')
            # 设置title
            result['TITLE'] = result['TITLE'] if (result['TITLE'] is not None and len(result['TITLE']) > 0) else '未知'
            teachers[teacher_id] = result
        return teachers

    def get_teachers_grouping_institutions(self, id_list, keys=None, elimination=None):
        """
        根据老师的id数组获取老师并按学校和学院进行分组
        :param id_list: 老师的id数组
        :param keys: 要获取的键数组
        :param elimination: 过滤函数 返回True则过滤该老师
        :return: 以学校和学院划分好的老师信息
        """
        teachers = teacher_dao.get_teachers_by_ids(id_list, keys=keys)
        results = {}
        # 按照学校、学院对老师进行分组
        for teacher in teachers:
            school_id = teacher['SCHOOL_ID']
            institution_id = teacher['INSTITUTION_ID']
            # 学校
            if school_id not in results:
                results[school_id] = {}
            school = results[school_id]
            # 学院
            if institution_id not in school:
                school[institution_id] = {}
                school[institution_id]['teachers'] = []
            # 过滤老师
            if elimination is None or elimination(teacher) is False:
                teacher['YEAROLD'] = None
                self.normalization_teacher(teacher)
                school[institution_id]['teachers'].append(teacher)

        return results

    def get_academic_titles_by_ids(self, id_list):
        """
        根据老师id数组获取存在的头衔
        :param id_list: 老师id所组成的数组
        :return:返回存在的老师头衔数组
        """
        results = teacher_dao.get_academic_titles_by_ids(id_list)
        return results

    def get_total_academic_titles(self):
        """
        获取所有的学术头衔
        :return: 学术头衔数组
        """
        results = teacher_dao.get_total_academic_titles()
        total_titles = [result['HONOR'] for result in results]

        return total_titles

    def normalization_teacher(self, teacher):
        """
        对老师的信息进行标准化，如把出生日期转为年龄
        :param teacher: 老师的信息字典
        :return: 转换好的老师信息，和参数teacher相同
        """
        for key, value in teacher.items():
            # 转换领域
            if key == 'FIELDS' and value is not None:
                fields = value.replace("\'", "\"")
                teacher[key] = tuple(json.loads(fields).keys())
            elif key == 'BIRTHYEAR' and value is not None:
                teacher['YEAROLD'] = time.localtime(time.time()).tm_year - int(teacher['BIRTHYEAR'])
        return teacher



teacher_service = TeacherService()


if __name__ == '__main__':
    import utils.db as db
    from config import DB_CONFIG
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine(**DB_CONFIG)
    # 获取该老师的所有联系
    # self_relations = teacher_service.get_relations_by_ids(150896)
    # print(self_relations)
    # # 获取teacher2_id的所有id
    # teacher_ids = [relation['teacher2_id'] for relation in self_relations]
    # # 获取所有老师相关信息
    # teacher_list = teacher_service.get_teachers_by_ids(teacher_ids)
    # print(teacher_list)

    # print(teacher_service.get_total_academic_titles())
    id_arr = [159822, 159729, 159835, 159805, 159742, 159842, 159739, 159808, 159737, 159828, 99181, 99236, 99318, 99329, 99304, 99234, 99252, 99259]
    keys = ['ID', 'NAME', 'TITLE', 'SCHOOL_ID', 'INSTITUTION_ID', 'BIRTHYEAR', 'FIELDS', 'ACADEMICIAN', 'OUTYOUTH', 'CHANGJIANG']
    print(teacher_service.get_teachers_grouping_institutions(id_arr, keys, lambda t: t['FIELDS'] is None))
