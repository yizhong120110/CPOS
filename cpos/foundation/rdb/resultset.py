# -*- coding: utf-8 -*-

# 实现数据库连接池
# 提供独立于线程的数据库连接对象服务。保证在同一个线程中，一个数据库连接只能响应一次事件
"""
20110216 zhangj
    经过实测，informix在AIX下，若频繁创建关闭数据库连接（6000次左右），会导致数据库连接创建失败和内存异常。
    因此，针对此现象修正数据库连接池的操作规则：
    1 informix数据库连接不再直接关闭
    2 在con中增加计数器，初始值有USE_TIMES 设定（假定5000次）
      该值在con被请求一次时减一，当减为0时，连接被关闭
2011108  zhangj
    经过生产系统运行，发现，informix数据库在多线程间迁移会导致各类突发性异常
    因此，连接池操作规则修正为当发生数据库错误后，无论何种错误，均关闭数据库连接
"""
import re
import threading , _thread
from ..substrate.types.attrdict import AttrDict
from ..substrate.utils.functools import register
from ..substrate import traceback2
from ..conf.core import settings


def sql_rep_ocl(sql, params, pgtype):
    """
        # 为了将sql语句中的$$key进行替换，转为占位符
    """
    repdic = {'oracle':{ 'rsstr':r'\s*\$\$(\w*)\s*', 'joinstr':':%s_%s' },
              'postgresql':{ 'rsstr':r'\s*\$\$(\w*)\s*', 'joinstr':'%%(%s_%s)s' },
             }
    if not repdic.get(pgtype):
        raise Exception('错误的数据库类型', pgtype)
    # 对sql中的 $$key 做展开
    rslst = re.findall(repdic[pgtype]['rsstr'],sql)
    for key_lst in rslst:
        # 应该展开，但是不存在，提示
        if not params.get(key_lst):
            raise Exception('列表型参数没有赋值', key_lst)
        else:
            sql = sql.replace(' $$%s '%key_lst, " %s "%(','.join([repdic[pgtype]['joinstr']%(key_lst,key_id) for key_id in range(len(params[key_lst]))])))
    return sql


def open_dicval_list(param_dic):
    """
        # 下面这一段是为了将list型的参数展开，从而支持in操作
        # test({'hydm':'kf9001','jsdm':[1,2,3],'jgm':set(['33','32','31']),'jglx':('33','32','31')})
        # test({'hydm':'kf9001','jsdm':[1,2,3],'jsdm_1':'a'})
    """
    param_dic_new = {}
    for key_t ,val_t in param_dic.items():
        # 列表类型的，要展开一次
        if isinstance(val_t,(list,tuple,set)) and len(val_t) > 0:
            val_t_lst = list(val_t)
            for i_t in range(len(val_t_lst)):
                key_id = "%s_%s"%(key_t,i_t)
                if param_dic_new.get(key_id):
                    raise Exception('参数字典的键值名错误', key_id)
                else:
                    param_dic_new[key_id] = val_t_lst[i_t]
        else:
            # 非列表类型的直接复制，排除掉原列表类型，是为了避免参数过多导致sql报错
            if param_dic_new.get(key_t):
                raise Exception('参数字典的键值名错误', key_t)
            else:
                param_dic_new[key_t] = val_t
    return param_dic_new


if settings.USE_DB:
    settings.check('DB_CONSTR', 'DB_TYPE', msg='或设置USE_DB为False')
    if settings.DB_TYPE == 'informix':
        import informixdb as db2api
    elif settings.DB_TYPE == 'postgresql':
        import psycopg2 as db2api
    elif settings.DB_TYPE == 'oracle':
        import cx_Oracle as db2api
    elif settings.DB_TYPE == 'db2':
        import DB2 as db2api

class Dummy:
    pass
if db2api.threadsafety == 0:
    DB_POOL = Dummy()
else:
    DB_POOL = Dummy() # threading.local()
LOCKED = threading.local() # 用于标记线程是否已申请数据库
#thread_not_safe_lock = threading.Lock()
operator_lock = threading.Lock()


