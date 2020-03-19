> 由于今年的疫情，已经太久没有更新文章，作为湖北人，深知不给大家带来麻烦的同时还要提升自己。奈何没有带电脑回家，家中电脑又是个老爷机，经过长达几天的折腾终于可以使用。第一时间带来【`Python`自动戴圣诞帽】系列的第二篇文章，另外，文末有抗疫彩蛋，别忘了翻过去看一看哦。

> 注：本文部分图片来自百度百科，如有侵权请联系删除。

### OpenCV人脸关键点检测

前面说到家中电脑的原因，实在是安装不上`face_recognition`库，于是临时更换为`OpenCV`中的`LBF`算法方式。方法其实没有什么不同，都是通过检测出人脸关键点，然后定位圣诞帽的位置。

上一篇文章详细讲了`face_recognition`方式获取人脸关键点，这里就不详细描述了，具体通过看代码和注释了解。代码中的`haarcascade_frontalface_alt2.xml`和`lbfmodel.yaml`可以自行搜索得到，或者在公众号后台回复`OpenCVFace`获取下载地址。

```python
# load image:
image = cv2.imread(image_path, 0)
# find faces:
cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')
faces = cascade.detectMultiScale(image, 1.3, 5)
# create landmark detector and load lbf model:
facemark = cv2.face.createFacemarkLBF()
facemark.loadModel('lbfmodel.yaml')
# ok代表是否检测出关键点, landmarks表示所有的关键坐标
ok, landmarks = facemark.fit(image, faces)
```

与`face_recognition`不同的是，这种方式生成的关键点并不是按照器官分组的字典，而是一个列表文件。下面是列表中各个点所属器官的关系表：

```log
landmarks---[0, 16]----Chin
landmarks---[17, 21]---Left eyebrow
landmarks---[22, 26]---Right eyebrow
landmarks---[27, 30]---Nose bridge
landmarks---[30, 35]---Lower nose
landmarks---[36, 41]---Left eye
landmarks---[42, 47]---Right Eye
landmarks---[48, 59]---Outer lip
landmarks---[60, 67]---Inner lip
```

用OpenCV将关键点显示出来：

```python
points_face = copy.deepcopy(image)
for each in landmarks[0][0]:
    points_face = cv2.circle(points_face, tuple(each), 3, (0, 0, 255), -1)
# Display the resulting image
cv2.imshow('points_face', points_face)
cv2.waitKey(0)
```

效果如下：

