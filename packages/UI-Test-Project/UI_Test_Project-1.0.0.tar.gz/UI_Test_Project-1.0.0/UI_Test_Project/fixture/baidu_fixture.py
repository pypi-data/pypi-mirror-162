#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : baidu_fixture.py
# @Author: zhoujinjian


import time
import pytest
import warnings
from UI_Test_Project.common.browser import Browser


@pytest.fixture()
def driver():
    warnings.simplefilter('ignore', ResourceWarning)
    driver = Browser.open_browser('chrome')
    yield driver
    time.sleep(2)
    driver.quit()
