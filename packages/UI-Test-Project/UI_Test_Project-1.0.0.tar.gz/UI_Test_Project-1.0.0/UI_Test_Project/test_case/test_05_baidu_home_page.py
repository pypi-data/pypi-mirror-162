# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : 狂师
# @Email : 公众号：测试开发技术

import logging
from UI_Test_Project.pages.baidu_home_page import BaiduHomePage
from UI_Test_Project.config.url_config import URLConf
from UI_Test_Project.fixture.baidu_fixture import *

logger = logging.getLogger(__name__)

@pytest.mark.baidu
class TestBaiduHomePage():

    @pytest.mark.test
    def test_001_baidu_search(self,driver):
        self.driver = driver
        logger.info('百度搜索:mikezhou')
        baidu_home = BaiduHomePage(self.driver)
        baidu_home.get(URLConf.INDEX_URL.value)
        baidu_home.home_search_input.send_keys("mikezhou")  # 调用search_box变量传入搜索值
        baidu_home.home_search_button.click()

    def test_002_baidu_search(self,driver):
        self.driver = driver
        logger.info('百度搜索:狂师')
        baidu_home = BaiduHomePage(self.driver)
        baidu_home.get(URLConf.INDEX_URL.value)
        baidu_home.home_search_input.send_keys("狂师")  # 调用search_box变量传入搜索值
        baidu_home.home_search_button.click()


if __name__ == '__main__':
    pytest.main(['-v','test_05_baidu_home_page.py'])