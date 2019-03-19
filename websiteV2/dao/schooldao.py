"""
author: xiaoniu
date: 2019-03-14
desc: 主要用在SchoolService类中，简单封装了和数据库的交互的SQL语句
"""
import utils.db as db


class SchoolDao:

    def get_position_by_names(self, school_names):
        """
        根据学校名获取到学校名对应的经纬度，并返回
        :param school_names: 学校名数组
        :return: 学校名对应的经纬度
        """
        string = 'select SCHOOL_NAME,POSITION from es_institution where SCHOOL_NAME IN(%s) and POSITION is not null group by SCHOOL_NAME'
        sql = string % (','.join(['?' for name in school_names]))
        # 调用语句
        results = db.select(sql, *school_names)
        return results

    def get_teachers_by_school(self, school_id, institution_id=None):
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


school_dao = SchoolDao()


if __name__ == '__main__':
    import utils.db as db
    from config import DB_CONFIG
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine(**DB_CONFIG)

    print(school_dao.get_position_by_names(['清华大学', '北京大学']))
    print(school_dao.get_teachers_by_school(17134, 557))

