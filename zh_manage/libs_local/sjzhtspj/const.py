
# -*- coding: utf-8 -*-
# Action: 常量定义
# Author: jind
# AddTime: 2015-01-13
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行


#字段类型字典
ZDLX_DIC = {
    '-1':'请选择',
    'CHAR': 'CHAR',
    'VARCHAR2': 'VARCHAR2',
    'NCHAR': 'NCHAR',
    'NVARCHAR2': 'NVARCHAR2',
    'DATE': 'DATE',
    'LONG': 'LONG',
    'RAW': 'RAW',
    'LONG RAW': 'LONG RAW',
    'BLOB': 'BLOB',
    'CLOB': 'CLOB',
    'NCLOB': 'NCLOB',
    'BFILE': 'BFILE',
    'NUMBER': 'NUMBER',
    'DECIMAL': 'DECIMAL',
    'INTEGER': 'INTEGER',
    'FLOAT': 'FLOAT',
    'REAL': 'REAL'
}

# 打印模板类型对应编辑器类型
MBLX_BJLX_DIC = {
    'xml': 'xml',
    'mako': 'python',
    'grid++': 'python'
}

# 节点类型对应名称
JDLX_MC_DIC = {
    '1': '交易节点',
    '2': '系统节点',
    '3': '开始节点',
    '4': '结束节点',
    '5': '通讯打包节点',
    '6': '通讯解包节点',
    '7': '通讯节点',
    '8': '流程打包节点',
    '9': '流程解包节点',
    '10': '开始节点',
    '11': '结束节点'
}

# 测试案例类别对应名称
CSALLB_MC_DIC = {
    '1': '交易',
    '2': '子流程',
    '3': '节点',
    '4': '通讯子流程',
}

# 超时时间（通讯）
TIMEOUT = 60

# 索引类型
SYLX_DIC = {
    'NORMAL': '正常索引',
    'NORMAL/REV': '反转索引',
    'BITMAP': '位图索引'
}

# 节点要素归属类别
JDYS_LB_DIC = {
    '1': '节点使用',
    '2': '系统默认'
}

# 节点要素来源
JDYS_LY_DIC = {
    '1': '自动',
    '2': '手工'
}

# oracle保留关键字,在新增表时数据表名称、字段名称都不可为这些关键字
ORACLE_KEYWORDS_LST = ['ABORT','COMMIT','EXIT','LIMITED','ORDER','ROWLABEL','TERMINATE','ACCEPT','COMPRESS','FALSE','LOCK','OTHERS','ROWNUM','THEN','ACCESS',
'CONNECT','FETCH','LONG','OUT','ROWS','TO','ADD','CONSTANT','FILE','LOOP','PACKAGE','ROWTYPE','TRIGGER','ALL','CRASH','FLOAT','MAX','PARTITION','RUN',
'TRUE','ALTER','CREATE','FOR','MAXEXTENTS','PCTFREE','SAVEPOINT','TYPE','AND','CURRENT','FROM','MIN','PLS_INTEGER','SCHEMA','UID','ANY','CURRVAL','FROM',
'MINUS','POSITIVE','SELECT','UNION','ARRAY','CURSOR','FUNCTION','MLSLABEL','POSITIVEN','SEPARATE','UNIQUE','ARRAYLEN','DATABASE','GENERIC','MOD','PRAGMA',
'SESSION','UPDATE','AS','DATA_BASE','GOTO','MODE','PRIOR','SET','USE','ASC','DATE','GRANT','MODIFY','PRIVATE','SHARE','USER','ASSERT','DBA','GROUP',
'NATUAL','PRIVILEGES','SIZE','VALIDATE','ASSIGN','DEBUGOFF','HAVING','NATURALN','PROCEDURE','SMALLINT','VALUES','AT','DEBUGON','IDENTIFIED','NEW','PUBLIC',
'SPACE','VARCHAR','AUDIT','DECLARE','IF','NEXTVAL','RAISE','SQL','VARCHAR2','BETWEEN','DECIMAL','IMMEDIATE','NOAUDIT','RANGE','SQLCODE','VARIANCE',
'BINARY_INTEGER','DEFAULT','IN','NOCOMPRESS','RAW','SQLERRM','VIEW','BODY','DEFINITION','INCREMENT','NOT','REAL','START','VIEWS','BOOLEAN','DELAY',
'INDEX','NOWAIT','RECORD','STATE','WHEN','BY','DELETE','INDEXES','NULL','REF','STATEMENT','WHENEVER','CASE','DESC','INDICATOR','NUMBER','RELEASE','STTDEV',
'WHERE','CHAR','DIGITS','INITIAL','NUMBER_BASE','REMR','SUBTYPE','WHILE','CHAR_BASE','DISPOSE','INSERT','OF','RENAME','SUCCESSFUL','WITH','CHECK',
'DISTINCT','INTEGER','OFFLINE','RESOURCE','SUM','WORK','CLOSE','DO','INTERFACE','ON','RETURN','SYNONYM','WRITE','CLUSTER','DROP','INTERSECT','ONLINE',
'REVERSE','SYSDATE','XOR','CLUSTERS','ELSE','INTO','OPEN','REVOKE','TABAUTH','TEXT','COLAUTH','ELSIF','IS','ROWLABEL','ROLLBACK','TABLE','COLUMN',
'EXCLUSIVE','LEVEL','OPTION','ROW','TABLES', 'COMMENT','EXISTS','LIKE','OR','ROWID','TASK','SYS']

# 无单引号的字段类型
STRING_ZD_LST = [ 'DATE' ]

# 复核人角色代码
FHR_JSDM = 'fhr'