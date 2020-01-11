# -*- coding=utf-8 -*-
import requests

if __name__ == '__main__':
    image_url = 'https://eapply.abchina.com/coin/Helper/ValidCode.ashx?0.5805915363836303'
    target = 0
    while target < 1000:
        data = requests.get(image_url).content
        with open('captchas/{}.jpg'.format(str(target + 1)), 'wb') as f:
            f.write(data)
        print('Current/total: {}/1000'.format(str(target + 1)))
        target += 1
    print('Done!')
