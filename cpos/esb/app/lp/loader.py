# -*- coding: utf-8 -*-

import os, sys

basepath = os.path.split( os.path.abspath( __file__ ) )[0]
basepath_lst = basepath.split( os.sep )

for n in range( len( basepath_lst ) ):
    stakepath = os.sep.join( basepath_lst[:-n] if n != 0 else basepath_lst )
    stake = os.path.join( stakepath, 'stakefile' )
    if os.path.exists( stake ):
        sys.path.append( os.path.split( stakepath )[0] )
        break

if __name__ == '__main__':
    pass