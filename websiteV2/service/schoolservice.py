"""
SchoolService
author: xiaoniu
date: 2019-03-14
desc: 内部调用了SchoolDao的函数，并提供了python下易用的函数
"""
from dao.schooldao import school_dao


class SchoolService:
    def get_position_by_names(self, school_names):
        """
        根据学校名获取到学校名对应的经纬度，并返回
        :param school_names: 学校名数组
        :return: schools['name'] = {'longitude': 100, 'latitude': 100}
        """
        if school_names is None or len(school_names) == 0:
            return None
        results = school_dao.get_position_by_names(school_names)
        schools = {}
        for result in results:
            name = result['SCHOOL_NAME']
            position = result['POSITION']

            # 切割出经纬度
            arr = position.split(',')
            schools[name] = {'longitude': float(arr[0]), 'latitude': float(arr[1])}

        return schools


school_service = SchoolService()


if __name__ == '__main__':
    import utils.db as db
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine('root', '9527', 'training')

    print(school_service.get_position_by_names(['清华大学', '北京大学']))