def get():
    global DB_POOL
    with operator_lock:
        if not hasattr( DB_POOL , 'lock' ):
            DB_POOL.lock = threading.Lock()

    if getattr( LOCKED , 'locked' , False ):
        # 在同一线程中是不应该重复请求连接的
        raise RuntimeError( "同一线程[%s]中不应该重复申请连接，代码有错误，请查找" % _thread.get_ident() )

    DB_POOL.lock.acquire() # 锁定当前请求，直到连接可用
    LOCKED.locked = True
    #if db2api.threadsafety == 0:
    #    thread_not_safe_lock.acquire()

    if getattr( DB_POOL , 'conn' , None ) is None:
        DB_POOL.conn = None
        DB_POOL.use_times = 0 # 为了避免创建数据库连接失败导致的put异常
        try:
            DB_POOL.conn = db2api.connect( **settings.DB_CONSTR )
            if settings.DB_TYPE == 'informix':
                # 仅需要在数据库连接创建时，执行一次
                DB_POOL.conn.sqltimeout = 20 * 1000  # 每个SQL的执行时间不应超过20秒钟，大于锁的时间
                cursor = DB_POOL.conn.cursor()
                cursor.execute( "SET LOCK MODE TO WAIT 10" ) # 锁定超过十秒，可以认为系统出问题了。避免数据库死锁导致全部交易暂停。
                cursor.execute( "SET ISOLATION TO REPEATABLE READ " )
            DB_POOL.use_times = settings.USE_TIMES or 10  # 若未设置，则按10次
        except:
            # 创建连接失败，应恢复线程状态
            traceback2.print_exc()
            put()
            raise
    DB_POOL.use_times -= 1
    return DB_POOL.conn

def put():
    global DB_POOL
    try:
        if DB_POOL.use_times <= 0: # 使用次数结束
            if DB_POOL.conn:
                try:
                    DB_POOL.conn.close()
                except:
                    pass  # 关闭不成功则丢弃
                DB_POOL.conn = None
    finally:
        LOCKED.locked = False
        #if db2api.threadsafety == 0:
        #    thread_not_safe_lock.release()
        DB_POOL.lock.release() # 释放线程级锁


class DBConnection(object):
    def __init__(self):
        self.con = get()
        self.cursors = []

    def cursor(self):
        #cursor = self.con.cursor()
        #self.cursors.append(cursor)
        #return cursor
        return self.cursors[0] if len(self.cursors) else self.con.cursor()

    def has_table(self, tname, schema=None):
        """
        检查时直接连接数据库select，没有异常就说明存在，有异常就说明表不存在
        """
        cur = self.cursor()
        rs = bool(0)
        if settings.DB_TYPE == 'postgresql':
            if schema is None:
                cur.execute(
                    """select relname from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname=current_schema() and lower(relname)=%(name)s""",
                    {'name': tname.lower()});
            else:
                cur.execute(
                    """select relname from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname=%(schema)s and lower(relname)=%(name)s""",
                    {'name': tname.lower(), 'schema': schema});
            rs = bool(cur.rowcount)
        elif settings.DB_TYPE == 'oracle':
            try:
                # 这里是因为oracle的处理方式同postgresql不一样，直接使用查询比较简单
                cur.execute("""select * from %(name)s where rownum = 1""" % {
                'name': (tname if schema is None else '%s.%s' % (schema, tname))})
                rs = bool(1)
            except:
                rs = bool(0)
        else:
            try:
                cur.execute("""select count(0) from %(name)s """ % {
                'name': (tname if schema is None else '%s.%s' % (schema, tname))})
                rs = bool(1)
            except:
                rs = bool(0)
        return rs

    def execute(self, sql, params=None):
        cur = self.cursor()
        # 去掉开头的注释
        sql = re.sub(r'^\s*--.*', '', sql)
        kind = sql.strip()[:6].lower()
        if type(params) in ( tuple, list ):
            if len(params) and type(params[0]) in ( tuple, list, dict ):
                cur.executemany(sql, params)
                return cur
            if kind != 'select':
                cur.execute(sql, params)
                return cur
        elif type(params) in ( dict, ):
            if kind != 'select':
                cur.execute(sql, params)
                return cur
        else:
            if kind != 'select':
                cur.execute(sql)
                return cur
            # 剩下的全是查询
        return sql_execute(cur, sql, params)

    #    函数 execute_sql
    #        参数：  sql 字符串 可以直接执行的sql语句
    #        返回值：类对象列表
    #        功能描述：
    #            执行sql语句，并组织一个类对象列表返回
    #            select类型的直接返回处理后的数据集
    #            非select类型的返回被转换为类对象的[{'rs':0}]
    def execute_sql(self, sql, params={}, dicorobj="class"):
        # 直接执行sql，不传入参数，不管是select还是insert都提供一个列表字典的返回值
        # 非select类的返回[{'rs':0}]
        cur = self.cursor()
        # 去掉开头的注释
        sql = re.sub(r'^\s*--.*', '', sql)

        # 找出所有的占位
        params_find = re.findall(r'%\(\s*(.+?)\s*\)s', sql)
        # 去掉多余的键值对
        params_removed = {k:v for k, v in params.items() if k not in params_find}
        # if params_removed:
        #     print('SQL参数已去掉多余的键值-->', params_removed)
        params = {k:v for k, v in params.items() if k in params_find}

        if settings.DB_TYPE == 'oracle':
            # 替换SQL百分号为冒号形式：%( id )s, %( ywbm)s --> :id, :ywbm
            sql = re.sub(r'%\(\s*(.+?)\s*\)s', r':\1', sql)

        # 2015-02-03 改为在sql中使用${}方式进行subsql的拼接
