"""
filename: honor.py
date: 2019-03-02
version: 1.1
description: honor.py代码用于填充 eval_changjiang、eval_yuanshi、eval_jieqing中teacher_id_list 为null的项
流程如下：
令key = (老师名字，学校名字)，先遍历es_teacher，其中判断key是否存在于以上三个表中，如果存在，则保存该老师的id;
接着遍历teacher表，遍历teacher表要确保该老师的数据不在es_teacher表中，之后流程同上，运行完毕后应该导出honor.sql文件
"""
import logging
from utils import db

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine('root', '9527', 'training')
    # 学校和对应的id
    school_id_mapping = {}
    results = db.select('select NAME, ID from es_school')
    for result in results:
        school_id_mapping[result.get('ID')] = result['NAME']
    # 查询荣誉的三个表
    honors = {}
    # 荣誉表的sql
    sql_honors = {}
    # 保存es_teacher的键值对 用于与teacher作互斥
    es_teachers = set()
    # 荣誉字段映射
    honor_fields = [
        {'table_name': 'eval_jiechu', 'name': 'name', 'school': 'school_name'},
        {'table_name': 'eval_yuanshi', 'name': 'name', 'school': 'school'},
        {'table_name': 'eval_changjiang', 'name': 'name', 'school': 'school'}
    ]
    # 老师表
    teacher_fields = [
        {'table_name': 'es_teacher', 'name': 'NAME', 'school_id': 'SCHOOL_ID', 'id': 'ID'},
        {'table_name': 'teacher', 'name': 'name', 'school_id': 'school_id', 'id': 'id'}
    ]
    with db.connection():
        for field in honor_fields:
            results = db.with_select('select * from %s where teacher_id_list is null' % field['table_name'])
            honors[field['table_name']] = {}
            honor = honors[field['table_name']]
            for result in results:
                teacher_name = result[field['name']]
                school_name = result[field['school']]

                honor[(teacher_name, school_name)] = {'id': result['id']}
        # 读取es_teacher表
        for field in teacher_fields:
            teachers = db.with_select('select * from %s' % field['table_name'])

            for teacher in teachers:
                # 获取老师表的老师名称和学校名称
                teacher_id = teacher[field['id']]
                teacher_name = teacher[field['name']]

                if field['table_name'] == 'es_teacher':
                    school_id = teacher[field['school_id']]
                    school_name = school_id_mapping[school_id]

                    es_teachers.add((teacher_name, school_name))
                elif field['table_name'] == 'teacher':
                    school_name = teacher['school']

                key = (teacher_name, school_name)

                # 保证只用es_teacher中没有的数据来填充es_teacher
                if field['table_name'] == 'teacher' and key in es_teachers:
                    continue
                # 遍历荣誉表
                for honor_tablename,honor_list in honors.items():
                    # (老师和学校名) 在荣誉表中有对应，则需要添加相应的SQL语句
                    if key in honor_list:
                        if honor_tablename in sql_honors:
                            sql_honor_map = sql_honors[honor_tablename]
                        else:
                            sql_honors[honor_tablename] = {}
                            sql_honor_map = sql_honors[honor_tablename]

                        if key in sql_honor_map:
                            sql_honor = sql_honor_map[key]
                        else:
                            sql_honor_map[key] = {}
                            sql_honor = sql_honor_map[key]
                            # 获取荣誉表的id
                            sql_honor['honor_id'] = honor_list[key]['id']

                            if field['table_name'] == 'es_teacher':
                                sql_honor['id_list'] = []
                        # es_teacher 只需要update即可
                        if field['table_name'] == 'es_teacher':
                            sql_honor['type'] = 'update'
                            sql_honor['id_list'].append(teacher_id)
                        # teacher表则需要先插入然后再update
                        elif field['table_name'] == 'teacher':
                            sql_honor['type'] = 'insert'
                            sql_honor.update(teacher)

    # 获取到当前最大id
    result = db.select_one('select * from es_teacher order by id desc limit 1')
    max_id = result['ID']
    # 根据学校和学院获取学院的ID
    institutions = db.select('select ID,SCHOOL_NAME,NAME from es_institution;')

    fp = open('honor.sql', 'w', encoding='utf-8')

    count = 0
    # 逐个表进行写入
    for table_name,sql_honor_list in sql_honors.items():
        print('开始写入表',table_name)
        # 逐个项进行写入
        for key,data in sql_honor_list.items():
            count += 1
            if data['type'] == 'update':
                sentence = "update %s set teacher_id_list='%s' where id = %s;\n" \
                           % (table_name, ','.join([ str(x) for x in data['id_list']]), data['honor_id'])
                fp.write(sentence)
            elif data['type'] == 'insert':
                # 获取学院的id
                for institution in institutions:
                    if institution['SCHOOL_NAME'] == key[1] and institution['NAME'] == data['institution']:
                        institution_id = institution['ID']
                max_id += 1
                # 对值进行预处理
                for key in ['name', 'title', 'eduexp', 'email', 'pic', 'homepage']:
                    data[key] = 'null' if data[key] is None else ("'%s'" % data[key])

                sentence1 = """insert into es_teacher(ID,NAME,TITLE,SCHOOL_ID, INSTITUTION_ID, EDUEXP,EMAIL,PIC,HOMEPAGE) values(%d,%s,%s, %d, %d,%s,%s,%s,%s);\n""" \
                            % (max_id, data['name'], data['title'], data['school_id'], institution_id, data['eduexp'], data['email'], data['pic'], data['homepage'])
                sentence2 = 'update %s set teacher_id_list=%s where id = %s;\n' \
                            % (table_name, str(max_id), data['honor_id'])
                fp.write(sentence1)
                fp.write(sentence2)
        print(table_name, '表的SQL语句写入结束')

    print('update语句共', count)
    fp.close()
