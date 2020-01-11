# -*- coding=utf-8 -*-
from cnocr import CnOcr
import cv2
import numpy as np

# 1 3 8 11 13 15
ocr = CnOcr()
for file in ['1', '3', '8', '11', '22']:
    img_fp = './test/{}.png'.format(file)
    img = cv2.imread(img_fp, 0)
    cv2.imshow('img', img)
    cv2.waitKey(0)
    _, thresh = cv2.threshold(img, 5, 255, cv2.THRESH_BINARY)
    cv2.imshow('thresh', thresh)
    cv2.waitKey(0)
    # thresh = np.array(thresh, np.uint8)
    res = ocr.ocr(img)
    print("Predicted Chars:", res)
    res = ocr.ocr(thresh)
    print("Predicted Chars:", res)