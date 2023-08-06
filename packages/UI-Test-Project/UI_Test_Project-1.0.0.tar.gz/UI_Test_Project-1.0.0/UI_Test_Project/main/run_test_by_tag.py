# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : Mike Zhou
# @Email : 公众号：测试开发技术

import pytest

# 定义标签，按照指定标签过滤运行用例
tag = "baidu"
pytest.main(["-v","-s","-m", f"{tag}"])
