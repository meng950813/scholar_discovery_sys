"""
author: xiaoniu
date: 2019-03-18
desc: 主要用在TeacherService类中，简单封装了和数据库的交互的SQL语句
"""
import utils.db as db


class TeacherDao:
    def get_relations_by_ids(self, id_list):
        """
        获取老师id对应的所有有联系的老师id
        :param id_list: 老师id数组
        :return: 所有和该老师有联系的数组
        """
        string = 'select * from teacher_teacher where teacher1_id in (%s)'
        sql = string % (','.join(['?' for id in id_list]))
        results = db.select(sql, *id_list)

        return results


    def get_teachers_by_ids(self, id_list):
        """
        根据老师id数组获取所有的老师
        :param id_list: 老师id所组成的数组
        :return:
        """
        string = 'select * from es_teacher where ID in (%s)'
        sql = string % (','.join(['?' for id in id_list]))

        results = db.select(sql, *id_list)
        return results

    def get_academic_titles_by_ids(self, id_list):
        """
        根据老师id数组获取存在的头衔
        :param id_list: 老师id所组成的数组
        :return:返回存在的老师头衔数组
        """
        string = "select * from es_honor where TYPE='学术头衔' and TEACHER_ID IN (%s)"
        sql = string % (','.join(['?' for id in id_list]))

        results = db.select(sql, *id_list)
        return results

    def get_total_academic_titles(self):
        """
        获取所有的学术头衔
        :return: 学术头衔数组
        """
        sql = "select HONOR from es_honor where TYPE ='学术头衔' group by HONOR"
        results = db.select(sql)

        return results




teacher_dao = TeacherDao()


if __name__ == '__main__':
    import utils.db as db
    from config import DB_CONFIG
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine(**DB_CONFIG)
    # 获取该老师的所有关系
    self_relations = teacher_dao.get_relations_by_id(150896)
    print(self_relations)
    # 获取teacher2_id的所有id
    teacher_ids = [relation['teacher2_id'] for relation in self_relations]
    # 获取老师相关信息
    teacher_list = teacher_dao.get_teachers_by_ids(teacher_ids)
    print('老师信息')
    print(teacher_list)
    # 获取老师对应的存在的学术头衔
    academic_titles = teacher_dao.get_academic_titles_by_ids(teacher_ids)
    print(academic_titles)
    # 获取所有学术头衔
    total_categories = teacher_dao.get_total_academic_titles()
    print(total_categories)

