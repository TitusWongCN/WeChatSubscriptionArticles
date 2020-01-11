# -*- coding=utf-8 -*-
import time
from selenium import webdriver
from keras.models import load_model
import pickle
from ABC.CaptchaHandler.processor import get_cutted_patches
import cv2
import numpy as np
from config import users
import random
from utils import find_and_click, find_and_fill

def choose_bank(driver, location):
    top_xpath = '//*[@id="orglevel1"]'
    locations = location.split(',')
    for index, loca in enumerate(locations):
        level = str(index + 1)
        xpath = top_xpath.replace('1', level)
        ele_orglevel = driver.find_element_by_xpath(xpath)
        for org_index, org in enumerate(ele_orglevel.text.split('\n')):
            if loca in org:
                find_and_click(driver, xpath + '/option[{}]'.format(str(org_index + 1)))
                break
    xpath = top_xpath.replace('1', str(len(locations) + 1))
    try:
        ele_bottom = driver.find_element_by_xpath(xpath)
    except:
        return
    else:
        org_index = random.choice(list(range(len(ele_bottom.text.split('\n'))))[1:])
        find_and_click(driver, xpath + '/option[{}]'.format(str(org_index + 1)))


def handle_capchar(driver, model, lb):
    capchar = 'ABC/temp_capchar.png'
    result = ''
    ele_piccaptcha = driver.find_element_by_xpath('//*[@id="piccaptcha"]')
    ele_piccaptcha.screenshot(capchar)
    image = cv2.imread(capchar, 0)
    image = image[1:-1, 1:-1]
    target_patches = get_cutted_patches(image)
    for target_patch in target_patches:
        image = cv2.resize(target_patch, (16, 16))
        # scale图像数据
        image = image.astype("float") / 255.0
        image = np.expand_dims(image, axis=-1)
        # 对图像进行拉平操作
        image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
        # 预测
        preds = model.predict(image)
        # 得到预测结果以及其对应的标签
        i = preds.argmax(axis=1)[0]
        label = lb.classes_[i]
        result += label
    ele_capchar = driver.find_element_by_xpath('//*[@id="piccode"]')
    ele_capchar.clear()
    ele_capchar.send_keys(result)


def get_mobile_code(driver, mobile, model, lb):
    handle_capchar(driver, model, lb)
    ele_mobile = driver.find_element_by_xpath('//*[@id="mobile"]')
    ele_mobile.send_keys(mobile)
    while True:
        find_and_click(driver, '//*[@id="sendValidate"]')
        ele_errorCaptchaNo = driver.find_element_by_xpath('//*[@id="errorCaptchaNo"]')
        if ele_errorCaptchaNo.text == '短信验证码已发送成功':
            break
        else:
            find_and_click(driver, '//*[@id="piccaptcha"]')
            time.sleep(0.1)
            handle_capchar(driver, model, lb)


def handle_coindate(driver):
    is_find = False
    find_and_click(driver, '//*[@id="coindate"]')
    while not is_find:
        for tr_index in range(6):
            for td_index in range(7):
                try:
                    ele_td = driver.find_element_by_xpath(
                        '//*[@id="ui-datepicker-div"]/table/tbody/tr[{}]/td[{}]'.format(str(tr_index + 1), str(td_index + 1)))
                except:
                    continue
                if ele_td.get_attribute('title') == '可选择':
                    is_find = True
                    ele_td.click()
                    return
        find_and_click(driver, '//*[@id="ui-datepicker-div"]/div/a[2]/span')


def auto_work(user, paras, model, lb, url):
    print('-' * 50)
    print(time.strftime('%y-%m-%d %H:%M:%S', time.localtime(time.time())))
    print('当前处理账户名为：{}'.format(user))
    driver = webdriver.Chrome()
    driver.get(url)
    get_mobile_code(driver, paras['mobile'], model, lb)
    find_and_fill(driver, '//*[@id="name"]', user)
    find_and_fill(driver, '//*[@id="identNo"]', paras['identNo'])
    find_and_fill(driver, '//*[@id="cardvalue0"]', paras['cardvalue0'])
    choose_bank(driver, paras['location'])
    handle_coindate(driver)
    phoneCaptchaNo = input('请输入手机验证码, 按回车键确认（如果还未收到短信，请等到短信之后再输入）：\n')
    find_and_fill(driver, '//*[@id="phoneCaptchaNo"]', phoneCaptchaNo)
    find_and_click(driver, '//*[@id="infosubmit"]')
    time.sleep(2)
    # driver.close()



if __name__ == '__main__':
    print('本工具仅作为技术交流之用，请勿滥用！')
    print('目前本软件仅能实现半自动化')
    print('目前版本的软件仅支持农行预约的省份')
    print("------读取自动识别验证码模型和标签------")
    model = load_model('ABC/CaptchaHandler/output/cnn.model')
    lb = pickle.loads(open('ABC/CaptchaHandler/output/cnn_lb.pickle', "rb").read())
    url = input('输入本次预约界面的网址，按回车键确认：\n')
    # url = 'https://eapply.abchina.com/coin/coin/CoinRequest?issueid=I049&t=1576767405981'
    for user, paras in users.items():
        auto_work(user, paras, model, lb, url)
