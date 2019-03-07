"""
TeacherDao
author: xiaoniu
date: 2019-03-05
desc: 主要用在TeacherService类中，简单封装了和数据库的交互的SQL语句
"""
import utils.db as db


class TeacherDao:

    def getRelationsById(self, teacher_id):
        """
        根据老师id获取该老师所有的关系
        :param teacher_id: 老师id
        :return:老师对应的所有关系 dict
        """
        sql = 'select * from teacher_teacher where teacher1_id=?'
        results = db.select(sql, teacher_id)

        return results

    def getRelationsByIds(self, teacher_ids_str):
        """
        根据老师id列表来获取老师们的所有关系
        :param teacher_ids_str: 老师们的id 类型为str 格式如(1,2,3)
        :return:老师列表的所有关系
        """
        sql = 'select * from teacher_teacher where teacher1_id in ' + teacher_ids_str
        results = db.select(sql)
        return results

    def getTeachersByIds(self, teacher_ids_str):
        """
        根据老师id列表获取老师的所有信息
        :param teacher_ids_str:老师们的id 类型为str 格式如(1,2,3)
        :return:老师的具体信息 格式如es_teacher
        """
        sql = 'select * from es_teacher where ID in ' + teacher_ids_str
        results = db.select(sql)
        return results

    def getAcademicTitlesByIds(self, teacher_ids_str):
        """
        获取老师id类别的学术头衔
        :param teacher_ids_str: 老师们的id 类型为str 格式如(1,2,3)
        :return: 返回存在的老师头衔数组
        """
        sql = "select * from es_honor where TYPE ='学术头衔' and TEACHER_ID in " + teacher_ids_str
        results = db.select(sql)
        return results

    def getCategoriesOfAcademicTitles(self):
        """
        从数据库中获取学术头衔的类别并返回
        :return: 学术头衔名称数组
        """
        sql = "select HONOR from es_honor where TYPE ='学术头衔' group by HONOR"
        results = db.select(sql)

        return results


teacher_dao = TeacherDao()
