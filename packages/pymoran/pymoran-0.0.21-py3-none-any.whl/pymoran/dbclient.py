import pymysql
from pymoran.strtool import StrClass


class MySQLClient:
    def __init__(self, dbdata: dict) -> None:
        '''
        初始化数据库连接
        :param dbdata(host 主机地址,user 用户名,password 密码,database 数据库,port 端口，默认3306)
        :return {bool} True/False
        '''
        # 打开数据库连接
        self.db = pymysql.connect(
            host=dbdata['host'],
            user=dbdata['user'],
            password=dbdata['password'],
            database=dbdata['database'],
            port=dbdata['port']
        )
        # 使用cursor()方法获取操作游标
        self.cursor = self.db.cursor()
        self.strclass=StrClass()

    def close(self):
        self.db.close()

    def insert(self, table: str, data: dict, close: bool = True):
        '''
        插入数据，插入的数据内容无需做特殊安全处理，方法内均进行了html转码保存数据
        :param table 表名
        :param data 需要插入的数据
        :param close 是否自动关闭数据库连接，默认True
        :return {bool} True/False
        '''
        result = False
        # 列
        col = []
        # 行
        row = []
        for d in data.keys():
            col.append(d)
            row.append('"'+self.strclass.html_escape(data[d])+'"')
        sql = 'INSERT INTO %s (%s) VALUES (%s)' % (
            table,
            ','.join(col),
            ','.join(row)
        )
        try:
            # 执行sql语句
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.db.commit()
            result = True
        except:
            # 如果发生错误则回滚
            self.db.rollback()
            result = False
        if close:
            self.close()
        return result

    def fetch(self, fields: list, table: str, query: str = '', orderby: dict = None, close: bool = True):
        '''
        查询数据，查询条件数据建议使用html_escape转码保证数据查询安全
        :param fields 要查询的字段名
        :param table 表名
        :param query 查询条件，默认为空
        :param orderby 排序，默认为空，例：{'sort':'desc'}
        :param close 是否自动关闭数据库连接，默认True
        :return {list} 如没有查询结果则返回None
        '''
        where_str = ''
        if query != '':
            where_str = 'WHERE %s' % query
        orderby_str = ''
        if orderby != None:
            orderby_arr = []
            for key in orderby.keys():
                orderby_arr.append('%s %s' % (key, orderby[key]))
            orderby_str = 'ORDER BY ' + ','.join(orderby_arr)
        sql = 'SELECT %s FROM %s %s %s' % (
            ','.join(fields),
            table,
            where_str,
            orderby_str
        )
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 获取所有记录列表
            results = self.cursor.fetchall()
        except:
            print("Error: unable to fetch data")
        # 关闭数据库连接
        if close:
            self.close()
        # 没有查询结果则返回None
        if len(results) == 0:
            return None
        # 转化查询结果为list
        res_data = []
        col_count = len(fields)
        for result in results:
            col_data = {}
            for col in range(col_count):
                col_data[fields[col]] = result[col]
            res_data.append(col_data)
        return res_data

    def fetch_count(self, table: str, query: str = '', close: bool = True):
        '''
        查询数据结果条数，查询条件数据建议使用html_escape转码保证数据查询安全
        :param table 表名
        :param query where后的查询条件，例：id=1 and name='张三'
        :param close 是否自动关闭数据库连接，默认True
        :return {list} 如没有查询结果则返回None
        '''
        where_str = ''
        if query != '':
            where_str = 'WHERE %s' % query
        sql = 'SELECT count(id) FROM %s %s' % (
            table,
            where_str
        )
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 获取所有记录列表
            results = self.cursor.fetchone()
        except:
            print("Error: unable to fetch data")
        # 关闭数据库连接
        if close:
            self.close()
        # 没有查询结果则返回None
        return results[0]

    def update(self, table: str, set: dict, query: str = '', close: bool = True):
        '''
        更新数据，查询条件数据建议使用html_escape转码保证数据查询安全
        :param table 表名
        :param set 需要修改的内容
        :param query 查询条件，默认为空
        :param close 是否自动关闭数据库连接，默认True
        :return {bool} True/False
        '''
        result = False
        where_str = ''
        if query != '':
            where_str = 'WHERE %s' % query
        set_list = []
        for key in set.keys():
            set_list.append(
                '%s="%s"' % (key, self.strclass.html_escape(set[key]))
            )
        sql = 'UPDATE %s SET %s %s' % (
            table,
            ','.join(set_list),
            where_str
        )
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.db.commit()
            result = True
        except:
            # 发生错误时回滚
            self.db.rollback()
            result = False
        # 关闭数据库连接
        if close:
            self.close()
        return result

    def delete(self, table: str, query: str = '', close: bool = True):
        '''
        删除数据，查询条件数据建议使用html_escape转码保证数据查询安全
        :param table 表名
        :param query 查询条件，默认为空
        :param close 是否自动关闭数据库连接，默认True
        :return {bool} True/False
        '''
        result = False
        where_str = ''
        if query != '':
            where_str = 'WHERE %s' % query
        sql = 'DELETE FROM %s %s' % (
            table,
            where_str
        )
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.db.commit()
            result = True
        except:
            # 发生错误时回滚
            self.db.rollback()
            result = False
        # 关闭数据库连接
        if close:
            self.close()
        return result


if __name__ == '__main__':
    pass
