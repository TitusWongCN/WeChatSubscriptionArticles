# 导入所需工具包
from keras.models import load_model
import pickle
import cv2
import numpy as np


# 加载测试数据并进行相同预处理操作
image = cv2.imread('./test_chars/H/face2.jpg', 0)
output = image.copy()
image = cv2.resize(image, (16, 16))
# scale图像数据
image = image.astype("float") / 255.0
image = np.expand_dims(image, axis=-1)
# 对图像进行拉平操作
image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
# 读取模型和标签
print("------读取模型和标签------")
model = load_model('./output/cnn.model')
lb = pickle.loads(open('./output/cnn_lb.pickle', "rb").read())
# 预测
preds = model.predict(image)
# 得到预测结果以及其对应的标签
i = preds.argmax(axis=1)[0]
label = lb.classes_[i]
# 在图像中把结果画出来
text = "{}: {:.2f}%".format(label, preds[0][i] * 100)
print(text)