from  base import dbs

# sql="SELECT * from main_lab where name like '%、%'"
# s_sql="SELECT * from main_lab where name=%s and org=%s"
# r=dbs.getDics(sql)
# for t in r:
#     index=t["name"].find("（")
#     school=t["name"][index+1:-1].split("、")
#     for s in school:
#         tmp=dbs.getDics(s_sql,(t["name"],s))
#         if len(tmp)==0:
#             item={"table":"main_lab","params":{"name":t["name"],"org":s}}
#             print(item)
            # dbs.insertItem(item)

sql="SELECT a.id,count(*) as num FROM teacher a join main_lab b on a.school=b.org and a.institution=b.institution GROUP BY a.id "
r=dbs.getDics(sql)
u_sql="update `teacher_rank` set mian_lab=%s where teacher_id=%s"

for t in r:
    dbs.exe_sql(u_sql,(t["num"],t["id"]))
