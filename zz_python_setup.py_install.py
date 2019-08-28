import os
import re
import shutil


def isMatch(name):
    if name in ('build', 'dist', '__pycache__'):
        return True
    if re.match('.*.egg-info', name):
        return True
    return False


def doSth():
    basename, filename = os.path.split(os.path.realpath(__file__))
    for dirpath, dirnames, filenames in os.walk(basename):
        for dirname in dirnames:
            if isMatch(dirname):
                dirname = os.path.join(dirpath, dirname)
                print('delete:', dirname)
                shutil.rmtree(dirname)
    print('')


if __name__ == '__main__':
    doSth()
    os.system('python setup.py install')
