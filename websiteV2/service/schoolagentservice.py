"""
author: xiaoniu
date: 2019-03-22
desc: 内部调用了SchoolDao
"""
import utils
import datetime
from dao.schoolagentdao import school_agent_dao


class SchoolAgentService:

    def get_relations_by_id(self, uid):
        """
        获取id数组对应的所有有联系的人
        :param uid: 商务的id
        :return: 已经按照学校名和学院名聚合的字典
        """
        results = school_agent_dao.get_relations_by_id(uid)
        # 按照学校和学院进行分类
        for result in results:
            result['CREATION_TIME'] = result['CREATION_TIME'].strftime('%Y/%m/%d')
        return results


school_agent_service = SchoolAgentService()


if __name__ == '__main__':
    import utils.db as db
    from config import DB_CONFIG
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine(**DB_CONFIG)

    output = school_agent_service.get_relations_by_id(100000)
    for school_name, school in output.items():
        print(school_name)
        for college_name, teachers in school.items():
            print(college_name)
            for teacher in teachers:
                print(teacher)
