def left_not_vertical(pointA, pointB, pointM, pointN):
    ''' lineAB不是竖线 '''
    xA, yA = pointA
    xB, yB = pointB
    xM, yM = pointM
    xN, yN = pointN
    kAB = (yA - yB) / (xA - xB)  # (y=k*x+b)里的k
    bAB = (xA * yB - xB * yA) / (xA - xB)  # (y=k*x+b)里的b
    pointIsExist = False
    point = None
    pointIsOnline = False
    if xM == xN:  # x为定值,竖直线.
        pointIsExist = True
        xP = xM
        yP = kAB * xP + bAB
        point = (xP, yP)
    else:
        kMN = (yM - yN) / (xM - xN)
        bMN = (xM * yN - xN * yM) / (xM - xN)
        pointIsExist = (kAB != kMN)  # 斜率不一样,肯定存在交叉点.
        if pointIsExist:
            xP = (bMN - bAB) / (kAB - kMN)  # 交点的x
            yP = (kAB * bMN - kMN * bAB) / (kAB - kMN)  # 交点的y
            point = (xP, yP)
    if point is not None:
        xMIN = min(xA, xB, xM, xN)
        xMAX = max(xA, xB, xM, xN)
        yMIN = min(yA, yB, yM, yN)
        yMAX = max(yA, yB, yM, yN)
        pointIsOnline = xMIN <= xP and xP <= xMAX and yMIN <= yP and yP <= yMAX
    return (pointIsExist, point, pointIsOnline)


def crossover_point_info(pointA, pointB, pointM, pointN):
    ''' 交叉点信息 '''
    xA, yA = pointA
    xB, yB = pointB
    xM, yM = pointM
    xN, yN = pointN
    abIsVertical = (xA == xB)
    mnIsVertical = (xM == xN)
    if abIsVertical and mnIsVertical:
        return (False, None, False)
    elif abIsVertical:
        return left_not_vertical(pointM, pointN, pointA, pointB)
    else:
        return left_not_vertical(pointA, pointB, pointM, pointN)


def _test(pA, pB, pM, pN):
    cpi = crossover_point_info(pA, pB, pM, pN)
    try:
        from matplotlib import pyplot as plt
        plt.title('isExist={}; point={}; isOnline={}'.format(*cpi))
        plt.scatter(*zip(pA, pB), s=90, marker='.', label='lineAB', c='red')
        plt.scatter(*zip(pM, pN), s=90, marker='.', label='lineMN', c='green')
        if cpi[0]:
            plt.scatter(*cpi[1], s=100, marker='*', label='crossP', c='blue')
        plt.legend()
        plt.show()
    except Exception as ex:
        print(cpi)
        print(ex)


if __name__ == '__main__':
    pA = (1, 2)
    pB = (1, 5)
    pM = (5, 6)
    pN = (2, 10)
    _test(pA, pB, pM, pN)