#        # 将sql中的$$展开
#        sql = sql_rep_ocl(sql, params, settings.DB_TYPE)
#        # 调整参数
#        params = open_dicval_list(params)

        kind = sql.strip()[:6].lower()
        if kind != 'select':
            if params and isinstance(params ,dict):
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            rs = [{'rs': 0}]
        else:
            # 剩下的全是查询
            rs = sql_execute(cur, sql, params)
            rs = rs.fetchall()

        if dicorobj != "class":
            # 返回时提供类对象，字典
            return rs
        else:
            # 返回时提供类对象，不是字典
            return [AttrDict(tk) for tk in rs]


    def rollback(self):
        # 抛异常后，应清理数据库连接，避免该线程下的数据库操作一直异常
        global DB_POOL
        DB_POOL.use_times = 0
        try:
            self.con.rollback()
        except:
            pass # rollback的异常不予处理

    def commit(self):
        self.con.commit()

    def _close( self ):
        try:
            list(map( lambda x:x.close() , self.cursors ))
        except:
            # 任何异常都应该导致数据库连接重置
            global DB_POOL
            DB_POOL.use_times = 0
        put()


@register()
@register('sjapi')
def connect():
    return DBConnection()


from contextlib import contextmanager


@register()
@register('sjapi')
@contextmanager
def connection():
    """
    用在with语句中，用于提供数据库连接对象。线程安全
    用法：
        with connection() as con:
            cur = con.cursor()
            cur.execute( "select * from gl_jddy where mc = '银联'" )
            rs = cur.fetchone()
            ...
    """
    con = None
    try:
        con = DBConnection()
        yield con
        con.commit()
    except:
        if con:
            con.rollback()
        raise
    finally:
        if con:
            con._close()

@register()
@register('sjapi')
def sql_execute(cur, sql, params=None, encoding=None):
    return ResultSet(cur, sql, params, encoding)


