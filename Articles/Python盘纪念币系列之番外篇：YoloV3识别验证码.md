> 最近武夷山币要开始准备预约了，公众号后台也有很多朋友向我咨询和交流脚本。本着技术交流的想法，把之前的代码重新梳理了一遍，发现识别验证码的成功率并没有想象中那么高。本着简化流程和“杀鸡就要用牛刀”的精神，这篇文章会通过`YoloV3`来解决这个问题。

> 本期文章较长，比较熟悉的同学可以粗略看看。

### 之前的做法

之前的做法是把每个字符切割出来，然后用一个`3`层卷积加`2`层全连接的卷积神经网络模型对字符分类。如果能精确切割，那效果自然没的说，但实际操作下来发现要想对所有组合的验证码作完美的切割还是有困难的（其实主要还是笨，没想到完美健壮的切割方法）。

目前的切割方法经常会把字符切割成下面这种样子：

![切割方法经常会把字符切割成下面这种样子](https://user-gold-cdn.xitu.io/2020/6/18/172c78762fa563f6?w=704&h=527&f=png&s=49208)

这明显是不对的，也导致最终验证码的错误。虽然页面上验证码填写错误会继续识别刷新出的新验证码，但考虑到这是一个类似于抢购的使用环境，“一击即中”的验证码识别方法是很有必要的。

### 为什么要用`YoloV3`

最近`Yolo`系列的目标检测算法可谓是相当热闹。`YoloV3`提出后，`Yolo`系列算法很久都没有比较大的进展，可近段时间`YoloV4`和`YoloV5`却如雨后春笋般冒了出来。先不说官方暂时还没认可`YoloV5`以`Yolo`命名，但单从算法性能来看，在一定程度上`YoloV5`已经算是现阶段速度与精度并存的`SoTA`了。

新算法层出不穷，真是苦了算法工程师们了，不少同学苦笑：学不动了！

![](https://user-gold-cdn.xitu.io/2020/6/17/172c2fff33150e53?w=1242&h=2208&f=jpeg&s=259938)

但发牢骚归发牢骚，新算法出来那是必须得好好摆弄一番的了。从全球最大的男性交友网站上[下载](https://github.com/ultralytics/yolov5)了`YoloV5`的代码，当然同时也不忘给了一个大大的`Star`。我平时用`Keras`比较多，但这套代码是基于`Pytorch`编写的。考虑到对`Keras`和`YoloV3`更加熟悉，这次暂时还是先用`YoloV3`来做，于是又[下载](https://github.com/qqwweee/keras-yolo3)了`Keras`版本的`YoloV3`代码。需要下载地址的可以在公众号后台发送`Yolo`获取。

正好武夷山币即将开始预约，又是一次调试代码交流技术的好机会，下面就来看看`YoloV3`是怎么解决验证码的识别问题的吧。

### 数据集构建

#### 准备数据集

在之前的文章中，我们已经拿到了大量的验证码图片，没有的同学可以到下面这个地址获取。

```html
https://github.com/TitusWongCN/WeChatSubscriptionArticlesAutoTokenAppointment/ABC/CaptchaHandler/captchas
```

（熟悉`YoloV3`数据集格式的同学可以直接跳到下一节）

#### 准备打标软件

`YoloV3`是一个目标检测模型，训练它需要的不只是图片本身，还要一起提供要检测目标的类别和位置，也就是常说的“标签”。给数据集打标的工具有很多，比如`LabelImg`和`Labelme`等，这里使用第一种工具。`LabelImg`是一款专门用于为目标检测数据集生成标签的开源软件，用户可以很方便的为目标“画框贴标签”。下面提供已经打包好的`exe`可执行文件，使用`Windows 10`系统的同学可以直接到下面的链接下载使用（其他`Windows`系统没有测试，可以下载来自己测试）：

```html
https://github.com/tzutalin/labelImg/files/2638199/windows_v1.8.1.zip
```

下载好之后，先把`data`文件夹下的`predefined_classes.txt`文件内容改为实际的验证码的所有类别。要注意，每一行只能有一个类别名，类别名的顺序没有强制要求，比如：

```text
A
B
C
...
0
2
5
...
```

这样做会为打标签和后面准备开始训练提供方便。

#### 开始打标

打开`labelImg.exe`出现下面的界面：

![LabelImg开启界面](https://user-gold-cdn.xitu.io/2020/6/18/172c6a03fe1d2ce8?w=1018&h=674&f=png&s=40093)

点击左侧菜单栏的`Open Dir`，在弹出的文件夹选择框中选择验证码图片所在的文件夹，这时候软件就会显示找到的第一张图片了。然后在验证码图片文件夹同级目录新建一个`labels`文件夹，接着点击左侧菜单栏的`Change Save Dir`选择`labels`文件夹，这样软件会默认把生成的标记文件存储在`labels`文件夹。

下面可以正式为图片打标了。点击左侧菜单栏的`Create\nRectBox`，这时鼠标会变成一个十字叉，用鼠标在图片上画出一个包裹目标的最小的矩形框。松开鼠标的时刻会出来一个对话框要选择这个框内目标的类别，前面已经配置过类别，在下面的框中选择对应的类别然后确认即可。

![LabelImg打标界面](https://user-gold-cdn.xitu.io/2020/6/18/172c76b9c83a4152?w=1018&h=674&f=png&s=94573)

上面就标记好了一个字符，每张验证码图片都有四个字符，所有每张验证码图片应该都有四个框。

#### 查看标记文件

每个文件打标后会生成对应的一个`.xml`格式的标记文件，文件内容如下（省略了部分内容）：

```xml
<annotation>
	<folder>captchas</folder>
	<filename>1.jpg</filename>
	<path>ABC\CaptchaHandler\captchas\1.jpg</path>
	<source>
		<database>Unknown</database>
	</source>
	<size>
		<width>0</width>
		<height>0</height>
		<depth>3</depth>
	</size>
	<segmented>0</segmented>
	<object>
		<name>4</name>
		<pose>Unspecified</pose>
		<truncated>0</truncated>
		<difficult>0</difficult>
		<bndbox>
			<xmin>38</xmin>
			<ymin>10</ymin>
			<xmax>50</xmax>
			<ymax>26</ymax>
		</bndbox>
	</object>
	<object>
		...
	</object>
	<object>
		...
	</object>
	<object>
		...
	</object>
</annotation>
```

生成的文件中有被标记文件的路径和对应图片中目标的位置以及类别等相关信息，这些信息下面都会用到。

#### 生成`Yolo`特定格式

相对于其他的目标检测模型来说，`Yolo`系列模型需要的训练数据的格式比较独特。参考下载的`YoloV3`源码的说明文件，可以找到支持的数据集格式如下：

> One row for one image;
> 
> Row format: image_file_path box1 box2 ... boxN;
> 
> Box format: x_min,y_min,x_max,y_max,class_id (no space).

这个解释简单明了，也就是说：

1. 一张图片占一行
2. 每一行的格式为：图片路径 目标框1 目标框2 ... 目标框N
3. 目标框的格式为：X轴最小值,Y轴最小值,X轴最大值,Y轴最大值,类别ID

最后还给出了示例：

> path/to/img1.jpg 50,100,150,200,0 30,50,200,120,3
>
> path/to/img2.jpg 120,300,250,600,2

既然人家都说的这么清楚了，那我们需要做的就是依葫芦画瓢了。代码如下：

```python
import os
import xml.etree.ElementTree as ET # 用来读取XML文件的包
import cv2

# 首先根据前面写的predefined_classes.txt文件内容定义好类别的顺序
labels = ['A','B','C','D','E','F','G','H','J','K','L','M','N','P','Q',
          'R','S','T','U','V','W','X','Y','Z','2','3','4','5','6','7','8']
dirpath = r'./capchars/labels'  # 存放xml文件的目录

for fp in os.listdir(dirpath):
    root = ET.parse(os.path.join(dirpath, fp)).getroot()
    path = root.find('path').text
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    height, width = img.shape
    boxes = [path, ]

    for child in root.findall('object'): # 找到图片中的所有框
        label = child.find('name')
        label_index = labels.index(label.text) # 获取类别名称的ID
        sub = child.find('bndbox') # 找到框的标注值并进行读取
        xmin = sub[0].text
        ymin = sub[1].text
        xmax = sub[2].text
        ymax = sub[3].text
        boxes.append(','.join([xmin, ymin, xmax, ymax, str(label_index)]))
    # 将数据写入data.txt文件
    with open('./capchars/data.txt', 'a+') as f:
        f.write(' '.join(boxes) + '\n')
```

写好的数据是这样的：

```text
F:\...\capchars\images\1.png 1,9,9,24,24 19,14,29,28,29 38,11,50,26,26 58,7,73,22,17
F:\...\images\10.png 1,8,15,23,7 18,11,29,26,26 39,15,49,29,30 58,14,73,27,17
F:\...\images\100.png 1,6,10,19,26 18,11,29,26,25 38,10,59,25,20 60,9,73,24,6
F:\...\images\101.png 1,8,14,24,21 18,8,33,23,1 38,13,55,28,9 57,12,69,26,8
F:\...\images\102.png 1,12,18,28,11 18,9,34,24,19 38,5,49,20,29 59,10,74,29,14
F:\...\images\103.png 1,10,18,25,20 18,5,29,19,30 38,7,54,22,12 59,7,74,25,14
F:\...\images\104.png 1,10,12,24,18 17,8,32,22,5 38,10,54,25,18 58,14,74,28,9
F:\...\images\105.png 1,13,9,27,8 18,9,34,24,22 37,12,50,27,8 58,11,74,29,14
F:\...\images\106.png 1,14,13,29,12 18,8,34,22,18 39,6,55,24,14 59,13,74,27,6
F:\...\images\107.png 1,8,13,22,2 17,9,32,24,4 38,8,53,23,4 58,11,73,26,11
```

到这里，用于`YoloV3`训练用的数据集就算是建好了。

### 模型训练

#### 修改模型参数配置

打开源代码根目录的`train.py`，需要把主函数`_main`的前几行更改成我们对应的文件。这里要注意，由于要解决的是验证码检测的问题，并不是十分复杂，所以选择使用`Yolo`的`tiny`版本，同时模型的输入尺寸为`(416,416)`。下面是更改后的代码：

```python
annotation_path = 'data/capchars/data.txt'
log_dir = 'logs/'
classes_path = 'model_data/cap_classes.txt' # 与前面的predefined_classes.txt文件内容一样
anchors_path = 'model_data/tiny_yolo_anchors.txt'
```

`YoloV3`默认的输入图像通道数为`3`，考虑到要解决的问题的难度，但通道足矣，为了简化模型，把`train.py`的`create_model`方法和`create_tiny_model`方法中的第二行代码都修改为：

```python
image_input = Input(shape=(None, None, 1))
```

#### 修改训练数据读取方式

查看源代码中读取数据的部分，发现`yolo3/utils.py`中的`get_random_data`方法在读取数据的同时做了一些数据增强的操作。但在这个问题中是不太需要这些操作的，所以选择删除这些代码。

【本文来自微信公众号Titus的小宇宙，ID为TitusCosmos，转载请注明！】

【为了防止网上各种爬虫一通乱爬还故意删除原作者信息，故在文章中间加入作者信息，还望各位读者理解】

另外，前面说到输入图像的尺寸应该是`(416,416)`，而验证码图片的尺寸明显不一样，因此就要做一些更改尺寸的操作。更改之后的`get_random_data`方法是这样的：

```python
from PIL import Image
import numpy as np

def get_random_data(annotation_line, input_shape, max_boxes=4):
    line = annotation_line.split()
    image = Image.open(line[0])
    iw, ih = image.size
    h, w = input_shape # (416,416)
    boxes = np.array([np.array(list(map(int,box.split(',')))) for box in line[1:]])
    image_resize = image.resize((w, h), Image.BICUBIC)
    box_data = np.zeros((max_boxes,5))
    np.random.shuffle(boxes)
    x_scale, y_scale = float(w / iw), float(h / ih) # 计算验证码图片在横纵方向上缩放的倍数
    for index, box in enumerate(boxes):
        box[0] = int(box[0] * x_scale)
        box[1] = int(box[1] * y_scale)
        box[2] = int(box[2] * x_scale)
        box[3] = int(box[3] * y_scale)
        box_data[index, :] = box
    image_data = np.expand_dims(image_resize, axis=-1)
    image_data = np.array(image_data)/255.
    return image_data, box_data
```

#### 模型训练

一切准备工作就绪，就可以运行`train.py`开始训练了，训练开始后控制台会输出如下信息：

```text
...

Epoch 2/100

 1/16 [>.............................] - ETA: 6s - loss: 511.1613
 2/16 [==>...........................] - ETA: 6s - loss: 489.3632
 3/16 [====>.........................] - ETA: 5s - loss: 474.8986
 4/16 [======>.......................] - ETA: 5s - loss: 458.0243
 5/16 [========>.....................] - ETA: 4s - loss: 443.5792
 6/16 [==========>...................] - ETA: 4s - loss: 430.4511
 7/16 [============>.................] - ETA: 4s - loss: 416.0158
 8/16 [==============>...............] - ETA: 3s - loss: 402.7111
 9/16 [===============>..............] - ETA: 3s - loss: 390.4001
10/16 [=================>............] - ETA: 2s - loss: 378.4502
11/16 [===================>..........] - ETA: 2s - loss: 368.6907
12/16 [=====================>........] - ETA: 1s - loss: 359.1886
13/16 [=======================>......] - ETA: 1s - loss: 350.0055
14/16 [=========================>....] - ETA: 0s - loss: 342.0475
15/16 [===========================>..] - ETA: 0s - loss: 333.6687
16/16 [==============================] - 8s 482ms/step - loss: 325.5808 - val_loss: 211.4188

...
```

源代码中默认是先用预训练模型训练`50`轮，此时只解冻最后两层；然后解冻所有层再训练50轮。我们观察`loss`和`val_loss`不再下降时，模型就训练的差不多了，当然就直接等待程序运行结束一般也是可以的。

程序运行结束会在`logs`文件夹下自动生成一个`trained_weights_final.h5`文件，这就是我们需要的训练好的模型文件。

### 模型测试

模型训练完成，接下来当然就是激动人心的测试环节啦。

不过，心急吃不了热豆腐，我们还得先修改源代码中的部分测试代码才能开始对我们的模型进行测试。

打开根目录下的`yolo.py`，模型测试的时候会调用这个脚本生成一个`Yolo`类的对象，然后用这个对象来预测，所以需要在运行脚本之前先配置好。其实跟前面配置训练脚本差不多，修改后的代码如下：

```python
_defaults = {
    "model_path": 'logs/trained_weights_final.h5',
    "anchors_path": 'model_data/tiny_yolo_anchors.txt',
    "classes_path": 'model_data/cap_classes.txt',
    ...
}
```

这时就可以开始运行测试模型的脚本`yolo_video.py`来开始预测了，这时程序需要输入要预测的图片路径。我们输入一个没有训练过的验证码图片：

```text
Input image filename:data/capchars/images/416.png
```

很快，结果就出来了：

![预测结果](https://user-gold-cdn.xitu.io/2020/6/18/172c7eb0eb53beda?w=417&h=417&f=png&s=46040)

很明显，结果是`LFG8`，与实际情况一致。

再测试几个：

![预测结果](https://user-gold-cdn.xitu.io/2020/6/18/172c7ef669020052?w=416&h=417&f=png&s=45724)

![预测结果](https://user-gold-cdn.xitu.io/2020/6/18/172c7f0aa52f5692?w=417&h=417&f=png&s=47413)

### 总结

这个方法不需要对验证码图片作不稳定的切割，避免了在切割过程中导致的错误。因此，这个验证码的识别方法在成功率上是要高于之前的方法的。当然，这个方法还有可以优化的地方。比如训练前先根据系列前几篇文章的内容把验证码图片中的干扰线去掉，这样准确率肯定会更高。

至此，`YoloV3`识别验证码就讲完了。

本系列的所有源代码都会放在下面的github仓库里面，有需要可以参考，有问题欢迎指正，欢迎交流，谢谢！

```html
https://github.com/TitusWongCN/WeChatSubscriptionArticles
```

---

【Python盘纪念币系列】往期推荐：

[第一期：Python盘纪念币系列之一：简介](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=2247483772&idx=1&sn=d578c80bbb0216c5bf528a8cc4a3a89a&chksm=ea4bdabcdd3c53aa46796d7b96a5292361223b1f96a1a0579f9bd2c3a80886a27ca4d57a6d68&scene=21#wechat_redirect)

[第二期：Python盘纪念币系列之二：识别验证码 01](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=2247483781&idx=1&sn=0bff3d3410b55f25a5528cfcd9454a41&chksm=ea4bda45dd3c5353ba6b6cc67ebe84cebabc06b53a39391e2d49be45a6e5b763ab4bd60b3979&scene=21#wechat_redirect)

[第三期：Python盘纪念币系列之二：识别验证码 02](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000138&idx=1&sn=442469c6418af28deedd24dbf4fa033b&chksm=6a4bda4a5d3c535ca5e7d46fdf4c837eabba8691fad6a881c56781e037a530952a6fd42e92c7#rd)

[第四期：Python盘纪念币系列之二：识别验证码 03](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000144&idx=1&sn=4541cf9fb5dfdf0df5b69193845ebb9a&chksm=6a4bda505d3c5346ae5fee707c6a6221d66b3ecd8f8ea70e31793140d83499925d3cfe3c2542#rd)

[第五期：Python盘纪念币系列之二：识别验证码 04](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000149&idx=1&sn=395d1ff104dfe1a2d5791e308ed81008&chksm=6a4bda555d3c53431f3632f976af24dc768b4be46ae73f3d67397ad7763f56aaf81b9ec52ddf#rd)

[第六期：Python盘纪念币系列之三：自动预约脚本编写 01](https://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000160&idx=1&sn=8a378d166a717a7844152f02813314e4&chksm=6a4bda605d3c5376936307ff2dea68be3d20e2dc6ecb57d4fc5fee75fde21bd1bf47b28fc81d#rd)

[第七期：Python盘纪念币系列之三：自动预约脚本编写 02](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000160&idx=1&sn=8a378d166a717a7844152f02813314e4&chksm=6a4bda605d3c5376936307ff2dea68be3d20e2dc6ecb57d4fc5fee75fde21bd1bf47b28fc81d#rd)

[第八期：Python盘纪念币系列之三：自动预约脚本编写 03 & 系列总结](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000166&idx=1&sn=4ac00276bdfecaa1a22e8a3c083e7d48&chksm=6a4bda665d3c537098af5aaed68f6a97e522ff69f4ba7f893d294e1fe400c15dea0d2aa3aa15#rd)


下面是我的公众号，有兴趣可以扫一下：

![](https://user-gold-cdn.xitu.io/2019/12/23/16f333d3a3578000?w=304&h=112&f=png&s=13830)

![](https://user-gold-cdn.xitu.io/2019/12/23/16f333c33bd9bbe4?w=258&h=258&f=png&s=37181)