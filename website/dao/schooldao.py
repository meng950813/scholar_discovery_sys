"""
author: xiaoniu
date: 2019-03-05
desc: 主要用在SchoolService类中，简单封装了和数据库的交互的SQL语句
"""
import utils.db as db


class SchoolDao:
    def getTeachers(self, school_id, institution_id=None):
        """
        获取学校id或者(学校id,学院id)下的所有老师
        :param school_id: 学校的id
        :param institution_id: 该学校对应的学院的id
        :return:list[dict] 字典的格式详见es_teacher
        """
        if institution_id is None:
            sql = 'select * from es_teacher where SCHOOL_ID = ?'
            results = db.select(sql, school_id)
        else:
            sql = 'select * from es_teacher where SCHOOL_ID = ? and INSTITUTION_ID=?'
            results = db.select(sql, school_id, institution_id)
        return results

    def getSchoolIdByName(self, school_name, institution_name=None):
        """
        通过学校名或者(学校名,学院名)获取学校id或者(学校id,学院id)
        :param school_name:学校名
        :param institution_name: 学院名
        :return:如果仅仅只有学校名，则返回学校对应的id；如果是(学校名,学院名)则获取的是(学校id,学院id)
        """
        institution_id = None

        if institution_name is None:
            sql = 'select SCHOOL_ID from es_institution where SCHOOL_NAME=?'
            result = db.select_one(sql, school_name)
        else:
            sql = 'select SCHOOL_ID,ID from es_institution where SCHOOL_NAME=? and NAME=?'
            result = db.select_one(sql, school_name, institution_name)
            institution_id = result['ID']

        school_id = result['SCHOOL_ID']
        return school_id, institution_id

    def getSchoolsByKeyword(self, keyword):
        """
        根据关键字找出匹配的学校
        TODO: 目前暂时未用到关键字
        :param keyword: 关键字
        :return: 匹配的学校列表
        """
        sql = 'select * from es_institution limit 0,20'
        results = db.select(sql)
        return results


school_dao = SchoolDao()


if __name__ == '__main__':
    import utils.db as db
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine('root', '9527', 'training')

    school_id, institution_id = school_dao.getSchoolIdByName('东南大学', '计算机科学与工程学院')
    print(school_id, institution_id)
    # 获取该院下的所有老师
    teachers = school_dao.getTeachers(school_id, institution_id)
    print(teachers)
