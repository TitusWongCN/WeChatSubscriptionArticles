# -*- coding=utf-8 -*-
import face_recognition
import cv2
import copy


faces = ['face1.png', 'face2.jpg', 'face3.png']

for face in faces:
    image = face_recognition.load_image_file(face)
    face_locations = face_recognition.face_locations(image)

    rects_face = copy.deepcopy(image)
    for top, right, bottom, left in face_locations:
        cv2.rectangle(rects_face, (left, top), (right, bottom), (0, 0, 255), 2)

    points_face = copy.deepcopy(image)
    face_landmarks = face_recognition.face_landmarks(image, face_locations)
    print(face_landmarks)
    for each in face_landmarks:
        for i in each.keys():
            if '' in i:
                # print(i, each[i])
                for any in each[i]:
                    points_face = cv2.circle(points_face, any, 3, (0,0,255), -1)

    # Display the resulting image
    cv2.imshow('points_face', points_face[:,:,::-1])
    cv2.imshow('rects_face', rects_face[:,:,::-1])
    cv2.waitKey(0)
