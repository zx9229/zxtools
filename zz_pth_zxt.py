import datetime
import os
import sys


def now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def calc_data():
    destpath = os.path.realpath(os.path.join(sys.prefix, 'lib/site-packages'))
    basename, filename = os.path.split(os.path.realpath(__file__))
    filename = filename + '.pth'
    filename = os.path.join(destpath, filename)
    content = basename
    return filename, content


def create_file(filename, content):
    try:
        with open(filename, 'w') as f:
            f.write(content)
    except Exception as ex:
        print(now(), ex)
    else:
        print(now(), 'successfully created')
        return True


def delete_file(filename):
    try:
        os.remove(filename)
    except Exception as ex:
        print(now(), ex)
    else:
        print(now(), 'deleted successfully')
        return True


if __name__ == '__main__':
    while True:
        print('C: create file, D: delete file.')
        data = input('please input C/D: ')
        data = data.upper().strip()
        filename, content = calc_data()
        if data == 'C':
            if create_file(filename, content):
                break
        elif data == 'D':
            if delete_file(filename):
                break
        else:
            pass
    exit(0)
