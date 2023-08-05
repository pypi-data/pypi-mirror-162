#!/bin/python3

import os
import sys
import shutil
from datetime import datetime

def generate_ver():
    current = datetime.now()
    version=current.strftime("%H-%M-%S")
    return version
    
def prepare_env(strDir,changeTo):
    isExists = os.path.exists(strDir)
    if not isExists:
        os.makedirs(strDir)
    else:
        shutil.rmtree(strDir)
        os.makedirs(strDir)
    if changeTo:
        os.chdir(strDir)
    return 0


def copy_file(srcName,tarName):
    fileR=open(srcName,"r")
    fileW=open(tarName,"w")

    R= fileR.read()
    W = fileW.write(R)

    fileR.close()
    fileW.close()
    return 0

def replace_string(fileName,srcStr,tarStr):
    t=""
    f= open(fileName,"r+") 
    t=f.read()
    t=t.replace(srcStr,tarStr)
    f.seek(0,0)
    f.write(t)
    f.truncate()
    return 0


