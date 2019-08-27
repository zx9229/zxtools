from setuptools import setup, find_packages
setup(
    name="zxt",
    version="0.0.20190827",
    packages=find_packages(),
)

# name参数的值, 就是 pip list 显示的名字, 但不是 import 的名字.
# import 的名字, 是(最顶层的 __init__.py 所在的目录)的名字.

# 自定义包
# python自定义第三方包的打包和安装
# https://www.jianshu.com/p/e909b56bc5c9
