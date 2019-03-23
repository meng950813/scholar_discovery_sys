"""
author: xiaoniu
date: 2019-03-18
desc: 主要用在SchoolAgentService类中，简单封装了和数据库的交互的SQL语句
学校商务DAO
"""
import utils.db as db


class SchoolAgentDao:

    def get_relations_by_id(self, uid):
        """
        获取id数组对应的所有有联系的人
        :param uid: 商务的id
        :return: 所有和该商务有联系的数组
        """
        sql = 'select * from sys_net_of_school_agent where U_ID = ?'
        results = db.select(sql, uid)

        return results


school_agent_dao = SchoolAgentDao()


if __name__ == '__main__':
    import utils.db as db
    from config import DB_CONFIG
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine(**DB_CONFIG)

    print(school_agent_dao.get_relations_by_id(100000))
