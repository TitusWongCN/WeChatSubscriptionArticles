# -*- coding=utf-8 -*-
import time
from selenium import webdriver
from config import users
from utils import find_and_click, find_and_fill
from selenium.webdriver.support.ui import WebDriverWait



def choose_bank(driver, location, cointype):
    locations = location.split(',')
    for province_index in range(15):
        ele_province = driver.find_element_by_xpath('//*[@id="areainfo"]/input[{}]'.format(str(province_index + 1)))
        if locations[0] in ele_province.get_attribute('value'):
            if '已约完' in ele_province.text:
                return False
            else:
                ele_province.click()
                break
    bank_xpath = [
        # ('//*[@id="selcoinType"]', cointype),
        ('//*[@id="selonebank"]', locations[0] if len(locations)>0 else '分行'),
        ('//*[@id="seltwobank"]', locations[1] if len(locations)>1 else '分行'),
        ('//*[@id="selbank"]', locations[2] if len(locations)>2 else '支行'),
    ]
    # element = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('//*[@id="selcoinType"]'))
    for xpath, filter in bank_xpath:
        while True:
            try:
                ele_target = driver.find_element_by_xpath(xpath)
                break
            except:
                continue
        for option_index, option in enumerate(ele_target.text.split('\n')[1:]):
            if filter in option:
                find_and_click(driver, xpath + '/option[{}]'.format(str(option_index + 1)))
                break
    find_and_click(driver, '//*[@id="nextstep1"]')
    try:
        ele_result = driver.find_element_by_xpath('//*[@id="timeerrordiv"]')
        if '该网点额度已被抢光' in ele_result.text:
            return False
        else:
            return True
    except:
        return True


def handle_coindate(driver):
    is_find = False
    find_and_click(driver, '//*[@id="txtexchangedate"]')
    while not is_find:
        for tr_index in range(6):
            for td_index in range(7):
                try:
                    ele_td = driver.find_element_by_xpath(
                        '//*[@id="ui-datepicker-div"]/table/tbody/tr[{}]/td[{}]'.format(str(tr_index + 1), str(td_index + 1)))
                except:
                    continue
                if '可选择' in ele_td.text:
                    is_find = True
                    ele_td.click()
                    return
        find_and_click(driver, '//*[@id="ui-datepicker-div"]/div/a[2]/span')


def handle_capchar(driver):
    # for i in range(1000):
    #     capchar = 'CaptchaHandler/captchas/{}.png'.format(str(i + 1))
    #     ele_img = driver.find_element_by_xpath('//*[@id="validateCode"]')
    #     ele_img.screenshot(capchar)
    #     find_and_click(driver, '//*[@id="refreshCode"]')
    #     time.sleep(0.5)
    capchar = input('输入验证码: \n')
    find_and_fill(driver, '//*[@id="txtverify"]', capchar)


def auto_work(user, paras, url):
    print('-' * 50)
    print(time.strftime('%y-%m-%d %H:%M:%S', time.localtime(time.time())))
    print('当前处理账户名为：{}'.format(user))
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(2)
    result = choose_bank(driver, paras['location'], paras['cointype'])
    if result != False:
        find_and_fill(driver, '//*[@id="txtName"]', user)
        find_and_fill(driver, '//*[@id="txtPpNum"]', paras['identNo'])
        find_and_fill(driver, '//*[@id="txtTel"]', paras['mobile'])
        find_and_click(driver, '//*[@id="nextstep3"]')
        handle_coindate(driver)
        handle_capchar(driver)
        appoint_cnt = driver.find_element_by_xpath('//*[@id="nums"]').get_attribute('value')
        max_cnt = driver.find_element_by_xpath('//*[@id="perbooknum"]').text.split('-')[-1][:-1]
        while True:
            find_and_click(driver, '//*[@id="js_submit"]')
            time.sleep(1)
            if appoint_cnt != max_cnt:
                try:
                    driver.switch_to.alert.accept()
                    time.sleep(3)
                    break
                except:
                    continue
        print('预约成功！')
    else:
        print('该营业处已约完！')


if __name__ == '__main__':
    print('本工具仅作为技术交流之用，请勿滥用！')
    print('目前本软件仅能实现半自动化')
    print('目前版本的软件仅支持农行/工行预约的省份')
    print("------读取自动识别验证码模型和标签------")
    # url = input('输入本次预约界面的网址，按回车键确认：\n')
    url = 'https://www.icbc.com.cn/ICBC/ICBCCOIN/coinorder.htm'
    for user, paras in users.items():
        auto_work(user, paras, url)
