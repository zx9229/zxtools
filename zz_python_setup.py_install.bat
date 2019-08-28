FOR /D %%a IN (build, dist, *.egg-info, __pycache__) DO (CHDIR && RMDIR /S /Q %%a 2>NUL )
python setup.py install
PAUSE
