# -*- coding=utf-8 -*-
import cv2
from PIL import Image
import math


def get_distance(point1, point2):
    return int(math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2))


image_path = './face1.png'
human_img = Image.open(image_path)
human_img = human_img.convert('RGBA')
# 圣诞帽相关参数
hat_img = Image.open("./hat.png")
hat_brim_length = 175.0
hat_height_buffer = 25.0
hat_img = hat_img.convert('RGBA')

# load image:
image = cv2.imread(image_path, 0)
# find faces:
cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')
faces = cascade.detectMultiScale(image, 1.3, 5)

# create landmark detector and load lbf model:
facemark = cv2.face.createFacemarkLBF()
facemark.loadModel('lbfmodel.yaml')

# run landmark detector:
# landmarks---[0, 16]----Jaw line
# landmarks---[17, 21]---Left eyebrow
# landmarks---[22, 26]---Right eyebrow
# landmarks---[27, 30]---Nose bridge
# landmarks---[30, 35]---Lower nose
# landmarks---[36, 41]---Left eye
# landmarks---[42, 47]---Right Eye
# landmarks---[48, 59]---Outer lip
# landmarks---[60, 67]---Inner lip
ok, landmarks = facemark.fit(image, faces)
print(ok)

chin = landmarks[0][0][:17]
nose_bridge = landmarks[0][0][27:31]

face_width = get_distance(chin[0], chin[-1])
hair_brim = get_distance(nose_bridge[-1], chin[int(len(chin)/2)])

resize_ratio = face_width / hat_brim_length
hat_width = int(hat_img.width * resize_ratio)
hat_height = int(hat_img.height * resize_ratio)
hat_buffer = int(hat_height_buffer * resize_ratio)

hat_bottom = int(nose_bridge[0][1]) - hair_brim
hat_top = hat_bottom - hat_height
hat_left = int(chin[0][0])
hat_right = hat_left + hat_width
hat_img = hat_img.resize((hat_width, hat_height))  # convert size of hat

# hat_img = hat_img.rotate(45)
hat_region = hat_img
human_region = (hat_left, hat_top + hat_buffer, hat_right, hat_bottom + hat_buffer)
human_img.paste(hat_region, human_region, mask=hat_img)
# human_img.show()
# print('hat done')

# 口罩相关参数
mask_img = Image.open("./mask.png")
mask_height = 330.0
mask_img = mask_img.convert('RGBA')

mask_actual_height = get_distance(nose_bridge[0], chin[int(len(chin)/2)])
mask_resize_ratio = mask_actual_height / mask_height
mask_width = int(mask_img.width * mask_resize_ratio)
mask_height = int(mask_img.height * mask_resize_ratio)

mask_top = int(nose_bridge[0][1])
mask_bottom = mask_top + mask_height
mask_left = int((nose_bridge[0][0] + chin[int(len(chin)/2)][0] - mask_width)/2)
mask_right = mask_left + mask_width
mask_img = mask_img.resize((mask_width, mask_height))  # convert size of mask

mask_region = mask_img
human_region = (mask_left, mask_top, mask_right, mask_bottom)
human_img.paste(mask_region, human_region, mask=mask_img)
human_img.show()
print('mask done')
