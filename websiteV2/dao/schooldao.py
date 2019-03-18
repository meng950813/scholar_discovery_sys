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
        str = 'select SCHOOL_NAME,POSITION from es_institution where SCHOOL_NAME IN(%s) and POSITION is not null group by SCHOOL_NAME'
        sql = str % (','.join(['?' for name in school_names]))
        # 调用语句
        results = db.select(sql, *school_names)
        return results


school_dao = SchoolDao()


if __name__ == '__main__':
    import utils.db as db
    from config import DB_CONFIG
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine(DB_CONFIG['user'], DB_CONFIG['pwd'], DB_CONFIG['db_name'])

    print(school_dao.get_position_by_names(['清华大学', '北京大学']))

