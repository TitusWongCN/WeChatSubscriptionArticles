# # -*- coding=utf-8 -*-
# import face_recognition
import cv2
import copy
from PIL import Image
#
#
# faces = ['face1.png', 'face2.jpg', 'face3.png']
#
# for face in faces:
#     image = face_recognition.load_image_file(face)
#     face_locations = face_recognition.face_locations(image)
#
#     rects_face = copy.deepcopy(image)
#     for top, right, bottom, left in face_locations:
#         cv2.rectangle(rects_face, (left, top), (right, bottom), (0, 0, 255), 2)
#
#     points_face = copy.deepcopy(image)
#     face_landmarks = face_recognition.face_landmarks(image, face_locations)
#     print(face_landmarks)
#     for each in face_landmarks:
#         for i in each.keys():
#             if '' in i:
#                 # print(i, each[i])
#                 for any in each[i]:
#                     points_face = cv2.circle(points_face, any, 3, (0,0,255), -1)
#
#     # Display the resulting image
#     cv2.imshow('points_face', points_face[:,:,::-1])
#     cv2.imshow('rects_face', rects_face[:,:,::-1])
#     cv2.waitKey(0)
#
# image = Image.open('./hat.png')
# image = image.rotate(-15)
# image.show()


image_path = './face1.png'
# load image:
image = cv2.imread(image_path)
gray_img = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
# find faces:
cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')
faces = cascade.detectMultiScale(gray_img, 1.3, 5)

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
ok, landmarks = facemark.fit(gray_img, faces)

points_face = copy.deepcopy(image)
for each in landmarks[0][0]:
    points_face = cv2.circle(points_face, tuple(each), 3, (0, 0, 255), -1)

# Display the resulting image
cv2.imshow('points_face', points_face)
cv2.waitKey(0)
