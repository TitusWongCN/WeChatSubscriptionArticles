# -*- coding=utf-8 -*-
import cv2
from PIL import Image
import math


def get_distance(point1, point2):
    return int(math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2))


image_path = './face2.png'
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

bottom = int(nose_bridge[0][1]) - hair_brim
top = bottom - hat_height
left = int(chin[0][0])
right = left + hat_width
hat_img = hat_img.resize((hat_width, hat_height))  # convert size of hat

# hat_img = hat_img.rotate(45)
hat_region = hat_img
human_region = (left, top + hat_buffer, right, bottom + hat_buffer)
human_img.paste(hat_region, human_region, mask=hat_img)
human_img.show()
print('done')
