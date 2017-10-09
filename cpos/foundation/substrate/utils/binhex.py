# -*- coding: utf-8 -*-
"""
    python34中str和python26中的str不一样，要按照bytes做格式化
    简单查看输出的二进制块的方式：
        建立一个二进制文件，然后将输出块放到文件中，将文件编码集转为对应的展示字符集
"""
import io


def bytes_to_hex( s):
    """
        将bytes类型的数据块，转为十六进制的字符串展示，带对比
        test:
            print( bytes_to_hex('abcdefghijklmnopqrstuvwxyz中国'.encode('gbk')) )

        将bytes转为十六进制的串
            import binascii
            str(binascii.b2a_hex(b'\x01\x0212'))[2:-1].upper()

        十六进制字符组转bytes
            bytes().fromhex('010210')
    """
    st = io.StringIO()

    def fmt( x):
        # 这是可见字符(十进制32到126)，不可见字符返回 '.'
        if ord(b' ') <= x <= ord(b'\x7E'):
            return chr(x)
        return '.'
    i = 0
    end = 0
    line = ''
    if not isinstance(s, bytes):
        s = bytes( s)
    for c in s:
        i += 1
        if i % 16 == 1:
            line += '%04X: ' % ( i - 1)
        line += '%02X ' % c
        if i % 8 == 0 and ( i / 8) % 2 == 1:
            line += '- '
        if i % 16 == 0:
            line += ' ' + ''.join( map( fmt, s[i-16:i]))
            st.write( line + '\n')
            line = ''
            end = i
    if line:
        line += ' ' * ( 56 - len( line))
        st.write( line)
        st.write( ' ' + ''.join( map( fmt, s[end:])) + '\n')
    return st.getvalue()
