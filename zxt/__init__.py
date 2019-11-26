# -*- coding: utf-8 -*-
# help(zxt) 的时候会显示这些文字.
# python setup.py install 会重新安装它. [zxt-0.1-py3.5.egg] => [^zxt-.*.egg$]

import zxt.db
import zxt.file
import zxt.hq_sinajs_cn
import zxt.tdx_file
import zxt.temp.crossover_point_info
import zxt.temp.db
import zxt.temp.math

# 在我们执行import时，当前目录是不会变的（就算是执行子目录的文件），还是需要完整的包名。
# 只需要在最顶层的 __init__.py 中 import 即可.
