from db_operate.dbhelper import DBhelper

def get_academican_without_school():
    '''
    获取院士表中没有学校或者teacher_id的院士的id和name，组成字典返回
    :return:
    '''
    data = DBhelper.execute("SELECT name,id from eval_yuanshi where school is NULL or teacher_id_list is NULL")
    id_name_dict = {}
    for name_id in data:
        id = name_id[1]
        name = name_id[0]
        id_name_dict[id] = name
    return id_name_dict
    # print(id_name_dict)

def get_teacher_info():
    '''
    获取教师的name, id, school
    :return: teacher_dict {name:[(id,school),...],}
    '''
    teacher_dict = {}
    data = DBhelper.execute("select ID, NAME, school_id from es_teacher")
    for t in data:
        id = t[0]
        name = t[1]
        school_id = t[2]

        if teacher_dict.__contains__(name):
            teacher_dict[name].append((id, school_id))
        else:
            teacher_dict[name] = [(id, school_id)]
    return teacher_dict
    # print(teacher_dict)

def get_school_info():
    '''
    获取学校中的id与名字，返回
    :return:{id:name,  ...}
    '''
    data = DBhelper.execute("SELECT ID, NAME from es_school")
    school_dict = {}
    for t in data:
        school_id = t[0]
        school_name = t[1]
        school_dict[school_id] = school_name
    return school_dict
    # print(school_dict)

def update_yuanshi(id_name_dict, school_dict, teacher_dict):
    '''
    从参数id_name_dict中获取缺少相关信息的院士的名字，在教师表中进行匹配，得到所缺失的信息，然后对院士表的相关字段进行更新。
    :param id_name_dict:
    :return:
    '''
    for id in id_name_dict.keys():
        name = id_name_dict[id] #获取缺少学校或teacher_id的院士名字
        if teacher_dict.__contains__(name):
            teacher_info_list = teacher_dict[name]
        else:
            continue
        # teacher_info_tup = ()
        if teacher_info_list is []:
            continue
        else:
            teacher_info_tup = teacher_info_list[0]
        teacher_id = teacher_info_tup[0]
        school_id = teacher_info_tup[1]
        if school_dict.__contains__(school_id):
            school_name = school_dict[school_id]
        else:
            continue

        s1 = "teacher_id_list = %s"% str(teacher_id) + ","
        s2 = "school = \"%s\""% (school_name) + " where id = %s"% (id)
        sql = "UPDATE eval_yuanshi set " + s1 + s2
        print(sql)
        DBhelper.execute(sql)
        # print("---", teacher_id, "   ", school_name)
if __name__ == '__main__':
    id_name_dict = get_academican_without_school()
    # print(id_name_dict)
    teacher_dict = get_teacher_info()
    # print(teacher_dict)
    school_dict = get_school_info()
    # print(school_dict)
    #
    update_yuanshi(id_name_dict, school_dict, teacher_dict)