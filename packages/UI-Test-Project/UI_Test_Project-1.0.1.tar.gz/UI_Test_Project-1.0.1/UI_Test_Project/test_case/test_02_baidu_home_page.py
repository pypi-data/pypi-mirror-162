# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : 狂师
# @Email : 公众号：测试开发技术
# @File : test_baidu_home_page_02.py

import time
import warnings
import pytest
from UI_Test_Project.pages.baidu_home_page import BaiduHomePage
from UI_Test_Project.common.browser import Browser

class TestBaiduHomePage():
    @classmethod
    def setup_class(cls) -> None:
        warnings.simplefilter('ignore', ResourceWarning)
        cls.url = 'https://www.baidu.com'
        # cls.driver = Browser.open_browser('chrome')
        cls.driver = Browser.open_browser('firefox')
        # cls.driver = Browser.open_browser('edge')

    @classmethod
    def teardown_class(cls) -> None:
        time.sleep(2)
        cls.driver.quit()

    def test_001_baidu_search(self):
        baidu_home = BaiduHomePage(self.driver)
        baidu_home.get(self.url)
        baidu_home.home_search_input.send_keys("mikezhou")  # 调用search_box变量传入搜索值
        baidu_home.home_search_button.click()

    def test_002_baidu_search(self):
        baidu_home = BaiduHomePage(self.driver)
        baidu_home.get(self.url)
        baidu_home.home_search_input.send_keys("狂师")  # 调用search_box变量传入搜索值
        baidu_home.home_search_button.click()


if __name__ == '__main__':
    pytest.main()