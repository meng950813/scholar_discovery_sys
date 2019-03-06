"""
author: xiaoniu
date: 2019-03-05
desc: 主要用在SchoolService类中，简单封装了和数据库的交互的SQL语句
"""


import dao.db as db


class SchoolDao:
    def getTeachers(self, *params):
        """
        获取学校或者(学校,学院)下的所有老师
        :param params: school_id 或者(school_id, institution_id) 前者获取该学校的所有老师，后者则获取该学校下院系的所有老师
        :return:list[dict] 字典的格式详见es_teacher
        """
        if len(params) == 1:
            sql = 'select * from es_teacher where SCHOOL_ID = ?'
        else:
            sql = 'select * from es_teacher where SCHOOL_ID = ? and INSTITUTION_ID=?'

        results = db.select(sql, *params)
        return results

    def getIdByName(self, *params):
        """
        通过学校名或者(学校名,学院名)获取学校id或者(学校id,学院id)
        :param params:学校名 或者(学校名,学院名)
        :return:如果是学校名，则返回学校名的id；如果是(学校名,学院名)则获取的是(学校id,学院id)
        """
        institution_id = None

        if len(params) == 1:
            sql = 'select SCHOOL_ID from es_institution where SCHOOL_NAME=?'
            result = db.select_one(sql, *params)
        else:
            sql = 'select SCHOOL_ID,ID from es_institution where SCHOOL_NAME=? and NAME=?'
            result = db.select_one(sql, *params)
            institution_id = result['ID']

        school_id = result['SCHOOL_ID']
        return school_id, institution_id


school_dao = SchoolDao()