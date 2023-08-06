# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : 狂师
# @Email : 公众号：测试开发技术


import re
import os
from selenium.webdriver.common.by import By
from UI_Test_Project.pages.baidu_search_page import BaiduSearchPage
from UI_Test_Project.config.url_config import URLConf
from UI_Test_Project.fixture.baidu_fixture import *
from UI_Test_Project.common.find_element_until import *
from UI_Test_Project.common.parse_excel import ParseExcel


def get_test_data():
    '''
    从外部获取参数数据
    :return:
    '''
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'test_data')
    excelPath = os.path.join(path, 'test_baidu_search.xlsx')
    sheetName = '搜索关键字'
    return ParseExcel(excelPath, sheetName)


class TestBaiduSearchFlow():

    def test_001_baidu_search_flow(self, driver):
        '''
        测试百度搜索业务流程，校验标签页
        '''

        self.driver = driver
        self.baidu = BaiduSearchPage(self.driver)
        self.baidu.get(URLConf.INDEX_URL.value)
        self.baidu.home_search_input.send_keys('python')
        self.baidu.home_search_button.click()
        tab_list = []
        for els in self.baidu.search_tab_item:
            print(els.text)
            tab_list.append(els.text)
        assert '图片' in tab_list
        assert '视频' in tab_list
        assert '地图' in tab_list

    @pytest.mark.parametrize('keyword,exp_nums', get_test_data().getDatasFromSheet())
    def test_002_baidu_search_flow(self, keyword, exp_nums,driver):
        '''
        参数化百度搜索业务流程，校验搜索结果大于等于0
        '''
        self.driver = driver
        self.baidu = BaiduSearchPage(self.driver)
        self.baidu.get(URLConf.INDEX_URL.value)
        self.baidu.home_search_input.send_keys(keyword)
        self.baidu.home_search_button.click()
        # 增加显式等待，以防元素没有加载出来
        find_element_visibility(self.driver, (By.CLASS_NAME, 'nums_text'))
        result_text = self.baidu.search_nums_text.text

        # 提取搜索结果数值
        nums = ''.join(re.findall("\d+", result_text))
        print(nums)
        assert (int(nums) >= exp_nums)


if __name__ == '__main__':
    pytest.main(['-v','test_04_baidu_search_flow.py'])
