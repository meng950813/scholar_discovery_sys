from search_module.algorithm.base import dbs

def get_lab_info():
    lab_info = dbs.getDics("select id, org, institution from national_key_lab")
    lab_dict = {}

    for i in lab_info:
        lab_id = i['id']
        lab_school = i['org']
        lab_institution = i['institution']
        lab_dict[(lab_school, lab_institution)] = lab_id
    # print(lab_dict)
    return lab_dict

def get_institution_info(lab_dict):
    institution_info = dbs.getDics("select id, school_name, `name` from es_institution")

    institution_dict = {}

    for i in institution_info:
        institution_id = i['id']
        institution_school = i['school_name']
        institution_name = i['name']
        institution_dict[(institution_school, institution_name)] = institution_id
    print(institution_dict)
    count = 0
    sql = "insert into institution_lab(institution_id, lab_id)values "
    res = ""
    for lab_tup in lab_dict:
        for school_insti in institution_dict:
            if lab_tup[0] == school_insti[0]:
                institution_name = school_insti[1]
                if institution_name[len(institution_name)-2: ] == "学院":
                    institution_name = institution_name[0:len(institution_name)-2]
                if institution_name in lab_tup[1]:
                    res += "(" + str(institution_dict[school_insti]) + "," + str(lab_dict[lab_tup]) + "),"
                    count += 1
    res = res[0: len(res)-1]
    sql += res
    print(sql)
    dbs.exe_sql(sql)
    print(count)

if __name__ == '__main__':
    lab_dict = get_lab_info()
    get_institution_info(lab_dict)