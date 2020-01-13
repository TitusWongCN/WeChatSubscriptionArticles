# -*- coding=utf-8 -*-
import face_recognition
from PIL import Image


face_image = face_recognition.load_image_file('face2.jpg')
face_locations = face_recognition.face_locations(face_image)
face_landmarks = face_recognition.face_landmarks(face_image, face_locations)

human_img = Image.open('./face2.jpg')
human_img = human_img.convert("RGBA")
hat_img = Image.open("./hat.png")
hat_img = hat_img.convert("RGBA")

for face_location, face_landmark in zip(face_locations, face_landmarks):
    top, right, bottom, left = face_location
    top -= 10
    head_h = bottom - top  # hight of head
    head_l = right - left  # length of head
    hat_img = hat_img.resize((head_l, head_h))  # convert size of hat
    hat_region = hat_img
    human_region = (left, top - head_h, right, top)
    human_img.paste(hat_region, human_region, mask=hat_img)
human_img.show()
