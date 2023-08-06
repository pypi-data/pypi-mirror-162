# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : 狂师
# @Email : 公众号：测试开发技术


from page_objects import PageElement, PageObject  #引入库

class BaiduHomePage(PageObject):
    '''百度首页'''
    home_search_input = PageElement(id_="kw")
    home_search_button = PageElement(id_="su")