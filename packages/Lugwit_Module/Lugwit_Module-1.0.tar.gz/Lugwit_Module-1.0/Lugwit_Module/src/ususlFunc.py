# -*- coding: utf-8
from __future__ import print_function
from inspect import getframeinfo, stack
import os
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

def LPrint(*args,end='\n'):
    caller = getframeinfo(stack()[1][0])
    #print (caller.filename, caller.lineno, caller.function, *args)
    print (args,'--info>>>   ',end='')
    print (u'{}{}{},line--{},fn--{}\n{}'.
        format( bcolors.OKBLUE,
                os.path.basename(caller.filename),
                bcolors.ENDC,
                caller.lineno,
                caller.function,
                bcolors.ENDC),end=end)
    
def test_LPrint(*args,):
    LPrint (u'你好',u'世界',{u'你好':u'世界'},(u'你好',u'世界'))
    
if __name__=='__main__':
    test_LPrint()

    

