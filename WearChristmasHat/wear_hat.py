# -*- coding=utf-8 -*-
import face_recognition
from PIL import Image
import math


def get_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

image_path = './face3.png'

face_image = face_recognition.load_image_file(image_path)
face_locations = face_recognition.face_locations(face_image)
face_landmarks = face_recognition.face_landmarks(face_image, face_locations)

human_img = Image.open(image_path)
human_img = human_img.convert("RGBA")
# 圣诞帽相关参数
hat_img = Image.open("./hat.png")
hat_brim_ratio = 175.0 / 300.0
hat_img = hat_img.convert("RGBA")

for face_location, face_landmark in zip(face_locations, face_landmarks):
    chin = face_landmark['chin']
    nose_bridge = face_landmark['nose_bridge']

    face_width = get_distance(chin[0], chin[-1])
    hair_brim = get_distance(nose_bridge[-1], chin[int(len(chin)/2)])

    image_width = int(face_width / hat_brim_ratio)

    top, right, bottom, left = face_location
    top -= 10
    head_h = bottom - top  # hight of head
    head_l = right - left  # length of head
    hat_img = hat_img.resize((head_l, head_h))  # convert size of hat

    # hat_img = hat_img.rotate(45)
    hat_region = hat_img
    human_region = (left, top - head_h, right, top)
    human_img.paste(hat_region, human_region, mask=hat_img)
human_img.show()
