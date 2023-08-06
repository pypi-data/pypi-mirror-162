# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : 狂师
# @Email : 公众号：测试开发技术
# @File : test_baidu_home_page_01.py

import os
import time
import pytest
from selenium import webdriver
from UI_Test_Project.pages.baidu_home_page import BaiduHomePage

class TestBaiduHomePage():
    @classmethod
    def setup_class(cls) -> None:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib')
        cls.url = 'https://www.baidu.com'
        cls.driver = webdriver.Chrome(executable_path=os.path.join(path,'chromedriver.exe'))

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