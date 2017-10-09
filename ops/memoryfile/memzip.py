# -*- coding: utf-8 -*-
try:
    from zipfileext import Memory_ZipFile as ZipFile ,ZIP_DEFLATED
except:
    from .zipfileext import Memory_ZipFile as ZipFile ,ZIP_DEFLATED

#from zipfile import ZipFile ,ZIP_DEFLATED
import io


class InMemoryZip(object):
    def __init__(self ,zipbuf=None):
        """
        Create the in-memory file-like object
        """
        in_memory_zip = io.BytesIO( zipbuf if isinstance(zipbuf ,bytes) else b'' ) 
        self.zipfile = ZipFile(in_memory_zip, "a", ZIP_DEFLATED, False)

    def __del__(self):
        if self.zipfile:
            self.zipfile.close()

    def close(self):
        self.zipfile.close()

    def add_file(self, filename_in_zip, file_contents):
        """
        向zip文件流中追加内容，bytes的
        """
        # Write the file to the in-memory zip
        self.zipfile.writestr(filename_in_zip, file_contents)
        # Mark the files as having been created on Windows so that
        # Unix permissions are not inferred as 0000
        for zfile in self.zipfile.filelist:
            zfile.create_system = 0       
        return self

    def get_zipbytes(self):
        """
            获得zip的bytes流
        """
        self.zipfile.sj_close()
        self.zipfile.fp.seek(0)
        return self.zipfile.fp.read()

    def get_filelist(self):
        """
            获得文件名列表，过滤掉目录，仅有文件名（全路径）
        """
        namelist = self.zipfile.namelist()
        return [fn for fn in namelist if not fn.endswith('/')]
        
    def get_file_contents(self,name):
        """
            通过文件名获得文件的bytes
        """
        if name in self.get_filelist():
            return self.zipfile.read(name)
        else:
            return None


############################################# 以下为测试用代码 #############################################
def _testwrite(fn,buf):
    """
        写二进制文件，用于测试时比较二进制流是否正确
    """
    open(fn ,'wb').write(buf)

def test_initzip(bytesbuf ,newfn):
    """
    bytesbuf = open(r'F:\Projects_TEMP\testzip\ml1.zip','rb').read()
    test_initzip(bytesbuf ,r'F:\Projects_TEMP\testzip\ml1_new.zip')
    """
    imz = InMemoryZip(bytesbuf)
    _testwrite(newfn ,imz.get_zipbytes())

def test_get_filelist(bytesbuf):
    """
    bytesbuf = open(r'F:\Projects_TEMP\testzip\ml1.zip','rb').read()
    print(test_get_filelist(bytesbuf))
    """
    imz = InMemoryZip(bytesbuf)
    return imz.get_filelist()

def test_get_file_contents(bytesbuf ,name):
    """
    bytesbuf = open(r'F:\Projects_TEMP\testzip\ml1.zip','rb').read()
    print(test_get_file_contents(bytesbuf ,'readme.txt'))
    print(test_get_file_contents(bytesbuf ,'ml1/NEWGL.log.20150623'))
    """
    imz = InMemoryZip(bytesbuf)
    return imz.get_file_contents(name)

def test_add_file(bytesbuf ,newname ,newbuf):
    """
    bytesbuf = open(r'F:\Projects_TEMP\testzip\ml1.zip','rb').read()
    print(test_add_file(bytesbuf ,'readme_new.txt' ,b'this is readme_new.txt'))
    print(test_add_file(bytesbuf ,'ml1/log_new' ,b'this is log_new'))
    """
    imz = InMemoryZip(bytesbuf)
    return imz.add_file(newname ,newbuf)

def test_add_file_2(bytesbuf):
    """
    bytesbuf = open(r'F:\Projects_TEMP\testzip\ml1.zip','rb').read()
    bytesbuf = None
    test_add_file_2(bytesbuf)
    """
    # 原来的
    imz = InMemoryZip(bytesbuf)
    _testwrite(r'F:\Projects_TEMP\testzip\old' ,imz.get_zipbytes())
    _testwrite(r'F:\Projects_TEMP\testzip\old.zip' ,imz.get_zipbytes())
    
    imz.add_file('readme_new.txt' ,b'this is readme_new.txt')
    imz.add_file('ml1/log_new' ,b'this is log_new')
    
    _testwrite(r'F:\Projects_TEMP\testzip\new' ,imz.get_zipbytes())
    _testwrite(r'F:\Projects_TEMP\testzip\new.zip' ,imz.get_zipbytes())
    imz.close()

if __name__ == "__main__":
    # Run a test
    bytesbuf = open(r'F:\Projects_TEMP\testzip\ml1.zip','rb').read()
    test_add_file_2(bytesbuf)
    
