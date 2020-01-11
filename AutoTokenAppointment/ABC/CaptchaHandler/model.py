# -*- coding=utf-8 -*-
from keras.layers import Flatten, Input, Dropout, Conv2D, MaxPooling2D, Dense
from keras.models import Model
from keras.optimizers import Adam


def model(input_size, class_num):
    input = Input(shape=input_size)
    x = Conv2D(16, (3,3), activation='relu', padding='same')(input)
    x = MaxPooling2D((2,2), strides=(2,2))(x)
    x = Conv2D(64, (3,3), activation='relu', padding='same')(x)
    x = MaxPooling2D((2,2), strides=(2,2))(x)
    x = Conv2D(256, (3,3), activation='relu', padding='same')(x)
    x = MaxPooling2D((2,2), strides=(2,2))(x)
    x = Flatten()(x)
    x = Dense(1024, activation='relu')(x)
    x = Dropout(0.5)(x)
    x = Dense(2048, activation='relu')(x)
    x = Dropout(0.5)(x)
    x = Dense(class_num, activation='softmax')(x)
    model = Model(input=input, output = x)

    model.compile(optimizer=Adam(lr=1e-4), loss='categorical_crossentropy', metrics=['accuracy'])
    return model
