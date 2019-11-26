import math


def adbf(f: float, sign: bool = False, aD: int = 0, bF: int = 6):
    '''
    print(adbf(3.14, False, 0, 6)) => [3.140000]
    print(adbf(3.14, False, 4, 6)) => [   3.140000]
    print(adbf(3.14,  True, 0, 6)) => [+3.140000]
    print(adbf(3.14,  True, 4, 6)) => [  +3.140000]
    '''
    srcStr = ('%' + ('+' if sign else '') + '.*f') % (bF, f)
    oldStr = ('%' + ('+' if sign else '') + 'd') % (f)
    newStr = ('%' + ('+' if sign else '') + '*d') % (aD, f)
    dstStr = srcStr.replace(oldStr, newStr)
    return dstStr


if __name__ == '__main__':
    print(adbf(3.14, False, 0, 6))
    print(adbf(3.14, False, 4, 6))
    print(adbf(3.14, True, 0, 6))
    print(adbf(3.14, True, 4, 6))
