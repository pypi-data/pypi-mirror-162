# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : 狂师
# @Email : 公众号：测试开发技术


import time
import re
import pytest
from selenium.webdriver.common.by import By
from UI_Test_Project.pages.baidu_search_page import BaiduSearchPage
from UI_Test_Project.common.browser import Browser
from UI_Test_Project.common.find_element_until import *

class TestBaiduSearchFlow():
    @classmethod
    def setup_class(cls) -> None:
        cls.url = 'http://www.baidu.com/'
        cls.driver = Browser.open_browser('chrome')

    @classmethod
    def teardown_class(cls) -> None:
        time.sleep(2)
        cls.driver.quit()

    def setup_method(self) -> None:
        self.baidu = BaiduSearchPage(self.driver)
        self.baidu.get(self.url)

    def test_001_baidu_search_flow(self):
        '''
        测试百度搜索业务流程，校验标签页
        '''
        self.baidu.home_search_input.send_keys('python')
        self.baidu.home_search_button.click()
        tab_list = []
        for els in self.baidu.search_tab_item:
            print(els.text)
            tab_list.append(els.text)
        assert '图片' in tab_list
        assert '视频' in tab_list
        assert '地图' in tab_list

    def test_002_baidu_search_flow(self):
        '''
        测试百度搜索业务流程，校验搜索结果大于等于0
        '''
        self.baidu.home_search_input.send_keys('python')
        self.baidu.home_search_button.click()
        # 增加显式等待，以防元素没有加载出来
        find_element_visibility(self.driver,(By.CLASS_NAME,'nums_text'))
        result_text = self.baidu.search_nums_text.text

        # 提取搜索结果数值
        nums = ''.join(re.findall("\d+", result_text))
        print(nums)
        assert int(nums) >= 0



if __name__ == '__main__':
    pytest.main()