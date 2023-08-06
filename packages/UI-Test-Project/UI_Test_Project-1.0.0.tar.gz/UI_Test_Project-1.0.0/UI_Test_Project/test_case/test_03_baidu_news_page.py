# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : 狂师
# @Email : 公众号：测试开发技术

from UI_Test_Project.pages.baidu_news_page import BaiduNewsPage
from UI_Test_Project.config.url_config import URLConf
from UI_Test_Project.fixture.baidu_fixture import *

class TestBaiduNewsPage():

    def test_001_baidu_news_search(self,driver):
        '''
        断言是否成功跳转到国内新闻
        '''
        self.driver = driver
        self.baidu_news = BaiduNewsPage(self.driver)
        self.baidu_news.get(URLConf.NEWS_URL.value)
        self.baidu_news.news_guonei_link.click()
        assert 'guonei' in self.driver.current_url

    def test_002_baidu_news_search(self,driver):
        '''
        断言是否成功跳转到国际新闻
        '''
        self.driver = driver
        self.baidu_news = BaiduNewsPage(self.driver)
        self.baidu_news.get(URLConf.NEWS_URL.value)
        self.baidu_news.news_guoji_link.click()
        assert 'guoji' in self.driver.current_url

    def test_003_baidu_news_search(self,driver):
        '''
        断言输入框搜索功能
        '''
        self.driver = driver
        self.baidu_news = BaiduNewsPage(self.driver)
        self.baidu_news.get(URLConf.NEWS_URL.value)
        self.baidu_news.news_search_input.send_keys('周星驰')
        self.baidu_news.news_search_button.click()
        assert '周星驰' in self.driver.title


if __name__ == '__main__':
    pytest.main(['-v', 'test_03_baidu_news_page.py'])