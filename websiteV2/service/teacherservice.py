"""
author: xiaoniu
date: 2019-03-18
desc: 主要用在TeacherService类中，简单封装了和数据库的交互的SQL语句
"""
from dao.teacherdao import teacher_dao
import json
import time


class TeacherService:

    def __init__(self):
        self.teacher_info_mapping = {
            'ID': 'id', 'NAME': 'name', 'FIELDS': 'fields', 'EMAIL': 'email'
        }

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
            teachers[teacher_id] = self.normalization_teacher(result)
        return teachers

    def get_teacher_info_by_id(self, teacher_id):
        keys = ['ID', 'NAME', 'TITLE', 'EMAIL', 'FIELDS', 'ACADEMICIAN', 'OUTYOUTH', 'CHANGJIANG']
        result = teacher_dao.get_teachers_by_ids([teacher_id], keys=keys)[0]
        info = self.normalization_teacher(result, False)
        return info

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

    def get_papers_by_id(self, teacher_id):
        """
        获取老师的所有论文数组
        :param teacher_id: 老师id
        :return: 论文信息数组
        """
        keys = ['name', 'org', 'year', 'cited_num', 'author']
        results = teacher_dao.get_papers_by_id(teacher_id, keys=keys)
        return results

    def normalization_teacher(self, teacher, isFieldList=True):
        """
        对老师的信息进行标准化，如把出生日期转为年龄
        :param teacher: 老师的信息字典
        :param isFieldList: 老师关键字是否只有值
        :return: 转换好的老师信息，和参数teacher相同
        """
        info = {}
        for key, value in teacher.items():
            trans_key = self.teacher_info_mapping.get(key, None)
            # 转换领域
            if key == 'FIELDS' and value is not None:
                fields = value.replace("\'", "\"")
                if isFieldList:
                    info[trans_key] = tuple(json.loads(fields).keys())
                else:
                    info[trans_key] = fields
            elif key == 'TITLE':
                info['title'] = value if (value is not None and len(value) > 0) else '未知'
            elif key == 'BIRTHYEAR' and value is not None:
                info['yearsold'] = time.localtime(time.time()).tm_year - int(teacher['BIRTHYEAR'])
            elif trans_key is not None:
                info[trans_key] = teacher[key]
            else:
                info[key] = teacher[key]

        return info


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
    tkeys = ['ID', 'NAME', 'TITLE', 'SCHOOL_ID', 'INSTITUTION_ID', 'BIRTHYEAR', 'FIELDS', 'ACADEMICIAN', 'OUTYOUTH', 'CHANGJIANG']
    print(teacher_service.get_teachers_grouping_institutions(id_arr, tkeys, lambda t: t['FIELDS'] is None))
    print(teacher_service.get_teacher_info_by_id(73932))
    print(teacher_service.get_papers_by_id(100874))