class ResultSet(object):
    """
        将cur的select返回结果转换为可按字段名称访问的格式
    """

    def __init__(self, cur, sql, params=None, encoding=None):
        """
            @param:cur   数据库引擎
            @param:sql   sql语句  变量用%s或%d的形式代替  例如:select * from gl_hydy where hydm ='%s' and jgdm =%d
            @param:params   参数列表(数据类型为列表),sql语句所需要的参数顺序组成的列表,接上面的例子,参数列表为: ['admin' ,10]
            @param:encoding  编码形式
        """
        self.__cursor = cur
        self.fields = {}
        #self.rowno  = 0
        self.encoding = encoding
        if params:
            self.__cursor.execute(sql.encode(encoding) if encoding else sql, params)
        else:
            # sql.encode('utf8) 对于cx_oracle连接utf8oracle时会出错
            self.__cursor.execute(sql.encode(encoding) if encoding else sql)
        if self.__cursor.description == None:
            return
        for i in range(0, len(self.__cursor.description)):
            self.fields[self.__cursor.description[i][0].lower()] = i
        self.row_cache = []

    @property
    def rowcount(self):
        """
            返回sql结果记录条数
        """
        self.fetchall()
        return self.__cursor.rowcount

    def printFieldName(self):
        """
            打印查询结果各字段的字段名
        """
        for i in self.fields.keys():
            print(i)

    def next(self):
        """
            顺序取下一条记录，直到取尽
        """
        #self.rowno += 1
        if not self.row_cache:
            self.row_cache = self.__cursor.fetchmany(100)

        self.item = self.row_cache.pop(0) if self.row_cache else None
        return self if self.item is not None else None

    fetchone = next

    def __iter__(self):
        while self.next():
            yield self

    def fetchall(self):
        """
            取所有数据
        """
        rows = []
        while self.next():
            rows.append(self.to_dict())
            #rows.append(  AttrDict(  self.to_dict( )  )  )
        return rows

    #    def getString( self , key , encoding = 'utf8' ):
    #        """
    #            以字符串形式返回某个字段的值
    #                @param:key  字段名称
    #                @encoding:  编码形式
    #        """
    #        if isinstance( key , int ):
    #            v = self.item[ key ]
    #        else:
    #            idx = self.fields[ key.lower() ]
    #            v = self.item[ idx ]
    #        if type( v ) == unicode:
    #            return v.encode( encoding )
    #        elif type( v ) == str and self.encoding != encoding :
    #            return v.decode( self.encoding ).encode( encoding )
    #        elif v:
    #            return str( v )
    #        elif v is not None:
    #            return str(v)
    #        else:
    #            return v

    #    def getUnicode( self , key ):
    #        """
    #            获取字段key的unicode值
    #            @param:key 字段名称
    #        """
    #        if isinstance( key , int ):
    #            v = self.item[ key ]
    #        else:
    #            idx = self.fields[ key.lower() ]
    #            v = self.item[ idx ]
    #        if type( v ) == str:
    #            return v.decode( self.encoding )
    #        elif v:
    #            return unicode( v )
    #        else:
    #            return v

    #    def getInt( self , key ):
    #        """
    #            以整数形式返回字段key的值
    #            @param: key 字段名称
    #        """
    #        if isinstance( key , int ):
    #            v = self.item[ key ]
    #        else:
    #            idx = self.fields[ key.lower() ]
    #            v = self.item[ idx ]
    #        if v:
    #            return int( v )
    #        else:
    #            return 0

    #    def getDouble( self , key ):
    #        """
    #            以float型返回字段key的值
    #            @param:key 字段名称
    #        """
    #        if isinstance( key , int ):
    #            v = self.item[ key ]
    #        else:
    #            idx = self.fields[ key.lower() ]
    #            v = self.item[ idx ]
    #        if v:
    #            return float( v )
    #        else:
    #            return 0.0

    def getValue(self, key):
        """
            获取某个字段的值，是什么类型就返回什么类型
        """
        if isinstance(key, int):
            v = self.item[key]
        else:
            idx = self.fields[key.lower()]
            v = self.item[idx]
        return v

    #    def getDate( self , key ):
    #        """
    #            获取日期型字段的值
    #        """
    #        if isinstance( key , int ):
    #            v = self.item[ key ]
    #        else:
    #            idx = self.fields[ key.lower() ]
    #            v = self.item[ idx ]
    #        if type( v ) == datetime.datetime:
    #            v = v.date()
    #        elif v and type( v ) != datetime.date:
    #            raise RuntimeError( '非日期字段不可按日期获取数据' )
    #        return v

    #    def getPickle( self , key ):
    #        if isinstance( key , int ):
    #            v = self.item[ key ]
    #        else:
    #            idx = self.fields[ key.lower() ]
    #            v = self.item[idx]
    #        if type( v ) == buffer:
    #            return pickle_loads( v )
    #        else:
    #            return None

    def to_dict(self):
        """
            将查询结果转化成字典的形式，键为字段名，实际值
        """
        d = {}
        for key, i in self.fields.items():
            d[key] = self.item[i]
        return d

    def __getitem__(self, key):
        """
            获取某个字段的值
        """
        return self.getValue(key)

    def __getattr__(self, key):
        return self.getValue(key)

    def close(self):
        try:
            self.__cursor.close()
        except:
            pass

#    def mkInsert( self , tn ):
#        """
#            按照查询出来的结果，拼写插入语句
#        """
#        s = 'insert into ' + tn + '('
#        a = self.fields.keys()
#        s += ','.join( a )
#        s += ') values ('
#        vs = []
#        for k in a:
#            v = self.getValue( k )
#            if type( v ) == type(''):
#                vs.append( "'%s'" % v )
#            elif type( v ) == type(0) :
#                vs.append( "%d" % v )
#            elif type( v ) == type(0.1):
#                vs.append( "%f" % v )
#            elif v == None:
#                vs.append( "null" )
#            else:
#                vs.append( "to_date( '%s' , 'YYYYMMDD' )" % v.strftime( '%Y%m%d' ) )
#        s += ','.join( vs )
#        s += ')'
#        return s


#class FakeResultSet( ResultSet ):
#    """ result的替换对象
#    """
#    def __init__( self , cur , sql ):
#        self.fields = {}
#        self.item = []
#        self.first = True
#
#    def next( self ):
#        if self.first :
#            self.first = False
#            return True
#        return False

@register()
def dbbinary( s ):
    """
    用于pgsql的Binary对象生成函数
    """
    return db2api.Binary( s )
