import logging
import db


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine('root', '9527', 'training')
    # 学校和对应的id
    school_id_mapping = {}
    # 语句
    sql_mapping = {}
    results = db.select('select school, school_id from discipline_school')
    for result in results:
        school_id_mapping[result.get('school_id')] = result['school']

    # 荣誉字段映射
    honor_fields = [
        {'table_name': 'eval_jiechu', 'name': 'name', 'school': 'school_name'},
        {'table_name': 'eval_yuanshi', 'name': 'name', 'school': 'school'},
        {'table_name': 'eval_changjiang', 'name': 'name', 'school': 'school'}
    ]
    teacher_fields = [
        {'table_name': 'es_teacher', 'name': 'NAME', 'school_id': 'SCHOOL_ID', 'id': 'ID'},
        {'table_name': 'teacher', 'name': 'name', 'school_id': 'school_id', 'id': 'id'}
    ]
    #
    sql = """select * from {teacher_tablename},{table_name} 
        where {table_name}.teacher_id_list is null and
         {teacher_tablename}.{teacher_name} = {table_name}.{name} and
          {teacher_tablename}.{school_id} = ? and {table_name}.{school} = ?"""

    with db.connection():
        for teacher_field in teacher_fields:
            for field in honor_fields:
                for school_id, school_name in school_id_mapping.items():
                    if school_id is None or school_name is None:
                        continue

                    results = db.with_select( \
                        sql.format(table_name=field['table_name'], name=field['name'], school=field['school'],\
                                   teacher_tablename=teacher_field['table_name'], teacher_name=teacher_field['name'], school_id=teacher_field['school_id']),\
                        school_id, school_name)
                    # 对查询结果进行处理
                    for result in results:
                        teacher_name = result[teacher_field['name']]
                        teacher_id = result[teacher_field['id']]
                        key = (teacher_name, school_name)

                        if teacher_id == 158465:
                            pass

                        if key not in sql_mapping:
                            sql_mapping[key] = {}
                            mapping = sql_mapping[key]
                            mapping['id_list'] = []
                        else:
                            # 已经存在对应的键,表示es_teacher已经有了对应的数据，此时直接跳过本次循环
                            if teacher_field == 'teacher':
                                continue
                            mapping = sql_mapping[key]
                        mapping['table_name'] = field['table_name']
                        mapping['id_list'].append(teacher_id)
                        mapping['honor_id'] = result['id']
                        # 判断是更新还是先插入后更新
                        if teacher_field == teacher_fields[0]:
                            mapping['type'] = 'update'
                        elif teacher_field == teacher_fields[1]:
                            mapping['type'] = 'insert'
                            mapping.update(result)
    # 获取到当前最大id
    result = db.select_one('select * from es_teacher order by id desc limit 1')
    max_id = result['ID']
    # 根据学校和学院获取学院的ID
    institutions = db.select('select ID,SCHOOL_NAME,NAME from es_institution;')

    with open('honor.sql', 'w', encoding='utf-8') as fp:
        for k, data in sql_mapping.items():
            sql_type = data['type']

            if sql_type == 'update':
                sentence = "update %s set teacher_id_list='%s' where id = %s;\n" \
                    % (data['table_name'], ','.join([ str(x) for x in data['id_list']]), data['honor_id'])

                fp.write(sentence)
            elif sql_type == 'insert':
                # 获取学院的id
                for institution in institutions:
                    if institution['SCHOOL_NAME'] == k[1] and institution['NAME'] == data['institution']:
                        institution_id = institution['ID']
                max_id += 1
                # 对值进行预处理
                for key in ['name', 'title', 'eduexp', 'email', 'pic', 'homepage']:
                    data[key] = 'null' if data[key] is None else ("'%s'" % data[key])

                sentence1 = """insert into es_teacher(ID,NAME,TITLE,SCHOOL_ID, INSTITUTION_ID, EDUEXP,EMAIL,PIC,HOMEPAGE) values(%d,%s,%s, %d, %d,%s,%s,%s,%s);\n""" \
                            % (max_id, data['name'], data['title'], data['school_id'], institution_id, data['eduexp'], data['email'], data['pic'], data['homepage'])
                sentence2 = 'update %s set teacher_id_list=%s where id = %s;\n' \
                           % (data['table_name'], str(max_id), data['honor_id'])
                fp.write(sentence1)
                fp.write(sentence2)



