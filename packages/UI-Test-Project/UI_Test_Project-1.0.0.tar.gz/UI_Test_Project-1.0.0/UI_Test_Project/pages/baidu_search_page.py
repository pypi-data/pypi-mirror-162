# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : 狂师
# @Email : 公众号：测试开发技术
# @File : baidu_search_page.py


from page_objects import PageElement, PageObject,MultiPageElement  #引入库
from UI_Test_Project.pages.baidu_home_page import BaiduHomePage

class BaiduSearchPage(BaiduHomePage):
    '''百度搜索结果页'''
    search_nums_text = PageElement(class_name="nums_text")
    search_tab_item = MultiPageElement(class_name="s-tab-item")
