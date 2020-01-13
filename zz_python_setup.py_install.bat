FOR /D %%a IN (build, dist, *.egg-info, __pycache__) DO (CHDIR && RMDIR /S /Q %%a 2>NUL )
python setup.py install
PAUSE
@REM 貌似(python setup.py install)无法自动安装依赖包.
@REM 因为(pip)是(easy_install)的替代品,相比(python setup.py install)增加了自动安装依赖包的功能.
@REM 执行(python setup.py --help-commands)查看详情.
@REM python setup.py sdist
@REM 据说下面的这条命令能自动安装依赖包,实际测试未通过.
@REM python -m pip install zxt --no-cache-dir --find-links ./dist/
