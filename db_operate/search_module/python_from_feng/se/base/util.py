
#  author   ：feng
#  time     ：2018/1/25
#  function : 数据库抽象功能函数
import pymysql

from search_module.python_from_feng.se.base.config import POOL


class dbutil:
    def insertItem(self,item):
        #insert into student_info(stuName,stuAge) values('liutao',13)
        table=item["table"]+"("
        temp=",".join(["%s" for i in item["params"]])
        column=" values("+temp+")"
        paramList=[]
        columnList=[]
        for k in item["params"]:
            columnList.append(k)
            paramList.append(item["params"][k])
        params=tuple(paramList)
        sql="insert into "+table+ ",".join(columnList)+")"+column
        self.exe_sql(sql,params)

    def getDics(self, sql, params=None):
        conn = POOL.connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        if params is None:
            cursor.execute(sql)
        else :
            cursor.execute(sql, params)
        result = cursor.fetchall()
        conn.close()
        return result

    def getTuples(self,sql,params=None):
        conn = POOL.connection()
        cursor = conn.cursor()
        if params is None:
            cursor.execute(sql)
        else :
            cursor.execute(sql, params)
        result = cursor.fetchall()
        conn.close()
        return result

    def exe_sql(self,sql,params=None):
        conn = POOL.connection()
        cursor = conn.cursor()
        if params is None:
            r=cursor.execute(sql)
        else :
            r=cursor.execute(sql, params)
        conn.commit()
        conn.close()
        return r

    def exe_many(self, sql, li=None):
        conn = POOL.connection()
        cursor = conn.cursor()
        if li is None:
            r = cursor.execute(sql)
        else:
            r = cursor.executemany(sql, li)
        conn.commit()
        conn.close()
        return r