![](https://user-gold-cdn.xitu.io/2020/2/5/170159205d5c4806?w=420&h=366&f=png&s=353350)

与`face_recognition`方式对比基本没有什么区别：

![](https://user-gold-cdn.xitu.io/2020/2/5/17015935cd30d1d4?w=406&h=359&f=png&s=284293)

### 戴圣诞帽前的准备

#### 合适的圣诞帽

首先需要找到一张合适的圣诞帽图片，一定要是带透明信息的`.png`格式的。

我找到的圣诞帽如下，还是比较漂亮的：

![](https://user-gold-cdn.xitu.io/2020/2/5/170159ec9a2e5ad9?w=246&h=159&f=png&s=32397)

根据常识，头的部分只是下图中蓝色框框住的地方，所以我们需要提前确定该部分的大小。

![](https://user-gold-cdn.xitu.io/2020/2/5/17015a2c6a3ce9a0?w=246&h=159&f=png&s=29606)

用windows自带的画图简单测量之后知道帽檐的部分宽为`175px`，同时帽檐离图片底部的距离为`25px`.

#### 确定圣诞帽的位置

有了圣诞帽，又知道了脸上各个关键点的位置，如何确定圣诞帽究竟该放在哪里？

这时候就需要小学美术学到的“三庭五眼”的知识了：

![](https://user-gold-cdn.xitu.io/2020/2/5/17015978dc6139ff?w=437&h=429&f=png&s=301963)

从图中可以看出从鼻翼下缘到下巴尖的距离与从眉心到发际线的距离相等，而脸的宽度与两颊的距离相等。

正常戴帽子时，帽檐一般会在发际线处，可以根据这点推测圣诞帽的位置（不考虑帽子的各种花式戴法）。仔细观察前文人脸关键点的图片示例会发现，鼻梁最上面的关键点与眉心位置很接近，可以根据这些信息确定圣诞帽在`Y`轴方向的位置。

检测人脸关键点时会得到两侧脸颊的具体坐标，根据脸颊第一个点的坐标和最后一个点的坐标即可计算出人脸的实际宽度。根据比例可以推算出圣诞帽在`X`轴方向的位置。

下面来进行细节的实现。

### 代码实现

首先圣诞帽要进行预处理：

```python
# 圣诞帽相关参数
hat_img = Image.open("./hat.png")
hat_brim_length = 175.0
hat_height_buffer = 25.0
hat_img = hat_img.convert('RGBA')
```

最后一句代码是将图片转换为`RGB`和透明度形式，便于后面直接用于掩膜，这也是需要`.png`格式图片的原因。

获取人脸关键点的方法已经介绍过，不再赘述。根据前面的分析，实现目标只需要目标人脸的脸颊关键点和鼻梁关键点，所以取出这些数据：

```python
chin = landmarks[0][0][:17]
nose_bridge = landmarks[0][0][27:31]
```

根据脸颊关键点计算实际脸宽，以及眉心到发际线距离：

```python
def get_distance(point1, point2):
    return int(math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2))

face_width = get_distance(chin[0], chin[-1])
hair_brim = get_distance(nose_bridge[-1], chin[int(len(chin)/2)])
```

这里是通过计算两颊端点之间距离的方式确定实际脸宽的，简便的方式的话，其实直接使用两点的横轴左边相减也能得到大致结果。

下面根据脸宽来调整圣诞帽的大小：

```python
resize_ratio = face_width / hat_brim_length
hat_width = int(hat_img.width * resize_ratio)
hat_height = int(hat_img.height * resize_ratio)
hat_buffer = int(hat_height_buffer * resize_ratio)
```

圣诞帽的帽檐应该是在发际线的位置，于是整张圣诞帽图片的底部坐标应该是鼻梁顶部纵坐标减去“一庭”的位置：

```python
hat_bottom = int(nose_bridge[0][1]) - hair_brim
```

同理，下面是圣诞帽图片的顶部、左侧和右侧坐标：

```python
hat_top = hat_bottom - hat_height
hat_left = int(chin[0][0])
hat_right = hat_left + hat_width
```

接下来是最后一步，把缩放过的圣诞帽通过前面的掩膜贴到原始图片上，然后显示出来：

```python
hat_region = hat_img
human_region = (hat_left, hat_top + hat_buffer, hat_right, hat_bottom + hat_buffer)
human_img.paste(hat_region, human_region, mask=hat_img)
human_img.show()
```

效果如下：

![](https://user-gold-cdn.xitu.io/2020/2/5/17015ca6b95cea03?w=407&h=329&f=png&s=345745)

![](https://user-gold-cdn.xitu.io/2020/2/5/17015cb396f2990b?w=344&h=273&f=png&s=219113)

> 注：这种方式没有在女主的图片中检测出人脸，所以没有放上结果。

观察下来，整体效果还行，但感觉被范闲瞪着不是很舒服。细节有点粗糙，对脸部状态有一定要求，脸部最好是处于正脸的位置。有兴趣的同学可以对脸部稍微倾斜的情况做一些优化。

### 彩蛋

此次疫情极大的影响了大家的生活，以后生活中一定要注意饮食健康。希望此次疫情早日结束，武汉加油，湖北加油，中国加油！

大家出门一定要戴好口罩，保护自己，也保护他人。特意为大家准备了口罩一枚：

![](https://user-gold-cdn.xitu.io/2020/2/5/17015d2f5a89d8ba?w=372&h=330&f=png&s=94943)

先帮范闲戴上：

![](https://user-gold-cdn.xitu.io/2020/2/5/17015d4b9f974ccd?w=402&h=326&f=png&s=334365)

最后，恭祝大家新的一年里少病少灾，实现心中所愿。

### 结语

这个系列就到此为止了，如果有想要了解交流的可以在公众号主页联系我，这个系列的代码在这里：

```html
https://github.com/TitusWongCN/WeChatSubscriptionArticles/tree/master/WearChristmasHat
```

大家有什么想了解的，或者有什么想做的也可以在文章后面留言，后面说不定就会做了哦~

### 后记

不管写什么，希望能跟更多人沟通，有问题或者需求随时欢迎交流。

我所有的项目源码都会放在下面的github仓库里面，有需要可以参考，有问题欢迎指正，谢谢！

```html
https://github.com/TitusWongCN/
```

<hr>

【Python自动戴圣诞帽】往期推荐：

第一期：[【Python自动戴圣诞帽】01 熟悉face_recognition库](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000211&idx=1&sn=e204a1f50238b7402601643ae192b7f0&chksm=6a4bda135d3c53054ca79d96a61e6ba2d83d67687a42cbe16db62b0a4601897b66abe8aec2da#rd)

下面是我的公众号，有兴趣可以扫一下：

![](https://user-gold-cdn.xitu.io/2020/2/5/17015da2c3bec53a?w=304&h=112&f=png&s=43506)

![](https://user-gold-cdn.xitu.io/2020/2/5/17015da4776ef2f4?w=258&h=258&f=png&s=23703)
