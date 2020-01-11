# -*- coding=utf-8 -*-
import requests

if __name__ == '__main__':
    image_url = 'https://jnb.icbc.com.cn/ICBCCOIN/outer/iepa_area05/servlets/ICBCVerifyImage'
    target = 0
    while target < 1000:
        data = requests.get(image_url)
        data = data.content
        with open('captchas/{}.png'.format(str(target + 1)), 'wb') as f:
            f.write(data)
        print('Current/total: {}/1000'.format(str(target + 1)))
        target += 1
    print('Done!')
