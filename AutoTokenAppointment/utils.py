# -*- coding=utf-8 -*-


def find_and_fill(driver, xpath, value):
    ele = driver.find_element_by_xpath(xpath)
    ele.send_keys(value)


def find_and_click(driver, xpath):
    ele = driver.find_element_by_xpath(xpath)
    ele.click()