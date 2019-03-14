from search_module.algorithm.base import dbs


def create_teacher_discipline():
    sql = "select ID, INSTITUTION_ID from es_teacher"
    data = dbs.getDics(sql)
    # print(type(data))
    teacher_institution = {}
    for l in data:
        teacher_id = l["ID"]
        institution_id = l["INSTITUTION_ID"]
        teacher_institution[teacher_id] = institution_id


    sql2 = "select INSTITUTION_ID, DISCIPLINE_CODE from es_relation_in_dis"
    data2 = dbs.getDics(sql2)
    institution_discipline = {}
    for l in data2:
        institution_id = l["INSTITUTION_ID"]
        discipline_id = l["DISCIPLINE_CODE"]

        if institution_discipline.__contains__(institution_id) == False:
            institution_discipline[institution_id] = discipline_id

    # print(teacher_institution)
    # print(institution_discipline)
    teacher_discipline = {}
    count = 0
    res = ""
    for teacher_id in teacher_institution:
        institution_id = teacher_institution[teacher_id]
        if institution_discipline.__contains__(institution_id):
            discipline_id = institution_discipline[institution_id]
        else:
            continue
        # print(teacher_id, "  ", discipline_id)
        teacher_discipline[teacher_id] = discipline_id
        count += 1
        res += "(" + str(teacher_id) + "," + str(institution_id) + "," + "\'" +str(discipline_id) + "\'" + "), "
        if count >= 3000:
            sql = "insert into teacher_discipline(teacher_id, institution_id, discipline_id)values"
            res = res[0: len(res)-2]
            sql += res
            print(sql)
            res = ""
            count = 0
            dbs.exe_sql(sql)
    sql = "insert into teacher_discipline(teacher_id, institution_id, discipline_id) values"
    res = res[0: len(res) - 2]
    sql += res
    dbs.exe_sql(sql)
if __name__ == '__main__':
    create_teacher_discipline()