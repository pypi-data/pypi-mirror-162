# -*- coding: utf-8 -*-
# file: __init__.py.py
# time: 2021/8/5
# author: yangheng <yangheng@m.scnu.edu.cn>
# github: https://github.com/yangheng95
# Copyright (C) 2021. All Rights Reserved.

__name__ = 'autocuda'
__version__ = '0.11.0'
from update_checker import UpdateChecker

from autocuda.autocuda import auto_cuda_info, auto_cuda_index, auto_cuda, auto_cuda_name

checker = UpdateChecker()
check_result = checker.check(__name__, __version__)

if check_result:
    print(check_result)
