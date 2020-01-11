from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
import numpy as np
from CaptchaHandler.model import model
import random
import pickle
import cv2
import os


# 读取数据和标签
print("------开始读取数据------")
image_path = './chars'
data = []
labels = []
imagePaths = []

for label in os.listdir(image_path):
    for image in os.listdir(os.path.join(image_path, label)):
        imagePaths.append(os.path.join(image_path, label, image))

# 拿到图像数据路径，方便后续读取
imagePaths = sorted(imagePaths)
random.seed(42)
random.shuffle(imagePaths)

# 遍历读取数据
for imagePath in imagePaths:
    # 读取图像数据
    image = cv2.imread(imagePath, 0)
    image = cv2.resize(image, (16, 16))
    image = np.expand_dims(image, axis=-1)
    data.append(image)
    # 读取标签
    label = imagePath.split(os.path.sep)[-2]
    labels.append(label)

# 对图像数据做scale操作
data = np.array(data, dtype="float") / 255.0
labels = np.array(labels)

# 数据集切分
(trainX, testX, trainY, testY) = train_test_split(data, labels, test_size=0.25, random_state=42)

# 转换标签为one-hot encoding格式
lb = LabelBinarizer()
trainY = lb.fit_transform(trainY)
testY = lb.transform(testY)

# 数据增强处理
aug = ImageDataGenerator(rotation_range=30, width_shift_range=0.1,
    height_shift_range=0.1, shear_range=0.2, zoom_range=0.2,
    horizontal_flip=True, fill_mode="nearest")


print("------准备训练网络------")
# 设置初始化超参数
EPOCHS = 50
BS = 16
# 建立卷积神经网络
model = model(input_size=(16,16,1), class_num=31)
# tensor_board = TensorBoard()
# 训练网络模型
# H = model.fit_generator(aug.flow(trainX, trainY, batch_size=BS),
#     validation_data=(testX, testY), steps_per_epoch=len(trainX) // BS,
#     epochs=EPOCHS)
# H = model.fit(trainX, trainY, validation_data=(testX, testY), epochs=EPOCHS, batch_size=BS, callbacks=[tensor_board])
H = model.fit(trainX, trainY, validation_data=(testX, testY), epochs=EPOCHS, batch_size=BS)

# 测试
print("------测试网络------")
predictions = model.predict(testX, batch_size=32)
print(classification_report(testY.argmax(axis=1),
    predictions.argmax(axis=1), target_names=lb.classes_))

# 绘制结果曲线
N = np.arange(0, EPOCHS)
plt.style.use("ggplot")
plt.figure()
plt.plot(N, H.history["loss"], label="train_loss")
plt.plot(N, H.history["val_loss"], label="val_loss")
plt.plot(N, H.history["accuracy"], label="train_acc")
plt.plot(N, H.history["val_accuracy"], label="val_acc")
plt.title("Training Loss and Accuracy")
plt.xlabel("Epoch #")
plt.ylabel("Loss/Accuracy")
plt.legend()
plt.savefig('./output/cnn_plot.png')

# 保存模型
print("------正在保存模型------")
model.save('./output/cnn.model')
f = open('./output/cnn_lb.pickle', "wb")
f.write(pickle.dumps(lb))
f.close()
