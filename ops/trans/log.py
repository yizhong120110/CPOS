# -*- coding: utf-8 -*-
import logging , os, sys , traceback, time

class DateFileHandler(logging.FileHandler):
    def __init__(self, filename, mode="a" ):
        self.bf = filename
        self.curDate = time.strftime( '%Y%m%d' , time.localtime())
        self.mode = mode
        t = time.time()
        filename = filename + '.' + self.curDate
        logging.FileHandler.__init__(self, filename, mode)

    def emit(self, record):
        cd = time.strftime( '%Y%m%d' , time.localtime())
        if cd != self.curDate:
            self.stream.close()
            self.curDate = cd
            self.stream = open(self.bf + '.' + cd , self.mode )
        logging.FileHandler.emit(self, record)

def init_log( name = None , screen = False , thread = True, logdir = os.path.abspath( '%s/log/'%os.environ.get('HOME','') ) ):
    return init_logger( name , logdir , screen , thread )

init = init_log

def init_logger( logname , logdir , screen = True , thread = True ):
    logobj = logging.getLogger( logname )
    # 判断是否需要清理
    if logobj.handlers:
        return  logobj  # 日志已创建，跳过
    
    # 初始化日志文件处理句柄
    fn = '%s.log' % logname
    hdlr = DateFileHandler( os.path.join( logdir , fn ) )
    fmts = '%(asctime)s ' + 'P%(process)d ' + ( 'T%(thread)d ' if thread else '' ) +  '%(levelname)s %(message)s'
    formatter = logging.Formatter( fmts )
    hdlr.setFormatter(formatter)
    logobj.addHandler( hdlr )
    
    if screen:
        # 初始化屏幕打印处理句柄
        hdlr = logging.StreamHandler()
        fmts = '%(asctime)s %(name)s：' + 'P%(process)d ' + ( 'T%(thread)d ' if thread else '' ) + '%(levelname)s %(message)s'
        formatter = logging.Formatter( fmts )
        hdlr.setFormatter(formatter)
        logobj.addHandler( hdlr )

    logobj.setLevel( logging.DEBUG )
    return logobj

def _fmt_msg( *args , **kwargs ):
    if len( args ) > 1:
        msg = args[0] % args[1:]
    elif len( args ) == 1:
        msg = args[0]
    else:
        msg = ''
    
    block = kwargs.get( 'block' )
    if type(block) is str:
        # 是块日志
        bin = kwargs.get( 'bin' , True )
        if bin:
            block = to_hex( block )
    
    if block:
        block = '\n'+'='*40+'\n'+block+ ('\n' if block[-1] != '\n' else '' ) +'='*40 + '\n'
    elif msg[-1] == '\n':
        block = ''
    else:
        block = '\n'
    
    msg = msg + block
    if msg[-1] == '\n':
        msg = msg[:-1]
    return msg
    
def debug( logname , *args , **kwargs ):
    if logname:
        logger = init_log( logname )
        logger.debug( _fmt_msg( *args , **kwargs ) )

def info( logname , *args , **kwargs ):
    if logname:
        logger = init_log( logname )
        logger.info( _fmt_msg( *args , **kwargs ) )
        
def warning( logname , *args , **kwargs ):
    if logname:
        logger = init_log( logname )
        logger.warning( _fmt_msg( *args , **kwargs ) )
        
def error( logname , *args , **kwargs ):
    if logname:
        logger = init_log( logname )
        logger.error( _fmt_msg( *args , **kwargs ) )
        
def critical( logname , *args , **kwargs ):
    if logname:
        logger = init_log( logname )
        logger.critical( _fmt_msg( *args , **kwargs ) )

def exception( logname , *args , **kwargs ):
    if logname:
        logger = init_log( logname )
        exc_msg = traceback.format_exc()
        args = list( args )
        if args:
            args[0] += '\n%s'
        else:
            args.append( '%s' )
        args.append( exc_msg )
        logger.error( _fmt_msg( *args , **kwargs ) )
        return ''