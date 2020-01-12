# -*- coding=utf-8 -*-
import face_recognition
import cv2


image = face_recognition.load_image_file('face1.jpg')
face_locations = face_recognition.face_locations(image)
face_landmarks = face_recognition.face_landmarks(image, face_locations)

for each in face_landmarks:
    for i in each.keys():
        # left_eyebrow[(141, 160), (149, 159), (157, 163), (163, 168), (169, 174)]
        # right_eyebrow[(186, 182), (197, 184), (206, 186), (213, 189), (218, 195)]
        # left_eye[(146, 176), (151, 176), (157, 180), (161, 187), (154, 185), (148, 182)]
        # right_eye[(185, 198), (191, 196), (198, 199), (203, 203), (196, 204), (190, 202)]
        if 'eye' in i:
            print(i, each[i])
            for any in each[i]:
                image = cv2.circle(image, any, 3, (0,0,255), -1)

# Display the resulting image
cv2.imshow('image', image[:,:,::-1])
cv2.waitKey(0)
