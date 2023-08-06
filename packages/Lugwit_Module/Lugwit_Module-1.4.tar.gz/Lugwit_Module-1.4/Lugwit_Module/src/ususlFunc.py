# -*- coding: utf-8
from __future__ import print_function
from inspect import getframeinfo, stack
import os,sys
from pprint import pprint
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def LPrint(*args,**kwargs):
    caller = getframeinfo(stack()[1][0])
    if 'end' not in kwargs:
        kwargs['end']='\n\n'
    if 'printFunc' not in kwargs:
        kwargs['printFunc']=pprint
    if sys.version[0]=='3':
        for x in args:
            kwargs['printFunc'](x,)
        print ('--print info>>>',end='')
    else:
        print (str(args).decode('unicode_escape'),'--info>>>  ',end='')
    # if sys.version[0]=='3':
    #     print (u'{}{}{},line--{},fn--{}{}'.
    #         format( bcolors.OKBLUE,
    #                 os.path.basename(caller.filename),
    #                 bcolors.ENDC,
    #                 caller.lineno,
    #                 caller.function,
    #                 bcolors.ENDC),end=kwargs['end'])
    # else:
    print (u'{},line--{},fn--{}'.
        format( os.path.basename(caller.filename),
                caller.lineno,
                caller.function,
                ),end=kwargs['end'])

def test_LPrint():
    LPrint ((u'你好',u'世界',{u'你好':u'世界'},(u'你好',u'世界')),end='\n\n')
    #print (r"u'\u4e16\u754c',{u'\u4f60\u597d': u'\u4e16\u754c'}".decode('unicode_escape'))
    
if __name__=='__main__':
    test_LPrint()

    

