import math


def adbf(f: float, symbol: bool = False, aD: int = 0, bF: int = 6):
    '''
    print(adbf(3.14, False, 0, 6)) => [3.140000]
    print(adbf(3.14, False, 4, 6)) => [   3.140000]
    print(adbf(3.14,  True, 0, 6)) => [+3.140000]
    print(adbf(3.14,  True, 4, 6)) => [  +3.140000]
    '''
    symbolStr = '+' if symbol else ''
    fmtF = '%{0:s}{1:d}.{2:d}f'.format(symbolStr, aD, bF)
    fm1D = '%{0:s}{1:d}d.'.format(symbolStr, aD)
    fm2D = '%{0:s}d.'.format(symbolStr, aD)
    fmtFs = fmtF % f
    fm1Ds = fm1D % f
    fm2Ds = fm2D % f
    sssss = fmtFs.replace(fm2Ds, fm1Ds)
    return sssss


if __name__ == '__main__':
    print(adbf(3.14, False, 0, 6))
    print(adbf(3.14, False, 4, 6))
    print(adbf(3.14, True, 0, 6))
    print(adbf(3.14, True, 4, 6))
