import pymysql

from pymysqlpool.pool import Pool

class sql():
    def __init__(self,host,user,pwd,db_name,port=None):
        self.db = pymysql.connect(host=host,user=user,password=pwd,database=db_name,port=port)
        self.cursor = self.db.cursor()
        #self.cursor.execute("SELECT VERSION()")

    def search(self,sql_condition,search_type=None):
            self.cursor.execute(sql_condition)
            if search_type == None or search_type == 'one':
                results = self.cursor.fetchone()
                ###print("results001_是",results)
                return results[0]
            elif search_type == 'all':
                results = self.cursor.fetchall()
                return results
            elif search_type == "del":
                try:
                    #self.cursor.execute(sql)
                    self.db.commit()
                except:
                    print("删除出错")
                    self.db.rollback()
            else:
                ###print("格式填写错误")
                return False

    def updata(self, sql_condition):
        self.cursor.execute(sql_condition)
        self.db.commit()


class sql_thread():
    def __init__(self,host,user,password,db,port=3306):
        '''

        :param host: host
        :param user: 用户名
        :param password: 密码
        :param db: 数据库名
        :param port: 端口
        '''
        self.pool = Pool(host=host, port=port, user=user, password=password, db=db, autocommit=True) #autocommit 为自动commit模式
        self.pool.init()
        self.connection = self.pool.get_conn()
        self.cursor = self.connection.cursor()


    def search(self,sql_condition,search_type=None):
        '''
        :param sql_condition: sql语句
        :param search_type: 搜索类型,one:搜索只定的一个;all:搜索全部
        :return:查询结果。one:字典,all:列表
        查询
        '''
        self.cursor.execute(sql_condition)
        if search_type == None or search_type == 'one':
            results = self.cursor.fetchone()
            ###print("results001_是",results)
            return results
        elif search_type == 'all':
            results = self.cursor.fetchall()
            return results
        else:
            ###print("格式填写错误")
            return False

    def updata(self, sql_condition):
        '''
        :param sql_condition: sql语句
        :return:
        上传sql语句：增加，删除，修改
        '''
        #自动commit模式
        self.cursor.execute(sql_condition)


    # 释放连接
    def release_connection(self):
        self.pool.release(self.connection)


