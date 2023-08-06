# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : 狂师
# @Email : 公众号：测试开发技术
# @File : baidu_news_page.py


from page_objects import PageElement, PageObject  #引入库

class BaiduNewsPage(PageObject):
    '''百度新闻页'''
    news_guonei_link = PageElement(link_text="国内")
    news_guoji_link = PageElement(link_text="国际")
    news_search_input = PageElement(id_="ww")
    news_search_button = PageElement(id_='s_btn_wr')
