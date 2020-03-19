
> 上一期里我们拿到1000张验证码图片，今天我们来谈谈怎么来使用这些图片。

### 读取图片

python有很多读取图片的库，比如OpenCV、PIL等，为了后期方便以及个人习惯，这里我们选择OpenCV.

以第一张图片1.jpg为例：
```python
import cv2

img = cv2.imread('1.jpg', 0)
cv2.imshow('img', img)
cv2.waitKey(0)
```
执行之后发现报错：
```python
# error: (-215:Assertion failed) size.width>0 && size.height>0 in function 'cv::imshow'
```
为了确定是哪里的问题，我换了一张图运行代码，结果还是报同样的错。在资源管理器里图片是可以正常预览的，这说明图片本身没有问题，那就是我们的代码有问题。于是我换用PIL包来处理，代码如下：
```python
from PIL import Image

img = Image.open('1.jpg')
print(img)
img.show()
```
执行代码之后，图片正常显示，同时，控制台输出如下信息：
```python
# <PIL.GifImagePlugin.GifImageFile image mode=P size=74x32 at 0x16E255480B8>
```
从字面意思上来看，这张图可能是GIF格式的，虽然他的扩展名是`.jpg`（其实`.jpg`也是上一节中我们自己设置的）。这就解释了为什么用OpenCV读图时会报错了，那是因为OpenCV不能直接读取GIF格式的图片，而是要像读视频文件一样一帧一帧的来处理。
```python
def get_gif_first_frame(gif_path):
    gif = cv2.VideoCapture(gif_path)
    _, frame = gif.read()
    gif.release()
    return frame
```
我们定义了一个函数，专门来获取验证码文件的第一帧。这里要解释一下为什么OpenCV这么麻烦我们不用PIL库，那是因为在读图之后我们要多次处理获取的图片，而在处理图片上，OpenCV的确很方便。

### 字符分割

读取图片之后，下一步我们自然就要把各个字符从原始图片中切割开成为独立的文件。

怎么分开呢？我脑中的第一个想法是这样的：

1. 图片转换为灰度图
```python
cap = get_gif_first_frame('1.jpg')
cap = cv2.cvtColor(cap, cv2.COLOR_BGR2GRAY)
```

![](https://user-gold-cdn.xitu.io/2019/12/10/16eefca709de3661?w=122&h=66&f=png&s=2060)

2. 图片中有多条颜色较浅的干扰线，而字符的颜色都非常亮，故考虑将图片中像素值小于某个数的像素像素值全部置零，有效降低干扰
```python
_, thresh = cv2.threshold(cap, 150, 255, cv2.THRESH_BINARY)
```

![](https://user-gold-cdn.xitu.io/2019/12/10/16eefcbdcf53ad58?w=121&h=64&f=png&s=1397)

3. 去掉干扰后，就剩下相对独立的字符了。但因为上一步去除干扰线的时候可能导致字符被切断，这里进行一下膨胀处理

```python
dilate = cv2.dilate(thresh, (7,7), iterations=5)
```

![](https://user-gold-cdn.xitu.io/2019/12/10/16eefcfe6833347a?w=122&h=66&f=png&s=1358)

4. 膨胀之后就可以搜索图中所有的轮廓了，理想情况下，图中有四个轮廓分别对应四个字符

```python
dilate = cv2.dilate(thresh, (7,7), iterations=5)
contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
```

5. 根据轮廓获取最小外接矩形，作为切割的根据，将每个字符切割出来
```python
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    area = w * h
    target = cap[y - 1 if y - 1 > 0 else 0:y + h, x - 1 if x - 1 > 0 else 0:x + w]
```

可是想象很丰满，现实很骨感。下面是这种方式生成的图块，有些字符能切准，但有些就没那么幸运了。

![](https://user-gold-cdn.xitu.io/2019/12/10/16eefd09307df790?w=121&h=48&f=png&s=1118)


![](https://user-gold-cdn.xitu.io/2019/12/10/16eefd0e9230e092?w=121&h=48&f=png&s=1141)


![](https://user-gold-cdn.xitu.io/2019/12/10/16eefd14aad51817?w=121&h=47&f=png&s=1165)

最后证明此路不通，那有没有其他的方法呢？

### 后记

我也是一步一步从头开始边做这个项目边写文章，所以正好能把项目中遇到的问题都暴露出来，这样有助于融会贯通。上面的这个问题，大家有没有什么好的解决方法呢？欢迎在留言中提出~

本系列的所有源代码都会放在我的[github](https://github.com/TitusWongCN/AutoTokenAppointment)仓库里面，有需要可以参考，有问题欢迎指正，谢谢！


> 下期预告：切割字符的另一种方法





