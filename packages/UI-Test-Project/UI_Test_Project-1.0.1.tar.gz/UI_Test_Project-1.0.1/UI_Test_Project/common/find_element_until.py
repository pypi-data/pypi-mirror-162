# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : 狂师
# @Email : 公众号：测试开发技术
# @File : find_element_until.py

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def find_element_presence(driver, selector, timeout=30):
    '''
    检查指定元素，在指定时间内，在DOM结构中是否存在
    '''
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located(selector))

def find_element_visibility(driver, selector, timeout=30):
    '''
    检查指定元素，在指定时间内，是否可见
    '''
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.visibility_of_element_located(selector))


def find_element_clickable(driver, selector, timeout=30):
    '''
    检查指定元素，在指定时间内，是否可点击
    '''
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.element_to_be_clickable(selector))