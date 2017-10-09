#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This is a module to provide the common interfaces.
"""

__author__ = 'Percy'
__version__ = '1.0'
__create_data__ = '2015/1/29'


class Clarified(object):
    NAME = 'ClarifiedObject'

    def __repr__(self):
        items = list()
        dent_fmt = ''

        if '__slots__' in dir(self):
            for key in self.__slots__:
                value = getattr(self, key, None)
                items.append('[__slots__]%s=%s' % (key, value))
        else:
            if not 'reprdent____' in dir( self):
                self.reprdent____ = 0
            dent_fmt = ''

            #print(self.NAME + str ( self.reprdent____))
            for x in range(self.reprdent____):
                dent_fmt += '\t'

            for key, value in self.__dict__.items():
                if getattr(self.__class__, key, None) != value:
                    #print (value)
                    if isinstance(value, Clarified):
                        value.reprdent____ = self.reprdent____ + 1
                        value.parent____ = self.getname()
                        #print ('isinstance' + str(value.__repr__dent))
                    if not key.endswith('____'):
                        items.append('%s=%s' % (key, value))

        if not items:
            return "<%s>" % self.NAME
        return ("\n"+dent_fmt+"<%s: \n\t"+dent_fmt+"%s \n"+dent_fmt+">") % (self.getname(), (',\n\t' + dent_fmt).join( sorted(items)))

    def getname(self):
        return self.NAME


class Named(Clarified):

    '''Provide methods to name the objects which extended from this one.

    '''
    NAME = 'NamedObject'

    def __init__(self):
        Clarified.__init__(self)
        self._name = 'unnamed'

    def getname(self):
        return self.NAME + " - " + self._name

    def setname(self, s):
        self._name = s


class Monitored(Named):

    '''Provide methods to monitor the objects which extended from this one.

    '''

    def __init__(self):
        Named.__init__(self)

    def serialize(self):
        '''Rewrite this method to allow more information to be presented.

            By default, only name is presented.
        '''
        return str(self.getname())

    def console_debug(self):
        print(self.serialize())

if __name__ == '__main__':
    pass
