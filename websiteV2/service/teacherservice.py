"""
author: xiaoniu
date: 2019-03-18
desc: 主要用在TeacherService类中，简单封装了和数据库的交互的SQL语句
"""
import utils
from dao.teacherdao import teacher_dao


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

    def get_teachers_by_ids(self, id_list):
        """
        根据老师id数组获取所有的老师
        :param id_list: 老师id所组成的数组
        :return:
        """
        results = teacher_dao.get_teachers_by_ids(id_list)
        # 转换成键值对的形式
        teachers = {}
        for result in results:
            teacher_id = result['ID']
            result.pop('ID')
            # 设置title
            result['TITLE'] = result['TITLE'] if (result['TITLE'] is not None and len(result['TITLE']) > 0) else '未知'
            teachers[teacher_id] = result
        return teachers

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


teacher_service = TeacherService()


if __name__ == '__main__':
    import utils.db as db
    from config import DB_CONFIG
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine(**DB_CONFIG)
    # 获取该老师的所有联系
    self_relations = teacher_service.get_relations_by_ids(150896)
    print(self_relations)
    # 获取teacher2_id的所有id
    teacher_ids = [relation['teacher2_id'] for relation in self_relations]
    # 获取所有老师相关信息
    teacher_list = teacher_service.get_teachers_by_ids(teacher_ids)
    print(teacher_list)

    print(teacher_service.get_total_academic_titles())
