"""
TeacherDao
author: xiaoniu
date: 2019-03-05
desc: 主要用在TeacherService类中，简单封装了和数据库的交互的SQL语句
"""


import dao.db as db


class TeacherDao:

    def getRelationsById(self, teacher_id):
        """
        根据老师的id获取该老师的所有的关系
        :param teacher_id: 老师id
        :return:老师对应的所有关系 dict
        """
        sql = 'select * from teacher_teacher where teacher1_id=?'
        results = db.select(sql, teacher_id)

        return results

    def getRelationsByIds(self, ids):
        """
        从数据库中获取在ids列表中的的所有关系
        :param ids: 老师的id列表 类型为str 格式如(1,2,3)
        :return:老师列表的所有关系
        """
        sql = 'select * from teacher_teacher where teacher1_id in ' + ids
        results = db.select(sql)
        return results

    def getTeachersByIds(self, ids):
        sql = 'select * from es_teacher where ID in ' + ids
        results = db.select(sql)
        return results

    def getAcademicTitlesByIds(self, ids):
        """
        获取老师的学术头衔
        :param ids:
        :return:
        """
        sql = "select * from es_honor where TYPE ='学术头衔' and TEACHER_ID in " + ids
        results = db.select(sql)
        return results


teacher_dao = TeacherDao()
