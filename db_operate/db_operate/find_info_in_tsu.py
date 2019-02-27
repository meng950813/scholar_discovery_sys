from db_operate.dbhelper import DBhelper

'''
2019.2.28
从清华大学所有的学院里找出所有的理工科学院
by zs
'''

def get_tsu_institution_info():
    '''
    获取清华大学中的所有学院
    :return: [institution1, institution2,.....]
    '''
    data = DBhelper.execute("select ID from es_institution where school_name= \"清华大学\"")
    return list(data)

def institution_to_discipline(institution_id_list):
    '''
    1.获取学院id和学科id关系，组成字典{学科id：学院id，.....}
    2.通过传入的institution_id_list获得清华学院的id，并从1中找到对应的学科id，判断id是否为理工科，
    :param institution_id_list:
    :return:
    '''
    data = DBhelper.execute("select institution_id, discipline_code from es_relation_in_dis")
    in_dis_dict = {}
    for t in data:
        in_id = t[0]
        dis_code = t[1]
        in_dis_dict[in_id] = dis_code
    # print(in_dis_dict)
    c = 0
    for id in institution_id_list:
            id = id[0]
            # print(id)
            if in_dis_dict.__contains__(id):
                dis_id = in_dis_dict[id]
            else:
                continue
            # 判断id是否是理工科的
            if dis_id[0] == "0" and (dis_id[1] == "7" or dis_id[1] == "8"):
                print(id)
                c += 1
    print(c)
if __name__ == '__main__':
    institution_id_list = get_tsu_institution_info()
    print(institution_id_list)
    institution_to_discipline(institution_id_list)