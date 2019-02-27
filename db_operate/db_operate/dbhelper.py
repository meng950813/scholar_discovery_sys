import pymysql.cursors

class DBhelper(object):
    # 数据库连接配置
    # mysql = MYSQL("localhost", "root", "coke", "project2")
    connect = pymysql.connect(
        host = '127.0.0.1',  # 数据库地址
        port = 3306,  # 数据库端口
        db = 'project2',  # 数据库名
        user = 'root',  # 数据库用户名
        passwd = 'coke',  # 数据库密码
        charset = 'utf8',  # 编码方式
        use_unicode = True
    )

    # 通过cursor执行增删查改
    cursor = connect.cursor()
    
    @classmethod
    def execute(cls,sql,errorMsg="has error"):
        try:
            # 执行 sql 语句
            cls.cursor.execute(sql)

            """
                data type : ((a1,b1,..),(a2,...),...)
            """
            data = cls.cursor.fetchall()

            # 提交 sql 语句
            cls.connect.commit()
            
            return data

        except Exception as e:
            print(errorMsg,e)
            with open("error.log","a") as f:
                f.write(sql[:50] + "    " + str(e))
                f.write("\r\n")
            return False
