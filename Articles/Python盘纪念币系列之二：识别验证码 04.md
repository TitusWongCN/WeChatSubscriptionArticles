
> 上一篇我们对图片做了预处理，构建了数据集，今天我们就要用这个数据集来训练神经网络了。

### 学习数据集

我们拿到任何一个数据集都要先进行观察。一是我们自己要学会分辨，这样才能更有针对性的指导神经网络来分类；二是要看我们要处理的问题的复杂度，这样也是便于了解我们的神经网络要有多复杂（或者多“深”）。

![](https://user-gold-cdn.xitu.io/2019/12/16/16f0ed7dc843b5b1?w=472&h=517&f=png&s=86661)

上图是我们的数据集的截图。观察发现“0”、“1”、“9”，“I”，“O”这五个字符是没有图片的，那是我们的数据集错了吗？检查原始的验证码图片发现，确实没有这几个字符。其实认真想一下就能知道，这几个都是容易与别的字符产生混淆的字符，所以大概率是在生成验证码的时候就可以把它们剔除了，在这里也要为这个程序员的细心点个赞~另外，观察还发现每个字符文件夹下面的图片数量是差不多的，这样也是为了让神经网络能不偏不倚的为每一个字符寻找最优的参数。


### 设计神经网络

说了这么多，终于要开始设计神经网络了。用`Python`编写神经网络的库有很多，比如`TensorFlow`、`PyTorch`和`Keras`等等，这里我们不讨论各自的优劣势，我的工作中用的是`Keras`，所以这里我们采用`Keras`。

因为是图像分类，所以我们使用在图像类任务中最常用到的神技——卷积神经网络（CNN）。

```python
from keras.layers import Flatten, Input, Dropout, Conv2D, MaxPooling2D, Dense
from keras.models import Model
from keras.optimizers import Adam

def model(input_size, class_num):
    input = Input(shape=input_size)
    x = Conv2D(16, (3,3), activation='relu', padding='same')(input)
    x = MaxPooling2D((2,2), strides=(2,2))(x)
    x = Conv2D(64, (3,3), activation='relu', padding='same')(input)
    x = MaxPooling2D((2,2), strides=(2,2))(x)
    x = Conv2D(256, (3,3), activation='relu', padding='same')(input)
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
```

这基本上就是一个最简单的CNN了，模型结构大致如下图：

![](https://user-gold-cdn.xitu.io/2019/12/16/16f0ef51840792a7?w=295&h=871&f=png&s=65116)

就是简单的卷积-池化-卷积-池化-卷积-池化-全连接-全连接-dropout结构，因为问题很简单，所以模型结构不需要多复杂。

### 训练神经网络

网络设计好了，就可以准备开始训练了，也就是想办法把训练图片喂到模型里面让它自动更新各项参数。因为我们前期其实已经做好了部分工作，所以只需要按照类别读取图片，然后输入到模型中区即可，读取图片并生成标签的代码如下：

```python
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
```

训练模型的代码如下：

```python
print("------准备训练网络------")
# 设置初始化超参数
EPOCHS = 50
BS = 16
# 建立卷积神经网络
model = model(input_size=(16,16,1), class_num=31)
H = model.fit(trainX, trainY, validation_data=(testX, testY), epochs=EPOCHS, batch_size=BS)
```

训练模型的代码反而最少，是不是发现训练一个神经网络其实根本就不难。

来看一下训练神经网络时的输出：

```txt
Train on 332 samples, validate on 111 samples
Epoch 1/50

 16/332 [>.............................] - ETA: 7s - loss: 3.4399 - accuracy: 0.0625
 32/332 [=>............................] - ETA: 4s - loss: 3.4547 - accuracy: 0.0312
 48/332 [===>..........................] - ETA: 3s - loss: 3.4442 - accuracy: 0.0208
 64/332 [====>.........................] - ETA: 2s - loss: 3.4401 - accuracy: 0.0312
 80/332 [======>.......................] - ETA: 2s - loss: 3.4368 - accuracy: 0.0250
 96/332 [=======>......................] - ETA: 2s - loss: 3.4366 - accuracy: 0.0208
112/332 [=========>....................] - ETA: 1s - loss: 3.4371 - accuracy: 0.0179
128/332 [==========>...................] - ETA: 1s - loss: 3.4373 - accuracy: 0.0156
144/332 [============>.................] - ETA: 1s - loss: 3.4358 - accuracy: 0.0139
160/332 [=============>................] - ETA: 1s - loss: 3.4337 - accuracy: 0.0188
176/332 [==============>...............] - ETA: 1s - loss: 3.4330 - accuracy: 0.0170
192/332 [================>.............] - ETA: 1s - loss: 3.4310 - accuracy: 0.0156
208/332 [=================>............] - ETA: 0s - loss: 3.4313 - accuracy: 0.0192
224/332 [===================>..........] - ETA: 0s - loss: 3.4325 - accuracy: 0.0179
240/332 [====================>.........] - ETA: 0s - loss: 3.4300 - accuracy: 0.0208
256/332 [======================>.......] - ETA: 0s - loss: 3.4315 - accuracy: 0.0195
272/332 [=======================>......] - ETA: 0s - loss: 3.4334 - accuracy: 0.0184
288/332 [=========================>....] - ETA: 0s - loss: 3.4341 - accuracy: 0.0208
304/332 [==========================>...] - ETA: 0s - loss: 3.4349 - accuracy: 0.0197
320/332 [===========================>..] - ETA: 0s - loss: 3.4315 - accuracy: 0.0281
332/332 [==============================] - 2s 7ms/step - loss: 3.4340 - accuracy: 0.0271 - val_loss: 3.4193 - val_accuracy: 0.0270
```

神经网络会在运行每一个Epoch时更新参数，这样不停更新，最后达到最优：

```txt
Epoch 50/50

 16/332 [>.............................] - ETA: 1s - loss: 0.0155 - accuracy: 1.0000
 32/332 [=>............................] - ETA: 1s - loss: 0.0132 - accuracy: 1.0000
 48/332 [===>..........................] - ETA: 1s - loss: 0.0259 - accuracy: 1.0000
 64/332 [====>.........................] - ETA: 1s - loss: 0.0289 - accuracy: 1.0000
 80/332 [======>.......................] - ETA: 1s - loss: 0.0247 - accuracy: 1.0000
 96/332 [=======>......................] - ETA: 1s - loss: 0.0271 - accuracy: 1.0000
112/332 [=========>....................] - ETA: 1s - loss: 0.0251 - accuracy: 1.0000
128/332 [==========>...................] - ETA: 1s - loss: 0.0243 - accuracy: 1.0000
144/332 [============>.................] - ETA: 1s - loss: 0.0230 - accuracy: 1.0000
160/332 [=============>................] - ETA: 1s - loss: 0.0234 - accuracy: 1.0000
176/332 [==============>...............] - ETA: 0s - loss: 0.0318 - accuracy: 0.9943
192/332 [================>.............] - ETA: 0s - loss: 0.0372 - accuracy: 0.9896
208/332 [=================>............] - ETA: 0s - loss: 0.0354 - accuracy: 0.9904
224/332 [===================>..........] - ETA: 0s - loss: 0.0395 - accuracy: 0.9866
240/332 [====================>.........] - ETA: 0s - loss: 0.0521 - accuracy: 0.9833
256/332 [======================>.......] - ETA: 0s - loss: 0.0491 - accuracy: 0.9844
272/332 [=======================>......] - ETA: 0s - loss: 0.0531 - accuracy: 0.9816
288/332 [=========================>....] - ETA: 0s - loss: 0.0510 - accuracy: 0.9826
304/332 [==========================>...] - ETA: 0s - loss: 0.0488 - accuracy: 0.9836
320/332 [===========================>..] - ETA: 0s - loss: 0.0488 - accuracy: 0.9844
332/332 [==============================] - 2s 6ms/step - loss: 0.0478 - accuracy: 0.9849 - val_loss: 0.0197 - val_accuracy: 0.9910
```

下面是整个训练过程中，各项参数值的曲线：

![](https://user-gold-cdn.xitu.io/2019/12/16/16f0f00a758d2dfd?w=640&h=480&f=png&s=47907)

简单的，就是在训练过程中，不论是训练集还是验证集，它们的损失值不断下降到无限接近于0，而模型的准确率则无限接近于1.

### 测试神经网络

我们随便拿两个字符来进行测试：

![](https://user-gold-cdn.xitu.io/2019/12/16/16f0f04d2ddf5065?w=18&h=16&f=png&s=365)

测试代码如下：

```python
# 加载测试数据并进行相同预处理操作
image = cv2.imread('./test_chars/3/1.jpg', 0)
output = image.copy()
image = cv2.resize(image, (16, 16))
# scale图像数据
image = image.astype("float") / 255.0
image = np.expand_dims(image, axis=-1)
# 对图像进行拉平操作
image = image.reshape((1, image.shape[0], image.shape[1],image.shape[2]))
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
```

输出结果为：

![](https://user-gold-cdn.xitu.io/2019/12/16/16f0f05a3e1d634c?w=199&h=81&f=png&s=3903)

再试一张：

![](https://user-gold-cdn.xitu.io/2019/12/16/16f0f05fcc4d271e?w=17&h=16&f=png&s=344)

输出结果为：

![](https://user-gold-cdn.xitu.io/2019/12/16/16f0f069647a34df?w=194&h=85&f=png&s=3914)

两次实验的结果都表明，我们的神经网络模型的性能是可以的。

### 后记

至此，验证码的识别就讲完了。

本系列的所有源代码都会放在下面的github仓库里面，有需要可以参考，有问题欢迎指正，谢谢！

```html
https://github.com/TitusWongCN/AutoTokenAppointment
```


> 得到最新消息，最新的纪念币将于本月19号开始预约，所以本系列也马上会在这个时间左右完结。敬请期待最后的自动预约部分~

---

[第一期：Python盘纪念币系列之一：简介](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=2247483772&idx=1&sn=d578c80bbb0216c5bf528a8cc4a3a89a&chksm=ea4bdabcdd3c53aa46796d7b96a5292361223b1f96a1a0579f9bd2c3a80886a27ca4d57a6d68&scene=21#wechat_redirect)

[第二期：Python盘纪念币系列之二：识别验证码 01](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=2247483781&idx=1&sn=0bff3d3410b55f25a5528cfcd9454a41&chksm=ea4bda45dd3c5353ba6b6cc67ebe84cebabc06b53a39391e2d49be45a6e5b763ab4bd60b3979&scene=21#wechat_redirect)

[第三期：Python盘纪念币系列之二：识别验证码 02](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000138&idx=1&sn=442469c6418af28deedd24dbf4fa033b&chksm=6a4bda4a5d3c535ca5e7d46fdf4c837eabba8691fad6a881c56781e037a530952a6fd42e92c7#rd)

[第四期：Python盘纪念币系列之二：识别验证码 03](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000144&idx=1&sn=4541cf9fb5dfdf0df5b69193845ebb9a&chksm=6a4bda505d3c5346ae5fee707c6a6221d66b3ecd8f8ea70e31793140d83499925d3cfe3c2542#rd)